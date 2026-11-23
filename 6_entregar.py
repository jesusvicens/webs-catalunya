"""Pas 6 · Entrega automàtica quan un taller paga.

Mira a Stripe els pagaments completats (el client_reference_id és el slug del taller),
genera la versió final (sense la franja de proposta), la publica en un lloc nou de Netlify
i envia al client l'enllaç de la seva web.

Ús:  python 6_entregar.py                          # revisa pagaments i entrega els nous
     python 6_entregar.py --dominio SLUG domini.cat   # connecta el domini propi del client
     python 6_entregar.py --actualitzar SLUG          # torna a publicar la web d'un client (després de canvis)
Es pot executar cada dia amb el cron, just després de 5_enviar.py.
"""
import importlib
import io
import smtplib
import sys
import time
import zipfile
from email.message import EmailMessage
from email.utils import formataddr

import requests

from comun import SALIDA, ahora, cargar_config, cargar_leads, guardar_leads

gen = importlib.import_module("3_generar")
NETLIFY = "https://api.netlify.com/api/v1"


def pagaments(cfg):
    """Sessions de Checkout pagades dels últims 30 dies → {slug: dades}."""
    key = cfg.get("STRIPE_SECRET_KEY")
    if not key:
        print("! Falta STRIPE_SECRET_KEY: no es poden comprovar pagaments")
        return {}
    out, params = {}, {"status": "complete", "limit": 100,
                       "created[gte]": int(time.time()) - 30 * 86400}
    while True:
        r = requests.get("https://api.stripe.com/v1/checkout/sessions", params=params,
                         auth=(key, ""), timeout=30)
        r.raise_for_status()
        d = r.json()
        for s in d["data"]:
            if s.get("payment_status") in ("paid", "no_payment_required") and s.get("client_reference_id"):
                out[s["client_reference_id"]] = {
                    "session": s["id"], "email": (s.get("customer_details") or {}).get("email"),
                    "subscription": s.get("subscription"), "import": (s.get("amount_total") or 0) / 100}
        if not d.get("has_more"):
            return out
        params["starting_after"] = d["data"][-1]["id"]


def render_final(l, cfg):
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(loader=FileSystemLoader(gen.RAIZ / "plantilla"), autoescape=select_autoescape(["html"]))
    html = env.get_template("taller.html").render(**gen.contexto(l, cfg, demo=False))
    dest = SALIDA / "finales" / l["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(html, encoding="utf-8")
    return dest


def publicar(cfg, l, carpeta):
    h = {"Authorization": f"Bearer {cfg['NETLIFY_TOKEN']}"}
    if not l.get("netlify_site_id"):
        nom = f"{l['slug'][:40]}-web".strip("-")
        r = requests.post(f"{NETLIFY}/sites", headers=h, json={"name": nom}, timeout=60)
        if r.status_code == 422:  # nom ocupat
            r = requests.post(f"{NETLIFY}/sites", headers=h, json={"name": f"{nom}-{int(time.time()) % 10000}"}, timeout=60)
        r.raise_for_status()
        l["netlify_site_id"] = r.json()["id"]
        l["web_final"] = r.json().get("ssl_url") or r.json().get("url")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in carpeta.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(carpeta).as_posix())
    r = requests.post(f"{NETLIFY}/sites/{l['netlify_site_id']}/deploys",
                      headers={**h, "Content-Type": "application/zip"}, data=buf.getvalue(), timeout=300)
    r.raise_for_status()
    return l["web_final"]


def avisar_client(cfg, l, url):
    msg = EmailMessage()
    msg["From"] = formataddr((cfg["REMITENTE_NOMBRE"], cfg["EMAIL_USER"]))
    msg["To"] = l.get("email_pagament") or l["email"]
    if cfg.get("BCC_COPIA"):
        msg["Bcc"] = cfg["BCC_COPIA"]
    msg["Subject"] = f"La web de {gen.nombre_corto(l['nombre'])} ja és en línia"
    msg.set_content(f"""Hola,

Gràcies per la confiança! La vostra web ja funciona:
{url}

Ara mateix té una adreça provisional. Si ja teniu un domini, digueu-me quin és; si no, digueu-me quin us agradaria (per exemple {l['slug'].split('-')[0]}.cat) i el registro a nom vostre.

Si voleu canviar qualsevol text, horari o posar-hi fotos del taller, només cal que respongueu aquest correu.

{cfg.get('REMITENTE_FIRMA', '')}""")
    with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg.get("SMTP_PORT", 587)), timeout=60) as s:
        s.starttls()
        s.login(cfg["EMAIL_USER"], cfg["EMAIL_PASS"])
        s.send_message(msg)


def main():
    cfg = cargar_config()
    leads = cargar_leads()
    per_slug = {l["slug"]: l for l in leads.values()}

    if "--dominio" in sys.argv:
        i = sys.argv.index("--dominio")
        slug, dom = sys.argv[i + 1], sys.argv[i + 2]
        l = per_slug[slug]
        r = requests.patch(f"{NETLIFY}/sites/{l['netlify_site_id']}",
                           headers={"Authorization": f"Bearer {cfg['NETLIFY_TOKEN']}"},
                           json={"custom_domain": dom}, timeout=60)
        r.raise_for_status()
        l["dominio"] = dom
        guardar_leads(leads)
        print(f"✓ {dom} connectat a {l['nombre']}. Al registrador, apunta el DNS:\n"
              f"   CNAME www → {l['web_final'].replace('https://', '')}\n"
              f"   A     @   → 75.2.60.5   (balancejador de Netlify)\n"
              f"Netlify activarà l'HTTPS sol en uns minuts.")
        return

    if "--actualitzar" in sys.argv:
        l = per_slug[sys.argv[sys.argv.index("--actualitzar") + 1]]
        print("✓ Actualitzada:", publicar(cfg, l, render_final(l, cfg)))
        guardar_leads(leads)
        return

    nous = 0
    for slug, p in pagaments(cfg).items():
        l = per_slug.get(slug)
        if not l:
            print(f"! Pagament amb referència desconeguda: {slug} ({p['email']}) — revisa-ho a Stripe")
            continue
        if l.get("estado") == "cliente":
            continue
        l.update({"estado": "cliente", "pagado": ahora(), "stripe_session": p["session"],
                  "stripe_subscription": p["subscription"], "email_pagament": p["email"]})
        try:
            url = publicar(cfg, l, render_final(l, cfg))
            avisar_client(cfg, l, url)
            print(f"✓ NOU CLIENT: {l['nombre']} — {url}")
            nous += 1
        except Exception as e:  # noqa
            l["notas"] = f"error entrega: {e}"
            print(f"! {l['nombre']}: {e}")
        guardar_leads(leads)
    print(f"✓ {nous} webs entregades")


if __name__ == "__main__":
    main()
