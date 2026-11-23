"""Paso 3 · Genera una web personalizada por cada taller objetivo.

Uso:  python 3_generar.py                 # todos los 'objetivo' y 'solo_telefono'
      python 3_generar.py --capturas      # además, captura móvil PNG (para WhatsApp)
      python 3_generar.py --final SLUG    # versión sin franja de demo para un cliente que ha comprado
Salida: salida/sites/<slug>/index.html
"""
import hashlib
import json
import re
import sys
from datetime import date
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from comun import RAIZ, SALIDA, cargar_config, cargar_leads, guardar_leads
from sectors import SECTORS

# Colores de taller: (acento, texto sobre el acento)
COLORES = [
    ("#1f4fa3", "#ffffff"),  # blau granota
    ("#b8321f", "#ffffff"),  # vermell taller
    ("#c44d14", "#ffffff"),  # taronja
    ("#2d6a3e", "#ffffff"),  # verd anglès
    ("#f2b705", "#1d1b18"),  # groc senyal
]

DIAS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_CA = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]

TITULARES = [
    ("El teu cotxe,", "en bones mans"),
    ("Mecànica", "de confiança"),
    ("Reparem.", "Sense sorpreses."),
    ("Taller de", "tota la vida"),
]

def _svg(path):
    return Markup('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>')

