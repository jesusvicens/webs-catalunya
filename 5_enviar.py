"""Paso 5 · Envía el primer email y los seguimientos, y detecta respuestas y rebotes.

Uso:  python 5_enviar.py                    # SIMULACIÓN: muestra lo que enviaría, no envía nada
      python 5_enviar.py --real             # envía de verdad
      python 5_enviar.py --prueba tu@mail   # te manda el email del primer lead a ti, para revisarlo
Pensado para ejecutarse una vez al día (cron / Programador de tareas). Respeta MAX_ENVIOS_DIA,
horario laboral y pausas aleatorias entre envíos. Si alguien responde, se para su secuencia.
"""
import email
import imaplib
import random
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

from comun import ahora, cargar_config, cargar_leads, guardar_leads
from mensajes import ASUNTO, MOTIVOS, PASOS
import importlib
nombre_corto = importlib.import_module("3_generar").nombre_corto


def texto_motivo(l):
    partes = [MOTIVOS[m] for m in (l.get("motivo") or "sin_web").split(",") if m in MOTIVOS]
    partes = list(dict.fromkeys(partes))  # sin duplicados
    if not partes:
        partes = [MOTIVOS["sin_web"]]
    frase = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " i " + partes[-1]
    return frase.format(municipio=l["municipio"])


def componer(l, paso, cfg):
    v = {
        "nombre": l["nombre"], "nombre_corto": nombre_corto(l["nombre"]), "municipio": l["municipio"],
        "rating": str(l.get("rating") or "").replace(".", ","), "n_resenas": l.get("n_resenas", 0),
        "motivo": texto_motivo(l), "url": l.get("demo_url", ""),
        "precio": cfg.get("PRECIO_UNICO"), "precio_mes": cfg.get("PRECIO_MES"),
        "firma": cfg.get("REMITENTE_FIRMA"), "remitente": cfg.get("REMITENTE_NOMBRE"),
    }
    asunto = ASUNTO.format(**v)
    return (asunto if paso == 0 else "Re: " + asunto), PASOS[paso].format(**v)


def enviar(cfg, para, asunto, cuerpo, responde_a=None):
    msg = EmailMessage()
    msg["From"] = formataddr((cfg["REMITENTE_NOMBRE"], cfg["EMAIL_USER"]))
    msg["To"] = para
    msg["Subject"] = asunto
    mid = make_msgid(domain=cfg["EMAIL_USER"].split("@")[1])
    msg["Message-ID"] = mid
    if cfg.get("BCC_COPIA"):
        msg["Bcc"] = cfg["BCC_COPIA"]
    msg["List-Unsubscribe"] = f"<mailto:{cfg['EMAIL_USER']}?subject=baixa>"
    if responde_a:
        msg["In-Reply-To"] = responde_a
        msg["References"] = responde_a
    msg.set_content(cuerpo)
    with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg.get("SMTP_PORT", 587)), timeout=60) as s:
        s.starttls()
        s.login(cfg["EMAIL_USER"], cfg["EMAIL_PASS"])
        s.send_message(msg)
    return mid


def revisar_buzon(cfg, leads):
    """Marca 'respondido' a quien haya contestado y 'rebotado' si el correo no existe."""
    activos = {l["email"].lower(): l for l in leads.values() if l.get("envios") and l["estado"] == "contactado"}
    if not activos:
        return
    try:
        im = imaplib.IMAP4_SSL(cfg["IMAP_HOST"])
        im.login(cfg["EMAIL_USER"], cfg["EMAIL_PASS"])
        im.select("INBOX", readonly=True)
        d0 = datetime.now() - timedelta(days=30)
        mes = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d0.month - 1]
        desde = f"{d0.day:02d}-{mes}-{d0.year}"
        _, ids = im.search(None, f'(SINCE "{desde}")')
        for i in ids[0].split()[-500:]:
            _, d = im.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM)] BODY.PEEK[TEXT]<0.4000>)")
            bruto = b"".join(p[1] for p in d if isinstance(p, tuple)).decode(errors="ignore").lower()
            remitente = email.utils.parseaddr(email.message_from_string(bruto).get("from", ""))[1]
            if remitente in activos:
                l = activos.pop(remitente)
                l["estado"], l["respondio"] = "respondido", ahora()
                print(f"  ✉ RESPUESTA de {l['nombre']} — contéstale tú")
            elif "mailer-daemon" in remitente or "postmaster" in remitente:
                for em, l in list(activos.items()):
                    if em in bruto:
                        l["estado"] = "rebotado"; activos.pop(em)
                        print(f"  ✗ rebote: {l['nombre']} ({em})")
        im.logout()
    except Exception as e:  # noqa
        print("  ! No se pudo revisar el buzón:", e)


