"""Descarrega els oficis de la següent comarca amb Apify (Google Maps Scraper) i els deixa a datos/entrada/.

Necessita APIFY_TOKEN a config.env. Amb el pla gratuït (5 $/mes) dona per a 1-3 comarques al mes.
Estat: datos/comarques.json (comarques ja fetes). Si no hi ha crèdit, surt sense error.
"""
import json
import sys
import time
from datetime import date

import requests

from comun import DATOS, RAIZ, cargar_config

ACTOR = "compass~crawler-google-places"
TERMES = ["lampista", "electricista", "empresa de reformes", "pintor de cases", "fuster", "fontaner"]
ORDRE = ["Osona", "Moianès", "Ripollès", "Lluçanès", "Garrotxa", "Bages", "Vallès Oriental", "Selva", "Berguedà",
         "Gironès", "Vallès Occidental", "Maresme", "Anoia", "Baix Llobregat", "Pla de l'Estany", "Alt Empordà",
         "Baix Empordà", "Solsonès", "Cerdanya", "Garraf", "Alt Penedès", "Baix Penedès", "Alt Camp", "Tarragonès",
         "Baix Camp", "Conca de Barberà", "Segarra", "Urgell", "Pla d'Urgell", "Segrià", "Noguera", "Garrigues",
         "Priorat", "Ribera d'Ebre", "Baix Ebre", "Montsià", "Terra Alta", "Alt Urgell", "Pallars Jussà",
         "Pallars Sobirà", "Alta Ribagorça", "Val d'Aran", "Barcelonès"]
ESTAT = DATOS / "comarques.json"


def main():
    cfg = cargar_config()
    token = cfg.get("APIFY_TOKEN")
    if not token:
        print("Sense APIFY_TOKEN: no es descarreguen comarques noves."); return
    fetes = json.loads(ESTAT.read_text(encoding="utf-8")) if ESTAT.exists() else {"fetes": ["Osona"]}
    pendents = [c for c in ORDRE if c not in fetes["fetes"]]
    if not pendents:
        print("Totes les comarques fetes."); return
    comarca = pendents[0]
    entrada = {"searchStringsArray": TERMES, "locationQuery": f"{comarca}, Catalonia, Spain",
               "maxCrawledPlacesPerSearch": 100, "language": "es", "scrapeContacts": True,
               "skipClosedPlaces": True, "scrapePlaceDetailPage": False}
    h = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"https://api.apify.com/v2/acts/{ACTOR}/runs", headers=h, json=entrada, timeout=60)
    if r.status_code in (402, 403):
        print(f"Apify no permet començar ({r.status_code}): probablement sense crèdit aquest mes."); return
    r.raise_for_status()
    run = r.json()["data"]
    print(f"Comarca {comarca}: execució {run['id']} començada")
    for _ in range(170):  # fins a ~85 min
        time.sleep(30)
        run = requests.get(f"https://api.apify.com/v2/actor-runs/{run['id']}", headers=h, timeout=60).json()["data"]
        if run["status"] not in ("READY", "RUNNING"):
            break
    print("Estat:", run["status"], "· cost aprox.", run.get("usageTotalUsd"))
    items = requests.get(f"https://api.apify.com/v2/datasets/{run['defaultDatasetId']}/items?clean=true&format=json",
                         headers=h, timeout=300).json()
    if not items:
        print("Cap resultat; no es marca la comarca com a feta."); return
    (DATOS / "entrada").mkdir(exist_ok=True)
    (DATOS / "entrada" / f"{comarca}__oficis_{date.today().isoformat()}.json").write_text(
        json.dumps(items, ensure_ascii=False), encoding="utf-8")
    fetes["fetes"].append(comarca)
    ESTAT.write_text(json.dumps(fetes, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {len(items)} negocis de {comarca} desats")


if __name__ == "__main__":
    main()