SERVICIOS = [
    {"titol": "Mecànica general", "text": "Motor, embragatge, distribució, suspensió i tot el que faci falta perquè el cotxe vagi fi.",
     "icono": _svg('<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>')},
    {"titol": "Revisions i manteniment", "text": "Canvi d'oli i filtres segons el pla del fabricant, sense perdre la garantia.",
     "icono": _svg('<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>')},
    {"titol": "Pre-ITV", "text": "Revisem el cotxe abans de la ITV perquè la passis a la primera.",
     "icono": _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>')},
    {"titol": "Frens i pneumàtics", "text": "Pastilles, discos, alineació i pneumàtics de totes les mides.",
     "icono": _svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M12 3v6M12 15v6M3 12h6M15 12h6"/>')},
    {"titol": "Diagnosi electrònica", "text": "Llegim les avaries amb màquina i et diem exactament què passa.",
     "icono": _svg('<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M6 14l3-4 3 3 3-5 3 6"/><path d="M8 22h8"/>')},
    {"titol": "Aire condicionat", "text": "Càrrega de gas, revisió de fuites i neteja del circuit.",
     "icono": _svg('<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>')},
]


def _hora(h, m, ampm):
    h = int(h); m = int(m or 0)
    if ampm == "PM" and h != 12: h += 12
    if ampm == "AM" and h == 12: h = 0
    return f"{h}:{m:02d}"


def _rango(txt):
    txt = txt.replace(" ", " ").replace("–", "-").replace("—", "-").upper()
    m = re.match(r"\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\s*-\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?", txt)
    if not m:
        return txt.strip().capitalize()
    h1, m1, a1, h2, m2, a2 = m.groups()
    if not a1:
        # "3-7PM" → mismo sufijo; "11-2PM" → AM
        a1 = a2 if a2 and int(h1) <= int(h2) and int(h1) != 12 else ("AM" if a2 == "PM" else a2)
    return f"{_hora(h1, m1, a1)}–{_hora(h2, m2, a2)}"


DIAS_ALIAS = [
    ("monday", "lunes", "dilluns"), ("tuesday", "martes", "dimarts"), ("wednesday", "miércoles", "miercoles", "dimecres"),
    ("thursday", "jueves", "dijous"), ("friday", "viernes", "divendres"), ("saturday", "sábado", "sabado", "dissabte"),
    ("sunday", "domingo", "diumenge"),
]
TANCAT = ("closed", "cerrado", "tancat")


def horario(raw):
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            raw = {}
    raw = {str(k).strip().lower(): v for k, v in (raw or {}).items()} if isinstance(raw, dict) else {}
    out = []
    for i, alias in enumerate(DIAS_ALIAS):
        v = next((raw[a] for a in alias if a in raw), None)
        if v is None:
            out.append({"dia": DIAS_CA[i], "horas": "—", "abierto": False}); continue
        partes = v if isinstance(v, list) else str(v).split(",")
        partes = [str(p).strip() for p in partes if str(p).strip()]
        if not partes or partes[0].lower().startswith(TANCAT):
            out.append({"dia": DIAS_CA[i], "horas": "Tancat", "abierto": False})
        elif "24" in partes[0] and ("hour" in partes[0].lower() or "hora" in partes[0].lower()):
            out.append({"dia": DIAS_CA[i], "horas": "24 h", "abierto": True})
        else:
            out.append({"dia": DIAS_CA[i], "horas": " · ".join(_rango(p) for p in partes), "abierto": True})
    return out


def telefono(raw):
    digitos = re.sub(r"\D", "", raw or "")
    if digitos.startswith("34") and len(digitos) == 11:
        digitos = digitos[2:]
    if len(digitos) != 9:
        return raw or "", raw or "", ""
    bonito = f"{digitos[:3]} {digitos[3:5]} {digitos[5:7]} {digitos[7:]}"
    wa = f"34{digitos}" if digitos[0] in "67" else ""
    return bonito, f"+34{digitos}", wa


def _bonic(n):
    """'TALLERS PUIG S.L.' → 'Tallers Puig S.L.' (només si el nom ve tot en majúscules)."""
    if n.upper() != n:
        return n
    petites = {"de", "del", "la", "les", "el", "els", "i", "y", "d'", "l'"}
    paraules = [w.capitalize() if w.lower() not in petites else w.lower() for w in n.lower().split()]
    return " ".join(paraules)


def nombre_corto(n):
    n = _bonic(n)
    n = re.sub(r"\b(s\.?l\.?u?|s\.?a\.?|s\.?c\.?p\.?)\b\.?", "", n, flags=re.I).strip(" ,.-")
    return n if len(n) <= 34 else n[:32].rsplit(" ", 1)[0]


DIAS_SCHEMA = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def schema(l, hor, tel_tel, rating, n, tipus="AutoRepair"):
    """Marcado schema.org de negocio local: ayuda a salir en Google con horario y estrellas."""
    spec = []
    for i, h in enumerate(hor):
        for a, b in re.findall(r"(\d{1,2}:\d{2})–(\d{1,2}:\d{2})", h["horas"]):
            spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": DIAS_SCHEMA[i],
                         "opens": a.zfill(5), "closes": b.zfill(5)})
    data = {"@context": "https://schema.org", "@type": tipus, "name": l["nombre"],
            "telephone": tel_tel, "address": l.get("direccion", ""),
            "areaServed": l["municipio"], "openingHoursSpecification": spec}
    if l.get("email"):
        data["email"] = l["email"]
    if l.get("lat") and l.get("lng"):
        data["geo"] = {"@type": "GeoCoordinates", "latitude": l["lat"], "longitude": l["lng"]}
    if rating and n:
        data["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": rating, "reviewCount": n}
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def contexto(l, cfg, demo=True):
    h = int(hashlib.md5(l["slug"].encode()).hexdigest(), 16)
    sec = SECTORS.get(l.get("sector") or "taller", SECTORS["taller"])
    t1, t2 = sec["titulars"][h % len(sec["titulars"])]
    tel, tel_tel, wa = telefono(l.get("telefono"))
    rating = l.get("rating") or 0
    n = l.get("n_resenas") or 0
    sub = sec["sub"].format(muni=l["municipio"])
    if rating >= 4.5 and n >= 15:
        sub += f" {n} clients ens valoren amb un {str(rating).replace('.', ',')}."
    hor = horario(l.get("horario_raw") or {})
    muni = l["municipio"]
    q = quote(f"{l['nombre']}, {l.get('direccion', '')}")
    pid = l.get("id", "")
    pid_q = f"&query_place_id={pid}" if pid.startswith("ChIJ") else ""
    pid_d = f"&destination_place_id={pid}" if pid.startswith("ChIJ") else ""
    nc = nombre_corto(l["nombre"])
    return {
        "inicial": (re.sub(r"^(taller(s|es)?|auto(s)?|mec[aà]nica|instal[·.]?lacions|reformes|reformas|fusteria|pintures?|electricitat)\s+", "", nc, flags=re.I) or nc)[:1].upper(),
        "maps_url": f"https://www.google.com/maps/search/?api=1&query={q}{pid_q}",
        "dir_url": f"https://www.google.com/maps/dir/?api=1&destination={q}{pid_d}",
        "schema": schema(l, hor, tel_tel, rating, n, sec["schema"]),
        "demo": demo,
        "nombre": l["nombre"], "nombre_corto": nombre_corto(l["nombre"]),
        "municipio": muni, "municipio_corto": muni if len(muni) <= 9 else (l.get("comarca") or muni.split()[0])[:12],
        "direccion": l.get("direccion", ""),
        "telefono": tel, "telefono_tel": tel_tel, "whatsapp": wa,
        "email": l.get("email", ""),
        "rating_txt": f"{rating:.1f}".replace(".", ",") if rating else "5,0",
        "n_resenas": n,
        "resenas": l.get("resenas") or [],
        "horario": hor, "horario_json": json.dumps([x["horas"] for x in hor], ensure_ascii=False),
        "servicios": [{"titol": a, "text": b, "icono": c} for a, b, c in sec["serveis"]],
        "sec": sec,
        "titular_1": t1, "titular_2": t2, "subtitulo": sub,
        "color": COLORES[h % len(COLORES)][0], "color_txt": COLORES[h % len(COLORES)][1],
        "remitente": cfg.get("REMITENTE_NOMBRE", ""), "email_remitente": cfg.get("EMAIL_USER", ""),
        "any": date.today().year,
    }


