"""Paso 4 · Publica todas las demos en Netlify (un único sitio, una carpeta por taller).

Cada taller queda en  DEMO_BASE_URL/<slug>/
El sitio entero lleva noindex: Google no lo indexa y nadie lo confunde con su web oficial.
"""
import io
import zipfile

import requests

from comun import SALIDA, cargar_config, cargar_leads, guardar_leads


def main():
    cfg = cargar_config()
    token, site = cfg.get("NETLIFY_TOKEN"), cfg.get("NETLIFY_SITE_ID")
    base = cfg.get("DEMO_BASE_URL", "").rstrip("/")
    if not (token and site and base):
        raise SystemExit("Faltan NETLIFY_TOKEN, NETLIFY_SITE_ID o DEMO_BASE_URL en config.env")

    carpeta = SALIDA / "sites"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in carpeta.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(carpeta).as_posix())
    print(f"Subiendo {buf.tell() / 1e6:.1f} MB a Netlify…")
    r = requests.post(f"https://api.netlify.com/api/v1/sites/{site}/deploys",
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/zip"},
                      data=buf.getvalue(), timeout=600)
    r.raise_for_status()
    print("✓ Deploy:", r.json().get("state"), r.json().get("deploy_ssl_url") or "")

    leads = cargar_leads()
    n = 0
    for l in leads.values():
        if l.get("generado") and (carpeta / l["slug"] / "index.html").exists():
            l["demo_url"] = f"{base}/{l['slug']}/"
            n += 1
    guardar_leads(leads)
    print(f"✓ {n} demos publicadas · ejemplo: {next((l['demo_url'] for l in leads.values() if l.get('demo_url')), '-')}")


if __name__ == "__main__":
    main()
