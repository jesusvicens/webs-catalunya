"""Paso 2 · Decide a quién escribir.

- Sin web (o solo Facebook/Instagram)  → objetivo
- Web mala (sin móvil, sin https, lenta, abandonada) → objetivo
- Web decente → descartado
Objetivo + email → 'objetivo'   ·   objetivo sin email → 'solo_telefono' (lista para llamar/WhatsApp)
También descarga 3 buenas reseñas de Google para cada objetivo.
"""
import re
import time

import requests

from comun import cargar_config, cargar_leads, guardar_leads

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
REDES = ("facebook.com", "instagram.com", "linktr.ee", "google.com", "goo.gl", "wa.me",
         "business.site", "paginasamarillas", "tiktok.com")
MIN_RATING = 3.8   # no escribimos a talleres con mala reputación: su problema no es la web


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_MALOS = ("example", "sentry", "wixpress", "wix.com", "domain.com", "email.com", "tuemail",
               "yourmail", "godaddy", "@2x", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")


def emails_en(html):
    html = html.replace("&#64;", "@").replace("%40", "@").replace("[at]", "@").replace("(at)", "@")
    out = []
    for e in EMAIL_RE.findall(html):
        e = e.strip(".").lower()
        if any(m in e for m in EMAIL_MALOS) or len(e) > 60:
            continue
        if e not in out:
            out.append(e)
    return out


def buscar_email(url, html):
    """Busca un correo en la portada y, si no, en la página de contacto."""
    found = emails_en(html)
    if found:
        return found[0]
    base = url.rstrip("/")
    links = re.findall(r'href=["\']([^"\']*(?:contact|contacte|contacto|contactar)[^"\']*)["\']', html, re.I)
    candidatos = [l if l.startswith("http") else base + "/" + l.lstrip("/") for l in links[:2]]
    candidatos += [base + "/contacte", base + "/contacto"]
    for c in candidatos[:4]:
        try:
            r = requests.get(c, headers=UA, timeout=10)
            if r.status_code < 400:
                found = emails_en(r.text[:300_000])
                if found:
                    return found[0]
        except requests.RequestException:
            pass
    return ""


def auditar(url, lead=None):
    """Devuelve (es_mala, motivo_en_catalán). Si encuentra un correo en la web, lo guarda en lead."""
    if not url or any(r in url.lower() for r in REDES):
        return True, "sin_web"
    motivos = []
    try:
        t0 = time.time()
        r = requests.get(url, headers=UA, timeout=15, allow_redirects=True)
        seg = time.time() - t0
        html = r.text[:400_000].lower()
    except requests.RequestException:
        return True, "web_caida"
    if r.status_code >= 400:
        return True, "web_caida"
    if lead is not None and not lead.get("email"):
        try:
            lead["email"] = buscar_email(r.url, r.text[:400_000])
        except Exception:  # noqa
            pass
    if not r.url.startswith("https"):
        motivos.append("no_https")
    if 'name="viewport"' not in html and "name='viewport'" not in html:
        motivos.append("no_movil")
    if seg > 5:
        motivos.append("lenta")
    anys = [int(a) for a in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20\d{2}|19\d{2})", html)]
    if anys and max(anys) <= 2019:
        motivos.append("abandonada")
    if any(x in html for x in ("jquery-1.", "<frameset", ".swf", "wix.com/website-template", "<marquee")):
        motivos.append("anticuada")
    # Considerada mala con un motivo fuerte o dos débiles
    fuertes = {"no_movil", "abandonada", "no_https"}
    if fuertes & set(motivos) or len(motivos) >= 2:
        return True, ",".join(motivos)
    return False, ",".join(motivos)


def resenas(api_key, place_id):
    try:
        r = requests.get("https://api.app.outscraper.com/maps/reviews-v3",
                         params={"query": place_id, "reviewsLimit": 20, "sort": "most_relevant",
                                 "language": "ca", "async": "false"},
                         headers={"X-API-KEY": api_key}, timeout=180)
        datos = (r.json().get("data") or [{}])[0]
    except Exception as e:  # noqa
        print("   ! reseñas:", e)
        return []
    buenas = []
    for rv in datos.get("reviews_data") or []:
        txt = (rv.get("review_text") or "").strip().replace("\n", " ")
        if rv.get("review_rating", 0) >= 5 and 50 <= len(txt) <= 300:
            nombre = (rv.get("author_title") or "Client").split()
            autor = nombre[0] + (f" {nombre[1][0]}." if len(nombre) > 1 else "")
            buenas.append({"autor": autor, "texto": txt, "estrellas": 5})
    return buenas[:3]


def main():
    cfg = cargar_config()
    leads = cargar_leads()
    pendientes = [l for l in leads.values() if l["estado"] == "nuevo"]
    print(f"Auditando {len(pendientes)} talleres…")
    for l in pendientes:
        if (l.get("rating") or 0) < MIN_RATING or (l.get("n_resenas") or 0) < 5:
            l["estado"], l["motivo"] = "descartado", "pocas_o_malas_resenas"
            continue
        mala, motivo = auditar(l.get("web"), l)
        l["motivo"] = motivo
        if not mala:
            l["estado"] = "descartado"
        else:
            l["estado"] = "objetivo" if l.get("email") else "solo_telefono"
            if cfg.get("OUTSCRAPER_API_KEY"):
                l["resenas"] = resenas(cfg["OUTSCRAPER_API_KEY"], l["id"])
        print(f"  {l['estado']:<14} {l['nombre'][:40]:<40} {motivo}")
        guardar_leads(leads)

    cuenta = {}
    for l in leads.values():
        cuenta[l["estado"]] = cuenta.get(l["estado"], 0) + 1
    print("\n✓", cuenta)


if __name__ == "__main__":
    main()
