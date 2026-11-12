#!/usr/bin/env python3
"""
Verifica referencias bibliográficas contra los criterios de fuentes de un curso.

Por qué existe: los trabajos académicos piden fuentes con criterios estrictos
(antigüedad, tipo de documento, revista indexada, cuartil) y las búsquedas web y
los asistentes de IA devuelven citas inventadas con apariencia creíble. Este script
automatiza la parte comprobable (existencia por DOI, año, publicación en volumen,
tipo de documento, cuartil SJR) y deja marcada la parte que requiere criterio
humano (si es de aporte o revisión, si la revista es depredadora).

Fuentes que consulta:
  - Crossref (api.crossref.org): existencia, metadatos, tipo, año, volumen.
  - OpenAlex (api.openalex.org): tipo "review" y abstract (señal de revisión).
  - CSV de SCImago descargado a mano (scimagojr <año>.csv, ver --sjr):
    cuartil por ISSN, sin depender de la web (SCImago bloquea el acceso automático).

Uso:

    # DOIs sueltos
    python3 verificar_referencias.py 10.3390/app16104682 10.1371/journal.pone.0331715

    # Un archivo .md/.txt con la lista de referencias (extrae los DOIs y
    # compara año/volumen de la referencia escrita contra Crossref)
    python3 verificar_referencias.py --refs courses/<curso>/deliverables/referencias.md

    # Criterios del curso: artículos de 3 años o menos, Q1/Q2 de preferencia, Q3/Q4 aceptables
    python3 verificar_referencias.py --refs refs.md --anios 3 \
        --cuartiles-preferidos Q1,Q2 --cuartiles-aceptados Q1,Q2,Q3,Q4 --out reporte.md
"""

import argparse
import csv
import datetime as dt
import glob
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "cordada-ai-verificar-referencias/1.0 (+https://github.com/joelsulca/cordada-ai)"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)
REVIEW_WORDS = re.compile(
    r"\b(review|survey|systematic|meta-analys\w*|literature|state of the art|"
    r"bibliometric|overview|scoping|revisi[oó]n|estado del arte)\b", re.I)

HERE = os.path.dirname(os.path.abspath(__file__))

# Política de cuartiles: se fija con --cuartiles-preferidos y --cuartiles-aceptados (ver main).
PREFERIDOS = {"Q1", "Q2"}
ACEPTADOS = {"Q1", "Q2", "Q3", "Q4"}


# ---------------------------------------------------------------- utilidades
def http_json(url, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == retries:
                raise
        except Exception:
            if i == retries:
                raise
        time.sleep(1.5 * (i + 1))


def clean_doi(d):
    d = d.strip().rstrip(".,;)]")
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.I)
    return d


def norm_issn(s):
    return re.sub(r"[^0-9Xx]", "", s or "").upper()


