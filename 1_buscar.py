"""Paso 1 · Busca talleres en Google Maps (vía Outscraper) en todos los municipios de Osona.

Uso:  python 1_buscar.py            # todos los municipios (API, necesita crédito en Outscraper)
      python 1_buscar.py Vic Manlleu  # solo algunos
      python 1_buscar.py --importar fichero.csv|.xlsx   # GRATIS: exportación hecha desde la web de Outscraper
Coste orientativo Outscraper: ~3 $ por 1.000 resultados + enriquecimiento de emails.
"""
import re
import sys
import time

import requests

from comun import (CATEGORIAS_OK, CONSULTAS, MUNICIPIOS, ahora, cargar_config,
                   cargar_leads, guardar_leads, slugify)

API = "https://api.app.outscraper.com/maps/search-v3"
# Cadenas grandes: tienen web corporativa y no deciden en local
CADENAS = ("norauto", "midas", "feu vert", "euromaster", "speedy", "carglass", "first stop", "confortauto",
           "confort auto", "vulco", "aurgi", "rodi ", "point s", "driver center", "profesional plus")


def buscar(api_key, consulta):
    params = {
        "query": consulta,
        "limit": 60,
        "language": "en",          # en inglés el horario viene en un formato fácil de leer
        "region": "ES",
        "async": "false",
        "enrichment": "domains_service",  # añade emails encontrados en la web del negocio
    }
    for intento in range(3):
        r = requests.get(API, params=params, headers={"X-API-KEY": api_key}, timeout=300)
        if r.status_code == 200:
            data = r.json().get("data") or [[]]
            return data[0] if data and isinstance(data[0], list) else data
        print(f"   ! {r.status_code} {r.text[:150]} (reintento {intento + 1})")
        time.sleep(5)
    return []


def es_taller(p):
    cat = " ".join(str(p.get(k) or "") for k in ("category", "type", "subtypes")).lower()
    return any(c in cat for c in CATEGORIAS_OK)


def emails_de(p):
    out = []
    for k, v in p.items():
        if k.startswith("email") and isinstance(v, str) and "@" in v and v not in out:
            out.append(v.strip().lower())
    return out


def registrar(resultados, leads, muni):
    nuevos = 0
    munis = [m.lower() for m in MUNICIPIOS]
    for p in resultados:
        pid = p.get("place_id") or p.get("google_id")
        if not pid or pid in leads:
            continue
        if p.get("business_status") not in (None, "", "OPERATIONAL"):
            continue
        if not es_taller(p):
            continue
        ciudad = p.get("city") or muni or ""
        direccion = p.get("full_address") or p.get("address") or ""
        dl = direccion.lower()
        if ciudad.lower() not in munis and not any(re.search(r"(?<!\w)" + re.escape(m) + r"(?!\w)", dl) for m in munis):
            continue
        if any(c in (p.get("name") or "").lower() for c in CADENAS):
            continue
        emails = emails_de(p)
        try:
            rating = float(str(p.get("rating") or 0).replace(",", "."))
        except ValueError:
            rating = 0
        try:
            n = int(float(str(p.get("reviews") or 0).replace(",", ".")))
        except ValueError:
            n = 0
        horario = p.get("working_hours") or {}
        if not isinstance(horario, dict):
            horario = {}
        leads[pid] = {
            "id": pid,
            "slug": slugify(f"{p.get('name', '')}-{ciudad}"),
            "nombre": (p.get("name") or "").strip(),
            "municipio": ciudad,
            "direccion": direccion,
            "telefono": str(p.get("phone") or ""),
            "web": p.get("site") or p.get("website") or "",
            "email": emails[0] if emails else "",
            "emails": emails,
            "rating": rating,
            "n_resenas": n,
            "horario_raw": horario,
            "categoria": p.get("category") or p.get("type") or "",
            "lat": p.get("latitude"), "lng": p.get("longitude"),
            "estado": "nuevo",
            "creado": ahora(),
            "envios": [],
        }
        nuevos += 1
    return nuevos


def _celda(v):
    if v is None:
        return None
    if isinstance(v, float) and v != v:  # NaN
        return None
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("{") or v.startswith("["):
            try:
                import json, ast
                try:
                    return json.loads(v)
                except Exception:
                    return ast.literal_eval(v)
            except Exception:
                return v
    return v


def importar(ruta):
    """Lee un CSV/XLSX exportado desde app.outscraper.cloud (Google Maps Data) y lo pasa a leads."""
    import csv
    filas = []
    if ruta.lower().endswith((".xlsx", ".xls")):
        try:
            import openpyxl
        except ImportError:
            raise SystemExit("Para .xlsx: pip install openpyxl (o exporta en CSV)")
        wb = openpyxl.load_workbook(ruta, read_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        cab = [str(c or "").strip() for c in next(it)]
        filas = [dict(zip(cab, r)) for r in it]
    else:
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            muestra = f.read(4096); f.seek(0)
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t")
            filas = list(csv.DictReader(f, dialect=dialecto))
    return [{k: _celda(v) for k, v in r.items()} for r in filas]


def main():
    cfg = cargar_config()
    leads = cargar_leads()
    if "--importar" in sys.argv:
        ruta = sys.argv[sys.argv.index("--importar") + 1]
        nuevos = registrar(importar(ruta), leads, None)
        guardar_leads(leads)
        print(f"\n✓ {nuevos} talleres nuevos importados · {len(leads)} en total → datos/leads.csv")
        return
    key = cfg.get("OUTSCRAPER_API_KEY")
    if not key:
        raise SystemExit("Falta OUTSCRAPER_API_KEY. Opción gratis: exporta desde la web de Outscraper y usa --importar fichero.csv")
    municipios = sys.argv[1:] or MUNICIPIOS
    nuevos = 0
    for muni in municipios:
        for q in CONSULTAS:
            consulta = f"{q}, {muni}, Barcelona"
            print(f"→ {consulta}")
            nuevos += registrar(buscar(key, consulta), leads, muni)
            guardar_leads(leads)
            time.sleep(1)
    print(f"\n✓ {nuevos} talleres nuevos · {len(leads)} en total → datos/leads.csv")


if __name__ == "__main__":
    main()
