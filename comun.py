"""Utilidades compartidas: configuración, base de datos de leads (JSON) y helpers."""
import csv
import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos"
SALIDA = RAIZ / "salida"
LEADS_JSON = DATOS / "leads.json"
LEADS_CSV = DATOS / "leads.csv"

# Municipios de Osona (sin los que pasaron al Lluçanès en 2023). Edita a tu gusto.
MUNICIPIOS = [
    "Vic", "Manlleu", "Torelló", "Centelles", "Roda de Ter", "Tona", "Taradell",
    "Sant Quirze de Besora", "Sant Hipòlit de Voltregà", "Les Masies de Voltregà",
    "Gurb", "Calldetenes", "Santa Eugènia de Berga", "Sant Julià de Vilatorta",
    "Folgueroles", "Balenyà", "Seva", "Aiguafreda", "Sant Pere de Torelló",
    "Sant Vicenç de Torelló", "Montesquiu", "Viladrau", "l'Esquirol", "Malla",
    "Muntanyola", "Les Masies de Roda", "Santa Cecília de Voltregà",
    "Sant Bartomeu del Grau", "Orís", "Sant Martí de Centelles",
]

# Búsquedas por municipio (Google Maps). Puedes añadir variantes.
CONSULTAS = ["taller mecànic", "taller de cotxes", "taller mecánico"]

# Palabras que deben aparecer en la categoría de Google para considerarlo taller.
CATEGORIAS_OK = ["taller", "mecàn", "mecán", "car repair", "auto repair", "mechanic",
                 "neumátic", "pneumàtic", "tire", "chapa", "body shop", "automoción",
                 "automòbil", "vehicle", "vehículo"]


def cargar_config():
    cfg = {}
    ruta = RAIZ / "config.env"
    if not ruta.exists():
        raise SystemExit("Falta config.env — copia config.env.example y rellénalo.")
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        cfg[k.strip()] = v.strip()
    cfg.update({k: v for k, v in os.environ.items() if k in cfg})
    return cfg


def cargar_leads():
    if LEADS_JSON.exists():
        return json.loads(LEADS_JSON.read_text(encoding="utf-8"))
    return {}


def guardar_leads(leads):
    DATOS.mkdir(exist_ok=True)
    tmp = LEADS_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(leads, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(LEADS_JSON)
    exportar_csv(leads)


def exportar_csv(leads):
    """CSV legible para abrir en Excel/Sheets (solo lectura: la fuente es leads.json)."""
    cols = ["estado", "nombre", "municipio", "telefono", "email", "web", "motivo",
            "rating", "n_resenas", "demo_url", "enviados", "ultimo_envio", "respondio", "notas"]
    with open(LEADS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cols)
        for l in sorted(leads.values(), key=lambda x: (x.get("estado", ""), x.get("municipio", ""))):
            w.writerow([l.get("estado", ""), l.get("nombre", ""), l.get("municipio", ""),
                        l.get("telefono", ""), l.get("email", ""), l.get("web", ""),
                        l.get("motivo", ""), l.get("rating", ""), l.get("n_resenas", ""),
                        l.get("demo_url", ""), len(l.get("envios", [])),
                        (l.get("envios") or [{}])[-1].get("fecha", ""),
                        l.get("respondio", ""), l.get("notas", "")])


def slugify(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:60] or "negoci"


def ahora():
    return datetime.now().isoformat(timespec="seconds")
