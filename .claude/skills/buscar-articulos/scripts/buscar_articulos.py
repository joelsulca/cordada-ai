#!/usr/bin/env python3
"""
Ejecuta las cadenas de búsqueda de una revisión de literatura y prepara el cribado.

Fuentes de registros (una u otra, o ambas):
  - API oficial de Scopus (vista STANDARD) con la API key del usuario en
    ~/.config/elsevier/apikey o en la variable ELSEVIER_API_KEY.
  - CSV exportados a mano desde Scopus (--csv C1=archivo.csv) o archivos de
    Web of Science en texto delimitado por tabulaciones (--wos C1=savedrecs.txt).

Pasos:
  1. Ejecuta cada cadena y registra el número de resultados y la fecha.
  2. Une los resultados y elimina duplicados por DOI (o por título normalizado).
  3. Completa resúmenes: OpenAlex -> Semantic Scholar -> Crossref. Vista STANDARD
     de Scopus no trae resúmenes sin acceso institucional.
  4. Aplica los criterios automatizables (ver SKILL.md): año, tipo de documento,
     volumen asignado, revisiones por título, cuartil SJR e idioma.
  5. Puntúa la afinidad de cada candidato con las preguntas de investigación, si
     el JSON de cadenas trae "_preguntas" (o se pasa --preguntas).
  6. Escribe cadenas-resultados.md, prisma.md, candidatos.md (con resúmenes para leer),
     excluidos.md y resultados.json en --out.

No decide la inclusión final: eso es lectura humana (y el cribado asistido que
describe SKILL.md).
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# El skill hermano verificar-referencias aporta la lectura del CSV de SCImago.
VERIF = os.path.abspath(os.path.join(HERE, "..", "..", "verificar-referencias", "scripts"))
sys.path.insert(0, VERIF)
try:
    from verificar_referencias import find_sjr_csv, load_sjr, norm_issn  # noqa: E402
except Exception:  # el skill hermano no está: seguir sin cuartiles
    find_sjr_csv = lambda explicit=None: explicit  # noqa: E731
    load_sjr = lambda path: {}  # noqa: E731
    norm_issn = lambda s: re.sub(r"[^0-9Xx]", "", s or "").upper()  # noqa: E731

UA = "cordada-ai-buscar-articulos/1.0 (+https://github.com/joelsulca/cordada-ai)"
MAILTO = os.environ.get("OPENALEX_MAILTO", "")
SCOPUS_URL = "https://api.elsevier.com/content/search/scopus"
MAX_POR_CADENA = 2000

# Revisiones: en el TÍTULO se excluyen automáticamente (CE1); en el resumen solo se marcan.
REVIEW_TITLE = re.compile(
    r"\b(review|survey|systematic literature|meta-analys\w*|bibliometric|"
    r"state[- ]of[- ]the[- ]art|scoping|literature analysis|revisi[oó]n)\b", re.I)
REVIEW_ABS = re.compile(
    r"\b(systematic (literature )?review|we review|this review|literature review|"
    r"survey of|bibliometric|meta-analys\w*|scoping review|PRISMA)\b", re.I)

# Afinidad con las preguntas de investigación: {"P1": ("categoría", [palabras clave]), ...}.
# Se carga de "_preguntas" en el JSON de cadenas o de --preguntas. Se puntúa sobre título + resumen.
# Es una ayuda para ordenar la lectura, no un criterio de inclusión.
PREGUNTAS = {}

# Idiomas aceptados (--idiomas); un registro sin idioma conocido no se excluye.
IDIOMAS_OK = {"en", "es", None, ""}
# Cuartiles: sin cuartil en SCImago se excluye (CE4); los no preferidos solo se marcan.
PREFERIDOS = {"Q1", "Q2"}


# ---------------------------------------------------------------- utilidades
def http_json(url, headers=None, data=None, retries=3, backoff=4.0):
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=h, data=data)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < retries:
                time.sleep(backoff * (i + 1))
                continue
            body = e.read()[:300].decode(errors="ignore")
            raise RuntimeError(f"HTTP {e.code}: {body}") from None
        except urllib.error.URLError:
            if i == retries:
                raise
            time.sleep(backoff)


def clean_doi(d):
    d = (d or "").strip().rstrip(".,;)]")
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.I).lower()


def norm_title(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def read_key():
    k = os.environ.get("ELSEVIER_API_KEY")
    p = os.path.expanduser("~/.config/elsevier/apikey")
    if not k and os.path.exists(p):
        k = open(p).read().strip()
    return k or None


def con_filtros(query, anios):
    """Agrega los filtros de año, tipo de documento y tipo de fuente si la cadena no los trae ya."""
    y = dt.date.today().year
    extra = []
    if "PUBYEAR" not in query.upper():
        extra.append(f"PUBYEAR > {y - anios} AND PUBYEAR < {y + 1}")
    if "DOCTYPE" not in query.upper():
        extra.append("DOCTYPE(ar)")
    if "SRCTYPE" not in query.upper():
        extra.append("SRCTYPE(j)")
    return query if not extra else f"{query} AND " + " AND ".join(extra)


# ---------------------------------------------------------------- fuentes
def scopus_api(cid, query, key):
    recs, start, total = [], 0, None
    while True:
        url = SCOPUS_URL + "?" + urllib.parse.urlencode(
            {"query": query, "count": 25, "start": start, "view": "STANDARD"})
        d, h = http_json(url, headers={"X-ELS-APIKey": key})
        sr = d["search-results"]
        total = int(sr.get("opensearch:totalResults", 0))
        for e in sr.get("entry", []):
            if "error" in e:
                continue
            aff = e.get("affiliation") or []
            recs.append({
                "fuente": "Scopus API", "cadenas": [cid],
                "titulo": e.get("dc:title", ""),
                "primer_autor": e.get("dc:creator", ""),
                "anio": int((e.get("prism:coverDate") or "0")[:4] or 0),
                "revista": e.get("prism:publicationName", ""),
                "issn": [x for x in (e.get("prism:issn"), e.get("prism:eIssn")) if x],
                "volumen": e.get("prism:volume") or "",
                "doi": clean_doi(e.get("prism:doi")),
                "tipo": e.get("subtypeDescription", ""),
                "tipo_fuente": e.get("prism:aggregationType", ""),
                "pais": sorted({a.get("affiliation-country") for a in aff if a.get("affiliation-country")}),
                "eid": e.get("eid", ""),
                # Criterio "Relevante" de la diapositiva S5 (fase 2): tasa de citaciones y cuartil.
                "citas": int(e.get("citedby-count") or 0),
                "acceso_abierto": bool(e.get("openaccessFlag")),
                "resumen": "", "resumen_fuente": "", "idioma": "",
            })
        start += 25
        if start >= total or start >= MAX_POR_CADENA:
            break
        time.sleep(0.15)
    return total, recs, h.get("X-RateLimit-Remaining")


SCOPUS_CSV = {"titulo": "Title", "anio": "Year", "revista": "Source title", "doi": "DOI",
              "resumen": "Abstract", "tipo": "Document Type", "volumen": "Volume",
              "issn": "ISSN", "idioma": "Language of Original Document", "autores": "Authors",
              "etapa": "Publication Stage", "eid": "EID"}
WOS_TXT = {"titulo": "TI", "anio": "PY", "revista": "SO", "doi": "DI", "resumen": "AB",
           "tipo": "DT", "volumen": "VL", "issn": "SN", "eissn": "EI", "idioma": "LA",
           "autores": "AU", "eid": "UT"}


def leer_export(cid, path, mapa, fuente, delim):
    recs = []
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f, delimiter=delim):
            g = lambda k: (row.get(mapa.get(k, "")) or "").strip()  # noqa: E731
            if not g("titulo"):
                continue
            issn = [g("issn")] + ([g("eissn")] if "eissn" in mapa else [])
            etapa = g("etapa").lower() if "etapa" in mapa else ""
            recs.append({
                "fuente": fuente, "cadenas": [cid], "titulo": g("titulo"),
                "primer_autor": (g("autores").split(";")[0] if g("autores") else ""),
                "anio": int(g("anio") or 0) if g("anio").isdigit() else 0,
                "revista": g("revista"), "issn": [x for x in issn if x],
                "volumen": "" if "press" in etapa else g("volumen"),
                "doi": clean_doi(g("doi")), "tipo": g("tipo"), "tipo_fuente": "Journal",
                "pais": [], "eid": g("eid"), "resumen": g("resumen"),
                "resumen_fuente": fuente if g("resumen") else "",
                "idioma": {"english": "en", "spanish": "es"}.get(g("idioma").lower(), g("idioma").lower()),
            })
    return len(recs), recs


# ---------------------------------------------------------------- resúmenes
def _pagina_springer(doi):
    """Springer publica el resumen en la metaetiqueta dc.description de su página."""
    req = urllib.request.Request("https://link.springer.com/article/" + doi,
                                 headers={"User-Agent": "Mozilla/5.0 (" + UA + ")"})
    with urllib.request.urlopen(req, timeout=30) as r:
        t = r.read().decode("utf-8", "ignore")
    m = re.search(r'<meta name="dc.description" content="([^"]+)"', t)
    return html.unescape(m.group(1)).strip() if m else ""


def completar_resumenes(recs, cache_path):
    """Busca resúmenes en cascada y guarda todo en caché para no repetir consultas.

    Orden: OpenAlex (lotes; da también idioma y tipo) -> Semantic Scholar (lotes;
    con SEMANTIC_SCHOLAR_API_KEY se evitan los 429) -> página de Springer (10.1007)
    -> Crossref (solo si faltan pocos). Elsevier (10.1016) no expone resúmenes sin
    acceso institucional: esos quedan marcados para leerlos en Scopus.
    """
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    dois = sorted({r["doi"] for r in recs if r["doi"] and not r["resumen"]})
    sin = lambda: [d for d in dois if not (cache.get(d) or {}).get("resumen")]  # noqa: E731

    # 1. OpenAlex: solo los DOIs nunca consultados
    # también se reconsultan entradas antiguas de la caché que no guardaron el año de OpenAlex
    nuevos = [d for d in dois if d not in cache or "oa_anio" not in cache[d]]
    for i in range(0, len(nuevos), 40):
        chunk = nuevos[i:i + 40]
        q = {"filter": "doi:" + "|".join(chunk), "per-page": 50,
             "select": "doi,abstract_inverted_index,language,type,publication_year"}
        if MAILTO:
            q["mailto"] = MAILTO
        try:
            d, _ = http_json("https://api.openalex.org/works?" + urllib.parse.urlencode(q))
        except Exception as e:
            print(f"  OpenAlex falló en un lote: {e}", file=sys.stderr)
            continue
        for x in chunk:
            cache.setdefault(x, {"resumen": "", "fuente": "", "idioma": "", "oa_tipo": ""})
            cache[x].setdefault("oa_anio", None)
        for w in d.get("results", []):
            doi = clean_doi(w.get("doi"))
            inv = w.get("abstract_inverted_index")
            ab = ""
            if inv:
                pos = {p: t for t, ps in inv.items() for p in ps}
                ab = " ".join(pos[k] for k in sorted(pos))
            prev = cache.get(doi) or {}
            cache[doi] = {"resumen": ab or prev.get("resumen", ""),
                          "fuente": "OpenAlex" if ab else prev.get("fuente", ""),
                          "idioma": w.get("language") or "", "oa_tipo": w.get("type") or "",
                          "oa_anio": w.get("publication_year")}
        time.sleep(0.2)

    # 2. Semantic Scholar: todos los que siguen sin resumen (también los de corridas previas)
    s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    faltan = sin()
    for i in range(0, len(faltan), 100):
        ids = ["DOI:" + d for d in faltan[i:i + 100]]
        hdr = {"Content-Type": "application/json"}
        if s2_key:
            hdr["x-api-key"] = s2_key
        try:
            res, _ = http_json("https://api.semanticscholar.org/graph/v1/paper/batch?fields=abstract",
                               headers=hdr, data=json.dumps({"ids": ids}).encode(),
                               retries=5, backoff=8.0)
        except Exception as e:
            print(f"  Semantic Scholar no respondió ({str(e)[:60]}); se reintenta en la próxima corrida.",
                  file=sys.stderr)
            res = []
        for did, r in zip(ids, res or []):
            if r and r.get("abstract"):
                cache.setdefault(did[4:], {"idioma": "", "oa_tipo": ""}).update(
                    {"resumen": r["abstract"], "fuente": "Semantic Scholar"})
        time.sleep(3)

    # 3. Springer: la página del artículo trae el resumen
    for d in [d for d in sin() if d.startswith("10.1007/")]:
        try:
            ab = _pagina_springer(d)
            if ab:
                cache.setdefault(d, {"idioma": "", "oa_tipo": ""}).update(
                    {"resumen": ab, "fuente": "Springer"})
        except Exception:
            pass
        time.sleep(0.5)

    # 4. Crossref: rara vez trae resúmenes en este dominio y va de uno en uno
    resto = [d for d in sin() if not d.startswith("10.1016/")]
    for d in (resto if len(resto) <= 100 else []):
        try:
            m, _ = http_json("https://api.crossref.org/works/" + urllib.parse.quote(d), retries=1)
            ab = re.sub(r"<[^>]+>", " ", (m.get("message") or {}).get("abstract") or "")
            ab = re.sub(r"\s+", " ", ab).strip()
            if ab:
                cache.setdefault(d, {"idioma": "", "oa_tipo": ""}).update(
                    {"resumen": ab, "fuente": "Crossref"})
        except Exception:
            pass
        time.sleep(0.1)

    json.dump(cache, open(cache_path, "w"), ensure_ascii=False)
    for r in recs:
        c = cache.get(r["doi"]) or {}
        if not r["resumen"] and c.get("resumen"):
            r["resumen"], r["resumen_fuente"] = c["resumen"], c["fuente"]
        if not r["idioma"]:
            r["idioma"] = c.get("idioma", "")
        r["oa_tipo"] = c.get("oa_tipo", "")
        r["oa_anio"] = c.get("oa_anio")


# ---------------------------------------------------------------- criterios
def evaluar(r, sjr_idx, anios):
    y = dt.date.today().year
    exc, marcas = [], []
    if r["anio"] and r["anio"] < y - anios + 1 - 0:
        exc.append(f"CI2: publicado en {r['anio']} (fuera de {y - anios + 1}–{y})")
    if r["tipo"] and not re.search(r"article|art[ií]culo", r["tipo"], re.I):
        exc.append(f"CE2: tipo '{r['tipo']}'")
    if r["tipo_fuente"] and r["tipo_fuente"].lower() not in ("journal",):
        exc.append(f"CE2: fuente '{r['tipo_fuente']}'")
    if not r["volumen"]:
        exc.append("CE3: sin volumen asignado (posible en prensa)")
    # Scopus fecha por el número de la revista; la primera publicación (en línea) puede ser anterior.
    # Para la antigüedad cuenta la primera publicación: se advierte, no se excluye, y se confirma
    # con el skill verificar-referencias.
    if r.get("oa_anio") and r["oa_anio"] < y - anios + 1 <= (r["anio"] or 0):
        marcas.append(f"publicado en línea en {r['oa_anio']} (Scopus lo fecha en {r['anio']}): "
                      "podría no cumplir la antigüedad del curso")
    if REVIEW_TITLE.search(r["titulo"]) or r.get("oa_tipo") == "review":
        exc.append("CE1: revisión o survey (título/tipo)")
    elif REVIEW_ABS.search(r["resumen"] or ""):
        marcas.append("posible revisión según el resumen: confirmar leyendo")
    q = None
    for s in r["issn"]:
        q = sjr_idx.get(norm_issn(s))
        if q:
            break
    r["cuartil"] = ((q or {}).get("quartile") or "").replace("-", "")
    r["sjr_categorias"] = (q or {}).get("categories") or ""
    if sjr_idx and not r["cuartil"]:
        exc.append("CE4: revista sin cuartil en el CSV de SCImago")
    elif r["cuartil"] and r["cuartil"] not in PREFERIDOS:
        marcas.append(f"{r['cuartil']}: no preferido, buscar alternativa en {'/'.join(sorted(PREFERIDOS))}")
    if (r["idioma"] or "").lower() not in IDIOMAS_OK:
        exc.append(f"CI4: idioma '{r['idioma']}'")
    if not r["resumen"]:
        marcas.append("SIN RESUMEN en fuentes abiertas: leerlo en Scopus (acceso institucional)")
    r["excluido_auto"], r["marcas"] = exc, marcas

    texto = (r["titulo"] + " " + (r["resumen"] or "")).lower()
    af = {}
    for p, (_, kws) in PREGUNTAS.items():
        n = sum(1 for k in kws if k.lower() in texto)
        if n:
            af[p] = n
    r["afinidad"] = af
    r["puntaje"] = sum(af.values()) + 2 * len(r["cadenas"]) - (1 if r["cuartil"] and r["cuartil"] not in PREFERIDOS else 0)


# ---------------------------------------------------------------- salida
def ref_corta(r):
    doi = f"https://doi.org/{r['doi']}" if r["doi"] else "(sin DOI)"
    return f"{r['primer_autor']} ({r['anio']}). *{r['revista']}*. {doi}"


def escribir(out, conteos, recs, dup, fecha, sjr_path):
    os.makedirs(out, exist_ok=True)
    json.dump({"fecha": fecha, "conteos": conteos, "registros": recs}, open(
        os.path.join(out, "resultados.json"), "w"), ensure_ascii=False, indent=1)

    t6 = ["# Resultados por cadena", "", f"Búsqueda ejecutada el {fecha}.", "",
          "| ID | Preguntas | Fuente | Resultados |", "|---|---|---|---|"]
    for c in conteos:
        t6.append(f"| {c['id']} | {c.get('preguntas', '')} | {c['fuente']} | {c['total']} |")
    open(os.path.join(out, "cadenas-resultados.md"), "w").write("\n".join(t6) + "\n")

    incl = [r for r in recs if not r["excluido_auto"]]
    exc = [r for r in recs if r["excluido_auto"]]
    motivos = {}
    for r in exc:
        k = r["excluido_auto"][0].split(":")[0]
        motivos[k] = motivos.get(k, 0) + 1
    identificados = sum(c["total"] for c in conteos)
    truncadas = [c["id"] for c in conteos if c["descargados"] < c["total"]]
    pr = ["# Números para el flujo PRISMA 2020 (etapa automática)", "", f"Fecha: {fecha}", "",
          "| Etapa | n |", "|---|---|",
          f"| Registros identificados (suma de cadenas) | {identificados} |",
          f"| Duplicados eliminados | {dup} |",
          f"| Registros únicos | {len(recs)} |",
          f"| Excluidos por criterios automáticos | {len(exc)} |"]
    for k, v in sorted(motivos.items()):
        pr.append(f"| &nbsp;&nbsp;— {k} | {v} |")
    pr += [f"| **Pasan al cribado por título y resumen** | **{len(incl)}** |", ""]
    if truncadas:
        pr += [f"**Atención:** {', '.join(truncadas)} superan {MAX_POR_CADENA} resultados y se descargaron "
               "solo los primeros. Una cadena tan amplia debe acotarse antes de seguir.", ""]
    pr += [
           "Las etapas siguientes (cribado por resumen, texto completo e inclusión final) se completan "
           "con la lectura: ver cribado.md.", "",
           f"Cuartiles: {os.path.basename(sjr_path) if sjr_path else 'sin CSV de SCImago'} (mejor cuartil por ISSN)."]
    open(os.path.join(out, "prisma.md"), "w").write("\n".join(pr) + "\n")

    incl.sort(key=lambda r: -r["puntaje"])
    ca = [f"# Candidatos para cribado ({len(incl)})", "",
          ("Ordenados por afinidad con las preguntas de investigación (ayuda de lectura, no criterio de inclusión)."
           if PREGUNTAS else "Sin preguntas configuradas: ordenados por número de cadenas que los recuperan."), ""]
    for i, r in enumerate(incl, 1):
        af = ", ".join(f"{p}×{n}" for p, n in sorted(r["afinidad"].items())) or "—"
        ca += [f"## {i}. {r['titulo']}", "",
               f"- **Ref.:** {ref_corta(r)} · vol. {r['volumen'] or '—'}",
               f"- **Cuartil SJR:** {r['cuartil'] or '—'} · **País:** {', '.join(r['pais']) or '—'} · "
               f"**Cadenas:** {', '.join(r['cadenas'])} · **Afinidad:** {af}",
               f"- **Citas (Scopus):** {r.get('citas', '—')} · **Acceso abierto:** "
               f"{ {True: 'sí', False: 'no'}.get(r.get('acceso_abierto'), '—') } · **DOI:** {r['doi'] or '—'}",
               ]
        if r["marcas"]:
            ca.append(f"- **Atención:** {'; '.join(r['marcas'])}")
        ca += ["", f"> {r['resumen'] or '(sin resumen disponible)'}",
               f"> — *resumen: {r['resumen_fuente'] or 'no encontrado'}*", ""]
    open(os.path.join(out, "candidatos.md"), "w").write("\n".join(ca) + "\n")
    # N.º de candidato -> DOI: el cribado se guarda por número y así se traslada entre corridas.
    json.dump([r["doi"] or "t:" + norm_title(r["titulo"]) for r in incl],
              open(os.path.join(out, ".orden_candidatos.json"), "w"), indent=0)

    ex = [f"# Excluidos automáticamente ({len(exc)})", "",
          "Revisar de un vistazo: un falso positivo (p. ej. 'review' en otro sentido) se puede rescatar.", "",
          "| # | Título | Año | Revista | Motivo |", "|---|---|---|---|---|"]
    for i, r in enumerate(exc, 1):
        ex.append(f"| {i} | {r['titulo'][:110]} | {r['anio']} | {r['revista'][:50]} | "
                  f"{'; '.join(r['excluido_auto'])} |")
    open(os.path.join(out, "excluidos.md"), "w").write("\n".join(ex) + "\n")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cadenas", help="JSON {id: {preguntas, query}} a ejecutar por la API de Scopus")
    ap.add_argument("--solo", nargs="*", help="ejecutar solo estos IDs de cadena (p. ej. C1 C3)")
    ap.add_argument("--csv", action="append", default=[], help="ID=export_scopus.csv (repetible)")
    ap.add_argument("--wos", action="append", default=[], help="ID=savedrecs.txt de WoS (repetible)")
    ap.add_argument("--out", required=True, help="carpeta de salida")
    ap.add_argument("--anios", type=int, default=4,
                    help="años hacia atrás incluyendo el actual (default 4: p. ej. 2023–2026 en 2026)")
    ap.add_argument("--sjr", help="CSV de SCImago (default: variable SJR_CSV, docs/referencia/ "
                                  "o perfil/referencia/ de la raíz del workspace)")
    ap.add_argument("--preguntas", help='JSON {"P1": {"categoria": "...", "palabras": [...]}} '
                                       '(default: la clave "_preguntas" del JSON de cadenas)')
    ap.add_argument("--idiomas", default="en,es", help="idiomas aceptados (default en,es)")
    ap.add_argument("--cuartiles-preferidos", default="Q1,Q2",
                    help="cuartiles preferidos; los demás se marcan (default Q1,Q2)")
    ap.add_argument("--sin-resumenes", action="store_true", help="no consultar fuentes de resúmenes")
    a = ap.parse_args()

    global IDIOMAS_OK, PREFERIDOS
    IDIOMAS_OK = {x.strip().lower() for x in a.idiomas.split(",") if x.strip()} | {None, ""}
    PREFERIDOS = {q.strip().upper() for q in a.cuartiles_preferidos.split(",") if q.strip()}
    preg = None
    if a.preguntas:
        preg = json.load(open(a.preguntas))
        preg = preg.get("_preguntas", preg)  # acepta el objeto directo o un JSON de cadenas
    elif a.cadenas:
        preg = json.load(open(a.cadenas)).get("_preguntas")
    for pid, v in (preg or {}).items():
        PREGUNTAS[pid] = (v.get("categoria", ""), v.get("palabras", []))

    fecha = dt.date.today().isoformat()
    conteos, todos = [], []

    if a.cadenas:
        key = read_key()
        if not key:
            sys.exit("No hay API key: guardarla en ~/.config/elsevier/apikey o ELSEVIER_API_KEY.")
        cad = json.load(open(a.cadenas))
        for cid, c in cad.items():
            if cid.startswith("_") or (a.solo and cid not in a.solo):
                continue
            q = con_filtros(c["query"], a.anios)
            print(f"Scopus {cid}…", file=sys.stderr)
            try:
                total, recs, rem = scopus_api(cid, q, key)
            except RuntimeError as e:
                sys.exit(f"La API de Scopus rechazó {cid}: {e}\n"
                         "Plan B: exportar el CSV desde Scopus (acceso institucional) y usar --csv.")
            conteos.append({"id": cid, "preguntas": c.get("preguntas", ""), "fuente": "Scopus",
                            "total": total, "descargados": len(recs), "query": q})
            todos += recs
            print(f"  {total} resultados (cuota restante: {rem})", file=sys.stderr)

    for spec, mapa, fuente, delim in [(s, SCOPUS_CSV, "Scopus CSV", ",") for s in a.csv] + \
                                      [(s, WOS_TXT, "WoS", "\t") for s in a.wos]:
        cid, path = spec.split("=", 1)
        n, recs = leer_export(cid, path, mapa, fuente, delim)
        conteos.append({"id": cid, "fuente": fuente.split()[0], "total": n, "descargados": n})
        todos += recs

    if not todos:
        sys.exit("No hay registros: pasar --cadenas o --csv/--wos.")

    # deduplicar: DOI, y si no hay DOI, título normalizado
    unicos, dup = {}, 0
    for r in todos:
        k = r["doi"] or "t:" + norm_title(r["titulo"])
        if k in unicos:
            dup += 1
            u = unicos[k]
            u["cadenas"] = sorted(set(u["cadenas"]) | set(r["cadenas"]))
            if not u["resumen"] and r["resumen"]:
                u["resumen"], u["resumen_fuente"] = r["resumen"], r["resumen_fuente"]
        else:
            unicos[k] = r
    recs = list(unicos.values())

    os.makedirs(a.out, exist_ok=True)
    if not a.sin_resumenes:
        print("Completando resúmenes…", file=sys.stderr)
        completar_resumenes(recs, os.path.join(a.out, ".cache_resumenes.json"))
    sjr_path = find_sjr_csv(a.sjr)
    sjr_idx = load_sjr(sjr_path)
    for r in recs:
        evaluar(r, sjr_idx, a.anios)
    escribir(a.out, conteos, recs, dup, fecha, sjr_path)

    con_ab = sum(1 for r in recs if r["resumen"])
    pasan = sum(1 for r in recs if not r["excluido_auto"])
    print(f"\nListo: {len(recs)} únicos ({dup} duplicados), {con_ab} con resumen, "
          f"{pasan} pasan a cribado. Salida en {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