def year_of(msg):
    for k in ("published-print", "published-online", "issued", "published"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            return dp[0][0]
    return None


# ---------------------------------------------------------------- SCImago
def raiz_workspace(desde=None):
    """Sube desde el directorio actual hasta encontrar AGENTS.md (la raíz del workspace)."""
    d = os.path.abspath(desde or os.getcwd())
    while True:
        if os.path.exists(os.path.join(d, "AGENTS.md")):
            return d
        padre = os.path.dirname(d)
        if padre == d:
            return None
        d = padre


def find_sjr_csv(explicit=None):
    """Busca el CSV de SCImago más reciente. Orden: --sjr, variable SJR_CSV,
    docs/referencia/ del directorio actual y perfil/referencia/ de la raíz del workspace."""
    if explicit:
        return explicit
    if os.environ.get("SJR_CSV"):
        return os.environ["SJR_CSV"]
    dirs = [os.path.join(os.getcwd(), "docs", "referencia"),
            os.path.join(os.getcwd(), "perfil", "referencia")]
    raiz = raiz_workspace()
    if raiz:
        dirs.append(os.path.join(raiz, "perfil", "referencia"))
    pats = []
    for d in dirs:
        pats += glob.glob(os.path.join(d, "scimagojr*.csv"))
    if not pats:
        return None

    def yr(p):
        m = re.search(r"(20\d\d)", os.path.basename(p))
        return int(m.group(1)) if m else 0
    return max(pats, key=yr)


def load_sjr(path):
    idx = {}
    if not path or not os.path.exists(path):
        return idx
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for row in csv.DictReader(f, delimiter=";"):
            for issn in (row.get("Issn") or "").split(","):
                n = norm_issn(issn)
                if n:
                    idx[n] = {
                        "title": row.get("Title"),
                        "quartile": row.get("SJR Best Quartile"),
                        "sjr": row.get("SJR"),
                        "categories": row.get("Categories"),
                        "sourceid": row.get("Sourceid"),
                        "type": row.get("Type"),
                        "publisher": row.get("Publisher"),
                    }
    return idx


# ---------------------------------------------------------------- verificación
def openalex_info(doi):
    try:
        w = http_json("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi))
    except Exception:
        return None
    if not w:
        return None
    abstract = ""
    inv = w.get("abstract_inverted_index")
    if inv:
        pos = {}
        for word, idxs in inv.items():
            for i in idxs:
                pos[i] = word
        abstract = " ".join(pos[i] for i in sorted(pos))
    oa = w.get("open_access") or {}
    return {"type": w.get("type"), "abstract": abstract,
            "retracted": w.get("is_retracted"), "language": w.get("language"),
            "publication_date": w.get("publication_date"),
            "is_oa": oa.get("is_oa"), "oa_status": oa.get("oa_status")}


def check(doi, ref_text, sjr_idx, min_year):
    r = {"doi": doi, "ref_text": ref_text, "checks": {}, "notes": []}
    try:
        data = http_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    except Exception as e:
        r["checks"]["existe"] = ("?", f"Crossref no respondió ({e}); reintentar")
        return r
    if not data:
        # Crossref solo cubre su agencia; arXiv, Zenodo, etc. registran en DataCite.
        try:
            h = http_json("https://doi.org/api/handles/" + urllib.parse.quote(doi))
        except Exception:
            h = None
        if not h or h.get("responseCode") != 1:
            r["checks"]["existe"] = ("NO", "El DOI no existe (ni en Crossref ni en doi.org): posible cita inventada")
            return r
        try:
            dc = http_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi))
            attrs = dc["data"]["attributes"]
            kind = (attrs.get("types") or {}).get("resourceTypeGeneral") or "?"
            r.update({"title": (attrs.get("titles") or [{}])[0].get("title", ""),
                      "year": attrs.get("publicationYear"), "publisher": attrs.get("publisher"),
                      "authors": ", ".join(c.get("familyName") or c.get("name", "")
                                           for c in (attrs.get("creators") or [])[:6])})
        except Exception:
            kind = "?"
        r["checks"]["existe"] = ("SÍ", f"registrado en DataCite, no en Crossref ({r.get('title','')})")
        r["checks"]["tipo"] = ("NO", f"DataCite/{kind}: normalmente preprint (arXiv), dataset o software, "
                                     "no artículo de revista. Buscar si tiene versión publicada en revista")
        return r
    m = data["message"]
    authors = m.get("author") or []
    r.update({
        "title": (m.get("title") or [""])[0],
        "journal": (m.get("container-title") or [""])[0],
        "authors": ", ".join(a.get("family", "") for a in authors[:6]) + (" et al." if len(authors) > 6 else ""),
        "year": year_of(m), "volume": m.get("volume"), "issue": m.get("issue"),
        "article": m.get("article-number") or m.get("page"),
        "type": m.get("type"), "issn": m.get("ISSN") or [],
        "publisher": m.get("publisher"),
    })
    r["checks"]["existe"] = ("SÍ", f"{r['authors']} ({r['year']}). {r['title']}. {r['journal']}")

    # tipo de documento
    t = r["type"]
    if t == "journal-article":
        r["checks"]["tipo"] = ("SÍ", "journal-article")
    elif t in ("proceedings-article", "posted-content", "book-chapter", "report", "dissertation"):
        why = {"proceedings-article": "congreso", "posted-content": "preprint"}.get(t, t)
        r["checks"]["tipo"] = ("NO", f"{t} ({why}); no es artículo de revista")
    else:
        r["checks"]["tipo"] = ("?", f"tipo Crossref = {t}")

    # antigüedad
    y = r["year"]
    if y is None:
        r["checks"]["antigüedad"] = ("?", "sin fecha en Crossref")
    elif y >= min_year:
        r["checks"]["antigüedad"] = ("SÍ", f"{y} (mínimo {min_year})")
    else:
        r["checks"]["antigüedad"] = ("NO", f"{y}: anterior al mínimo ({min_year})")

    # publicado en volumen (no in press)
    if t != "journal-article":
        r["checks"]["en volumen"] = ("—", "no aplica: no es artículo de revista")
    elif r["volume"] and (r["issue"] or r["article"]):
        r["checks"]["en volumen"] = ("SÍ", f"vol. {r['volume']}" + (f"({r['issue']})" if r["issue"] else "")
                                     + (f", {r['article']}" if r["article"] else ""))
    elif r["volume"]:
        r["checks"]["en volumen"] = ("?", f"vol. {r['volume']} sin número ni páginas")
    else:
        r["checks"]["en volumen"] = ("NO", "sin volumen: posible 'in press' u 'online first'")

    # cuartil SJR
    hit = None
    for issn in r["issn"]:
        hit = sjr_idx.get(norm_issn(issn))
        if hit:
            break
    if not sjr_idx:
        r["checks"]["cuartil"] = ("?", "no se encontró el CSV de SCImago")
    elif not hit:
        r["checks"]["cuartil"] = ("NO", f"ISSN {', '.join(r['issn']) or '—'} no figura en SJR: revista no indexada en Scopus (o ISSN distinto; revisar a mano)")
    else:
        q = hit["quartile"] or "-"
        # Política del curso: --cuartiles-preferidos cumplen; los demás aceptados, "ACEPT.".
        if q in PREFERIDOS:
            ok = "SÍ"
        elif q in ACEPTADOS:
            ok = "ACEPT."
        elif q in ("Q1", "Q2", "Q3", "Q4"):
            ok = "NO"
        else:
            ok = "?"
        why = {"ACEPT.": f" (aceptable; se prefiere {'/'.join(sorted(PREFERIDOS))})",
               "NO": " (fuera de los cuartiles aceptados)",
               "?": " (sin cuartil asignado en esta edición; revisar a mano)"}.get(ok, "")
        r["checks"]["cuartil"] = (ok, f"{q}{why} · SJR {hit['sjr']} · {hit['categories'][:140]}")
        r["sjr_sourceid"] = hit["sourceid"]

    # aporte vs revisión (señales; la decisión es humana)
    oa = openalex_info(doi)
    signals = []
    if REVIEW_WORDS.search(r["title"] or ""):
        signals.append("el título sugiere revisión/survey")
    if oa and oa.get("type") == "review":
        signals.append("OpenAlex lo clasifica como 'review'")
    if oa and oa.get("retracted"):
        r["checks"]["retractado"] = ("NO", "OpenAlex lo marca como retractado")
    if signals:
        r["checks"]["de aporte"] = ("?", "; ".join(signals) + ": leer el abstract")
    else:
        r["checks"]["de aporte"] = ("?*", "sin señales de revisión; confirmar leyendo el abstract")
    if oa:
        r["abstract"] = (oa.get("abstract") or "")[:700]
        r["language"] = oa.get("language")
        r["acceso_abierto"] = oa.get("is_oa")
        r["oa_status"] = oa.get("oa_status")
        # Crossref suele fechar por el número de la revista; la primera publicación en línea
        # puede ser uno o dos años anterior. Para la antigüedad cuenta la primera publicación.
        pd_ = oa.get("publication_date") or ""
        r["primera_publicacion"] = pd_
        if pd_[:4].isdigit() and int(pd_[:4]) < min_year and r["checks"].get("antigüedad", ("",))[0] == "SÍ":
            r["checks"]["antigüedad"] = ("?", f"Crossref {y}, pero OpenAlex lo fecha en línea el {pd_}: "
                                              "confirmar la fecha de primera publicación en la editorial")

    # coherencia con la referencia escrita
    if ref_text:
        mism = []
        ym = re.search(r"\((\d{4})[a-z]?\)", ref_text)
        if ym and y and int(ym.group(1)) != y:
            mism.append(f"año escrito {ym.group(1)} ≠ Crossref {y}")
        vm = re.search(r"\*?,\s*\*?(\d+)\*?\s*(\((\w+)\))?,", ref_text)
        if vm and r["volume"] and vm.group(1) != str(r["volume"]):
            mism.append(f"volumen escrito {vm.group(1)} ≠ Crossref {r['volume']}")
        if mism:
            r["checks"]["coincide con la cita"] = ("NO", "; ".join(mism))
        else:
            r["checks"]["coincide con la cita"] = ("SÍ", "año y volumen coinciden")
    return r


