#!/usr/bin/env python3
"""Descarga el texto completo de un artículo de acceso abierto y lo deja con marcas de página.

Uso:
  obtener_texto.py <DOI> --out <carpeta> [--pdf archivo.pdf]

- Busca el PDF en OpenAlex (best_oa_location y demás ubicaciones abiertas).
- Si el usuario ya tiene el PDF (p. ej. descargado con su acceso institucional), se pasa con --pdf.
- Extrae el texto con `pdftotext -layout` y escribe `texto.txt` con "=== Página N ===" antes de cada
  página, para que cada dato del informe pueda citarse con su página.
- También escribe `meta.json` con título, autores, revista, fecha de publicación y acceso abierto.

No automatiza ScienceDirect, Scopus ni el proxy de la universidad: solo URLs abiertas que OpenAlex declara.
"""
import argparse, json, os, re, subprocess, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (cordada-ai; informe de artículos)"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        return data if binary else data.decode("utf-8", "replace")


def openalex(doi):
    w = json.loads(get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi)))
    locs = [w.get("best_oa_location") or {}] + (w.get("oa_locations") or [])
    pdfs = []
    for l in locs:
        for k in ("pdf_url", "landing_page_url"):
            u = (l or {}).get(k)
            if u and u not in pdfs:
                pdfs.append(u)
    # Springer: OpenAlex a veces no declara el PDF abierto, pero la ruta directa funciona (06-nov-2026)
    if doi.lower().startswith("10.1007/"):
        u = "https://link.springer.com/content/pdf/" + doi + ".pdf"
        if u not in pdfs:
            pdfs.append(u)
    meta = {
        "doi": doi, "titulo": w.get("title"),
        "autores": [a["author"]["display_name"] for a in w.get("authorships", [])],
        "revista": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "fecha_publicacion": w.get("publication_date"),
        "acceso_abierto": (w.get("open_access") or {}).get("is_oa"),
        "urls_candidatas": pdfs,
    }
    return meta


def es_pdf(data):
    return data[:5] == b"%PDF-"


def descargar_pdf(urls, dest):
    for u in urls:
        try:
            data = get(u, binary=True)
        except Exception as e:
            print(f"  · {u}: {e}", file=sys.stderr)
            continue
        if es_pdf(data):
            open(dest, "wb").write(data)
            return u
        # página HTML: buscar un enlace directo al PDF (citation_pdf_url es estándar en editoriales)
        m = re.search(rb'citation_pdf_url"\s+content="([^"]+)"', data)
        if m:
            u2 = urllib.parse.urljoin(u, m.group(1).decode())
            try:
                d2 = get(u2, binary=True)
                if es_pdf(d2):
                    open(dest, "wb").write(d2)
                    return u2
            except Exception as e:
                print(f"  · {u2}: {e}", file=sys.stderr)
    return None


def extraer(pdf, txt):
    # UTF-8 explícito: en Windows la codificación por defecto (cp1252) rompe nombres en cirílico
    raw = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", pdf, "-"], capture_output=True,
                         encoding="utf-8", errors="replace").stdout
    pages = raw.split("\f")
    with open(txt, "w", encoding="utf-8") as f:
        for i, p in enumerate(pages, 1):
            if p.strip():
                f.write(f"\n=== Página {i} ===\n{p}")
    return len([p for p in pages if p.strip()])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doi")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pdf", help="PDF ya descargado por el usuario")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = openalex(a.doi)
    pdf = os.path.join(a.out, "articulo.pdf")
    if a.pdf:
        meta["fuente_pdf"] = "PDF entregado por el usuario"
        if os.path.abspath(a.pdf) != os.path.abspath(pdf):
            open(pdf, "wb").write(open(a.pdf, "rb").read())
    else:
        src = descargar_pdf(meta["urls_candidatas"], pdf)
        if not src:
            json.dump(meta, open(os.path.join(a.out, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            sys.exit("No se pudo obtener el PDF abierto. Pídele al usuario que lo descargue con su acceso institucional "
                     "y vuelve a correr con --pdf.")
        meta["fuente_pdf"] = src
    n = extraer(pdf, os.path.join(a.out, "texto.txt"))
    meta["paginas"] = n
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Listo: {n} páginas en {a.out}/texto.txt (fuente: {meta['fuente_pdf']})")


if __name__ == "__main__":
    main()
