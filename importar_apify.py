"""Importa un dataset JSON exportat d'Apify (Google Maps Scraper) a datos/leads.json.

Ús:  python importar_apify.py fitxer.json [--comarca Osona]
Detecta el sector (lampista, electricista, reformes, pintor, fuster, taller) per la categoria i el nom.
"""
import json
import re
import sys

from comun import ahora, cargar_leads, guardar_leads, slugify
from sectors import detectar

CADENES = ("leroy", "bricomart", "bauhaus", "obramat", "norauto", "midas", "feu vert", "endesa", "iberdrola",
           "naturgy", "repsol", "securitas", "prosegur", "homeserve", "ralarsa")
NO_OFICI = ("arquitect", "estudio de arquitectura", "interiorista", "tienda", "botiga", "ferreter", "supermerc",
            "inmobiliari", "immobiliària", "ayuntamiento", "ajuntament", "proveedor", "distribuidor", "mayorista",
            "gestor", "asesor", "assessor", "automat", "broker", "technolog", "ingenier", "enginyer", "industrial")


def horari(oh):
    out = {}
    for d in oh or []:
        out[str(d.get("day", "")).lower()] = d.get("hours", "")
    return out


def main():
    ruta = sys.argv[1]
    comarca = sys.argv[sys.argv.index("--comarca") + 1] if "--comarca" in sys.argv else ""
    dades = json.load(open(ruta, encoding="utf-8"))
    leads = cargar_leads()
    nous, per_sector = 0, {}
    for p in dades:
        pid = p.get("placeId")
        if not pid or pid in leads or p.get("permanentlyClosed") or p.get("temporarilyClosed"):
            continue
        cat = " ".join([p.get("categoryName") or ""] + (p.get("categories") or []))
        nom = (p.get("title") or "").strip()
        if any(c in nom.lower() for c in CADENES) or any(c in (cat + " " + nom).lower() for c in NO_OFICI):
            continue
        sector = detectar(cat, nom, p.get("searchString"))
        if not sector:
            continue
        emails = []
        for e in (p.get("emails") or []):
            e = e.strip().lower()
            if "@" in e and e not in emails and not re.search(r"\.(png|jpg|webp|svg)$|example|sentry|wix", e):
                emails.append(e)
        ciutat = (p.get("city") or "").strip()
        if not ciutat or (ciutat == "Barcelona" and comarca != "Barcelonès"):
            continue  # sense població o adreça fiscal a Barcelona: no sabem on treballen
        loc = p.get("location") or {}
        leads[pid] = {
            "id": pid,
            "slug": slugify(f"{nom}-{ciutat}"),
            "nombre": nom,
            "municipio": ciutat,
            "comarca": comarca,
            "direccion": p.get("address") or ", ".join(x for x in [p.get("street"), ciutat] if x),
            "telefono": p.get("phone") or "",
            "web": p.get("website") or "",
            "email": emails[0] if emails else "",
            "emails": emails,
            "rating": p.get("totalScore") or 0,
            "n_resenas": p.get("reviewsCount") or 0,
            "horario_raw": horari(p.get("openingHours")),
            "categoria": p.get("categoryName") or "",
            "sector": sector,
            "lat": loc.get("lat"), "lng": loc.get("lng"),
            "estado": "nuevo",
            "creado": ahora(),
            "envios": [],
            "font": "apify",
        }
        nous += 1
        per_sector[sector] = per_sector.get(sector, 0) + 1
    guardar_leads(leads)
    print(f"✓ {nous} negocis nous: {per_sector}")


if __name__ == "__main__":
    main()