def capturar(paginas):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        for html, png in paginas:
            pag.goto(html.as_uri()); pag.wait_for_timeout(1200)
            pag.screenshot(path=str(png))
        nav.close()


def main():
    cfg = cargar_config()
    leads = cargar_leads()
    env = Environment(loader=FileSystemLoader(RAIZ / "plantilla"), autoescape=select_autoescape(["html"]))
    tpl = env.get_template("taller.html")
    sites = SALIDA / "sites"; sites.mkdir(parents=True, exist_ok=True)

    if "--final" in sys.argv:
        slug = sys.argv[sys.argv.index("--final") + 1]
        l = next(x for x in leads.values() if x["slug"] == slug)
        dest = SALIDA / "finales" / slug; dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(tpl.render(**contexto(l, cfg, demo=False)), encoding="utf-8")
        print(f"✓ Versión final en {dest}/index.html — súbela a su dominio.")
        return

    hechos, capturas = 0, []
    for l in leads.values():
        # Regenera también las demos ya enviadas (en la nube no se guarda salida/)
        if l["estado"] == "descartado" or not (l["estado"] in ("objetivo", "solo_telefono") or l.get("generado")):
            continue
        d = sites / l["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(tpl.render(**contexto(l, cfg)), encoding="utf-8")
        l["generado"] = True
        capturas.append((d / "index.html", d / "movil.png"))
        hechos += 1
    guardar_leads(leads)

    # raíz del sitio de demos: sin indexar
    (sites / "index.html").write_text("<!doctype html><meta name=robots content=noindex><title>Demos</title>", encoding="utf-8")
    (sites / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n", encoding="utf-8")
    (sites / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    if "--capturas" in sys.argv and capturas:
        capturar(capturas)
    print(f"✓ {hechos} webs generadas en salida/sites/")


if __name__ == "__main__":
    main()