def pendientes(leads, dias_seg):
    """Lista (lead, paso) que tocan hoy: primero seguimientos, luego nuevos."""
    hoy = datetime.now()
    seg, nuevos = [], []
    for l in leads.values():
        if not l.get("demo_url") or not l.get("email"):
            continue
        n = len(l.get("envios", []))
        if l["estado"] == "objetivo" and n == 0:
            nuevos.append((l, 0))
        elif l["estado"] == "contactado" and 0 < n <= len(dias_seg):
            primero = datetime.fromisoformat(l["envios"][0]["fecha"])
            if hoy >= primero + timedelta(days=dias_seg[n - 1]):
                seg.append((l, n))
    nuevos.sort(key=lambda x: (-(x[0].get("rating") or 0) * (x[0].get("n_resenas") or 0)))
    return seg + nuevos


def main():
    cfg = cargar_config()
    leads = cargar_leads()
    real = "--real" in sys.argv

    if "--prueba" in sys.argv:
        dest = sys.argv[sys.argv.index("--prueba") + 1]
        l = next((x for x in leads.values() if x.get("demo_url")), None) or next(iter(leads.values()))
        for paso in range(len(PASOS)):
            asunto, cuerpo = componer(l, paso, cfg)
            enviar(cfg, dest, f"[PRUEBA {paso}] {asunto}", cuerpo)
        print(f"✓ {len(PASOS)} emails de prueba enviados a {dest}")
        return

    dias_seg = [int(x) for x in cfg.get("SEGUIMIENTOS_DIAS", "4,10").split(",")]
    if real:
        revisar_buzon(cfg, leads); guardar_leads(leads)

    hoy = datetime.now().date().isoformat()
    ya_hoy = sum(1 for l in leads.values() for e in l.get("envios", []) if e["fecha"].startswith(hoy))
    cupo = max(0, int(cfg.get("MAX_ENVIOS_DIA", 25)) - ya_hoy)
    por_ejec = int(cfg.get("MAX_POR_EJECUCION", 0) or 0)  # en la nube: pocos por ejecución, sin pausas
    cola = pendientes(leads, dias_seg)[:cupo]
    if por_ejec:
        cola = cola[:por_ejec]
    print(f"{len(cola)} emails para hoy (cupo restante {cupo})" + ("" if real else " — SIMULACIÓN, usa --real para enviar"))

    for k, (l, paso) in enumerate(cola):
        h = datetime.now()
        if real and (h.weekday() >= 5 or not int(cfg["HORA_INICIO"]) <= h.hour < int(cfg["HORA_FIN"])):
            print("Fuera de horario laboral; paro aquí."); break
        asunto, cuerpo = componer(l, paso, cfg)
        if not real:
            print(f"\n─── {l['email']} · paso {paso} ───\nAsunto: {asunto}\n\n{cuerpo}")
            continue
        try:
            prev = l["envios"][0]["message_id"] if l.get("envios") else None
            mid = enviar(cfg, l["email"], asunto, cuerpo, prev)
            l.setdefault("envios", []).append({"paso": paso, "fecha": ahora(), "message_id": mid})
            l["estado"] = "contactado"
            if paso == len(PASOS) - 1:
                l["estado"] = "secuencia_terminada"
            print(f"  ✓ [{paso}] {l['nombre']} <{l['email']}>")
        except Exception as e:  # noqa
            l["notas"] = f"error envío: {e}"
            print(f"  ! {l['nombre']}: {e}")
        guardar_leads(leads)
        if k < len(cola) - 1 and not por_ejec:
            time.sleep(random.randint(int(cfg["PAUSA_MIN_SEG"]), int(cfg["PAUSA_MAX_SEG"])))


if __name__ == "__main__":
    main()