# ---------------------------------------------------------------- entrada / salida
def parse_refs(path):
    items, sin_doi = [], []
    text = open(path, encoding="utf-8").read()
    # Si el archivo tiene sección de referencias, limitarse a ella
    m = re.search(r"^#+\s*(referencias|references|bibliograf\w*)\s*$", text, re.I | re.M)
    if m:
        text = text[m.end():]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        dm = DOI_RE.search(line)
        if dm:
            items.append((clean_doi(dm.group(0)), line))
        elif re.search(r"\(\d{4}\)", line):
            sin_doi.append(line)
    return items, sin_doi


def render(results, sin_doi, sjr_path, min_year):
    out = [f"# Verificación de referencias",
           "",
           f"- Fecha: {dt.date.today().isoformat()} · artículos científicos desde {min_year} · "
           f"cuartil según `{os.path.basename(sjr_path) if sjr_path else 'sin CSV'}`",
           f"- Cuartiles preferidos: {', '.join(sorted(PREFERIDOS))} · aceptados: {', '.join(sorted(ACEPTADOS))}",
           "- Leyenda: SÍ = cumple · ACEPT. = aceptable, pero no preferido · NO = no cumple · ? = revisar a mano · ?* = sin señales, confirmar leyendo el abstract",
           ""]
    cols = ["existe", "tipo", "antigüedad", "en volumen", "cuartil", "de aporte", "coincide con la cita"]
    out.append("| Referencia | " + " | ".join(cols) + " |")
    out.append("|---|" + "---|" * len(cols))
    for r in results:
        name = f"{r.get('authors','').split(',')[0] or r['doi']} ({r.get('year','?')})"
        cells = [r["checks"].get(c, ("—", ""))[0] for c in cols]
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("")
    for r in results:
        out.append(f"## {r.get('authors') or r['doi']} ({r.get('year','?')})")
        out.append(f"- DOI: https://doi.org/{r['doi']}")
        if r.get("journal"):
            out.append(f"- Revista: *{r['journal']}* · {r.get('publisher','')} · ISSN {', '.join(r.get('issn', []))}")
        for k, (v, why) in r["checks"].items():
            out.append(f"- **{k}**: {v} — {why}")
        if r.get("primera_publicacion") or r.get("acceso_abierto") is not None:
            oa_txt = {True: f"sí ({r.get('oa_status')})", False: "no"}.get(r.get("acceso_abierto"), "—")
            out.append(f"- Primera publicación (OpenAlex): {r.get('primera_publicacion') or '—'} · "
                       f"Acceso abierto: {oa_txt}")
        if r.get("widget"):
            out.append(f"- Evidencia SCImago (widget oficial): `{r['widget']}`")
        elif r.get("widget_url"):
            out.append(f"- Evidencia SCImago: abrir {r['widget_url']} en el navegador y guardar la imagen")
        if r.get("language"):
            out.append(f"- Idioma (OpenAlex): {r['language']}" + "")
        if r.get("abstract"):
            out.append(f"- Abstract (inicio): {r['abstract']}…")
        out.append("")
    if sin_doi:
        out.append("## Referencias sin DOI (verificación manual)")
        out.append("Informes, tesis, libros o sitios web: aplicar el criterio de antigüedad del curso para estas fuentes; "
                   "verificar que la URL abre el documento citado y que los datos coinciden.")
        out += [f"- {s}" for s in sin_doi]
        out.append("")
    out.append("## Pendiente siempre manual")
    out.append("- **De aporte**: confirmar leyendo el abstract que no es revisión, survey ni resumen.")
    out.append("- **Revista depredadora**: revisar editorial y señales (ver SKILL.md).")
    return "\n".join(out)


