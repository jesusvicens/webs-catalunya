"""Pas 7 · Pont de respostes: envia des de webscatalunya@gmail.com les respostes que redacta Claude.

Claude (tasca programada) llegeix les converses a jesusvicens8@gmail.com i, quan cal respondre un taller,
envia a webscatalunya@gmail.com un correu amb aquest format:

    Assumpte: [RELAY:<RELAY_TOKEN>] Re: Una web per a Taller X
    Cos:
        TO: taller@exemple.com
        SUBJECT: Re: Una web per a Taller X
        ---
        <text de la resposta>

Aquest script el llegeix per IMAP, comprova que ve de RELAY_REMITENT i porta el token,
l'envia al taller des de webscatalunya (amb còpia oculta a BCC_COPIA) i mou l'ordre a la paperera.

Programa'l cada 15 minuts en horari laboral:
    */15 9-19 * * 1-5  cd /ruta/webs-osona && python3 7_relay.py >> relay.log 2>&1
"""
import email
import imaplib
import re
import smtplib
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

from comun import cargar_config


def text_pla(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
                html = re.sub(r"<br\s*/?>|</p>|</div>", "\n", html, flags=re.I)
                return re.sub(r"<[^>]+>", "", html)
        return ""
    return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", "replace")


def main():
    cfg = cargar_config()
    token, remitent = cfg.get("RELAY_TOKEN"), cfg.get("RELAY_REMITENT", "").lower()
    if not token or not remitent:
        raise SystemExit("Falten RELAY_TOKEN o RELAY_REMITENT a config.env")

    im = imaplib.IMAP4_SSL(cfg["IMAP_HOST"])
    im.login(cfg["EMAIL_USER"], cfg["EMAIL_PASS"])
    im.select("INBOX")
    _, ids = im.search(None, f'(SUBJECT "[RELAY:{token}]")')
    enviats = 0
    for i in ids[0].split():
        _, d = im.fetch(i, "(RFC822)")
        msg = email.message_from_bytes(d[0][1])
        de = parseaddr(msg.get("From", ""))[1].lower()
        assumpte = str(make_header(decode_header(msg.get("Subject", ""))))
        if de != remitent or f"[RELAY:{token}]" not in assumpte:
            print(f"! Ordre ignorada (remitent {de})")
            im.store(i, "+X-GM-LABELS", "\\Trash")
            continue
        cos = text_pla(msg).replace("\r\n", "\n")
        m = re.search(r"^\s*TO:\s*(\S+@\S+)\s*\nSUBJECT:\s*(.+?)\s*\n-{3,}\s*\n(.*)$", cos, flags=re.S | re.M)
        if not m:
            print(f"! Format incorrecte a «{assumpte}»; la deixo per revisar")
            continue
        to, subj, text = m.group(1).strip("<>"), m.group(2).strip(), m.group(3).strip()
        text = re.split(r"\n\s*(?:On .+ wrote:|El .+ escribió:|El .+ va escriure:)", text)[0].strip()

        out = EmailMessage()
        out["From"] = formataddr((cfg["REMITENTE_NOMBRE"], cfg["EMAIL_USER"]))
        out["To"] = to
        out["Subject"] = subj
        if cfg.get("BCC_COPIA"):
            out["Bcc"] = cfg["BCC_COPIA"]
        out.set_content(text)
        try:
            with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg.get("SMTP_PORT", 587)), timeout=60) as s:
                s.starttls()
                s.login(cfg["EMAIL_USER"], cfg["EMAIL_PASS"])
                s.send_message(out)
            im.store(i, "+X-GM-LABELS", "\\Trash")
            enviats += 1
            print(f"✓ Resposta enviada a {to}: {subj}")
        except Exception as e:  # noqa
            print(f"! No s'ha pogut enviar a {to}: {e}")
    im.expunge()
    im.logout()
    print(f"✓ {enviats} respostes enviades")


if __name__ == "__main__":
    main()
