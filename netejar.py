"""Descarta cadenes i tallers de fora d'Osona que s'hagin colat, i esborra les seves demos."""
import importlib, re, shutil
from comun import MUNICIPIOS, SALIDA, cargar_leads, guardar_leads
b = importlib.import_module("1_buscar")
leads = cargar_leads()
munis = [m.lower() for m in MUNICIPIOS]
n = 0
for l in leads.values():
    nom = (l.get("nombre") or "").lower()
    dl = (l.get("direccion") or "").lower()
    fora = (l.get("municipio") or "").lower() not in munis and not any(
        re.search(r"(?<!\w)" + re.escape(m) + r"(?!\w)", dl) for m in munis)
    if fora or any(c in nom for c in b.CADENAS):
        if l.get("estado") != "descartado":
            l["estado"], l["motivo"] = "descartado", "fora_osona_o_cadena"
            n += 1
        shutil.rmtree(SALIDA / "sites" / l["slug"], ignore_errors=True)
        l.pop("demo_url", None)
guardar_leads(leads)
print(f"{n} descartats")