def descargar_widgets(results, carpeta):
    """Intenta descargar el widget oficial de SCImago (journal_img.php): un PNG con el mejor cuartil
    y el SJR del año, útil como evidencia en informes de artículos.
    Desde el 30-sep-2026 SCImago responde 403 también a este recurso: en ese caso se deja la URL
    para que el usuario la abra en su navegador y guarde la imagen ("Guardar imagen como…")."""
    os.makedirs(carpeta, exist_ok=True)
    for r in results:
        sid = r.get("sjr_sourceid")
        if not sid:
            continue
        r["widget_url"] = f"https://www.scimagojr.com/journal_img.php?id={sid}"
        slug = re.sub(r"[^a-z0-9]+", "-", (r.get("journal") or sid).lower()).strip("-")[:60]
        dest = os.path.join(carpeta, f"scimago-{slug}.png")
        if not os.path.exists(dest):
            req = urllib.request.Request(r["widget_url"],
                                         headers={"User-Agent": "Mozilla/5.0"})
            try:
                data = urllib.request.urlopen(req, timeout=30).read()
            except Exception as e:
                print(f"AVISO: SCImago bloqueó la descarga del widget de {r.get('journal')} ({e}); "
                      "queda la URL en el reporte para guardarlo desde el navegador.", file=sys.stderr)
                continue
            if not data.startswith(b"\x89PNG"):
                print(f"AVISO: el widget de {r.get('journal')} no es un PNG; descargarlo a mano.", file=sys.stderr)
                continue
            open(dest, "wb").write(data)
            time.sleep(0.5)
        r["widget"] = dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dois", nargs="*", help="DOIs a verificar")
    ap.add_argument("--refs", help="archivo .md/.txt con la lista de referencias")
    ap.add_argument("--sjr", help="ruta al CSV de SCImago (por defecto: variable SJR_CSV, docs/referencia/ "
                                  "o perfil/referencia/ de la raíz del workspace)")
    ap.add_argument("--anios", type=int, default=5,
                    help="antigüedad máxima en años de los artículos científicos (default 5; usa la del curso)")
    ap.add_argument("--cuartiles-preferidos", default="Q1,Q2",
                    help="cuartiles que cumplen sin observación (default Q1,Q2)")
    ap.add_argument("--cuartiles-aceptados", default="Q1,Q2,Q3,Q4",
                    help="cuartiles aceptables; los demás no cumplen (default Q1,Q2,Q3,Q4)")
    ap.add_argument("--out", help="guardar el reporte en este .md")
    ap.add_argument("--json", help="guardar también los resultados crudos en JSON")
    ap.add_argument("--widgets", help="carpeta donde descargar el widget oficial de SCImago de cada revista "
                                      "(evidencia del cuartil para informes de artículos)")
    a = ap.parse_args()
    global PREFERIDOS, ACEPTADOS
    PREFERIDOS = {q.strip().upper() for q in a.cuartiles_preferidos.split(",") if q.strip()}
    ACEPTADOS = {q.strip().upper() for q in a.cuartiles_aceptados.split(",") if q.strip()} | PREFERIDOS

    items, sin_doi = [], []
    if a.refs:
        items, sin_doi = parse_refs(a.refs)
    items += [(clean_doi(d), "") for d in a.dois]
    seen, uniq = set(), []
    for d, t in items:
        if d.lower() not in seen:
            seen.add(d.lower())
            uniq.append((d, t))
    if not uniq and not sin_doi:
        sys.exit("No se encontraron DOIs. Pasa DOIs como argumentos o un archivo con --refs.")

    sjr_path = find_sjr_csv(a.sjr)
    sjr_idx = load_sjr(sjr_path)
    if not sjr_idx:
        print("AVISO: no se cargó el CSV de SCImago; el cuartil quedará como '?'.", file=sys.stderr)
    min_year = dt.date.today().year - a.anios

    results = []
    for d, t in uniq:
        print(f"· verificando {d} …", file=sys.stderr)
        results.append(check(d, t, sjr_idx, min_year))
        time.sleep(0.3)

    if a.widgets:
        descargar_widgets(results, a.widgets)
    report = render(results, sin_doi, sjr_path, min_year)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(report)
        print(f"Reporte guardado en {a.out}", file=sys.stderr)
    if a.json:
        json.dump(results, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(report)


if __name__ == "__main__":
    main()
