# Webs para talleres de Osona — sistema automático

Busca talleres en Google Maps → descarta los que ya tienen buena web → genera una web personalizada para cada uno → la publica → envía email + 2 seguimientos → detecta quién responde.

```
1_buscar.py    Google Maps (Outscraper): nombre, teléfono, email, web, horario, rating
2_filtrar.py   audita su web (móvil, https, velocidad, antigüedad) y baja 3 reseñas de 5★
3_generar.py   plantilla/taller.html → salida/sites/<slug>/index.html (+ captura móvil)
4_publicar.py  sube todas las demos a Netlify → demos.tudominio.com/<slug>/
5_enviar.py    email inicial + seguimientos a los 4 y 10 días; para si responden o rebota
pipeline.py    lo ejecuta todo
mensajes.py    textos de los emails (catalán) — edítalos
datos/leads.csv  tu "CRM": estado de cada taller (ábrelo en Excel)
```

## Puesta en marcha (una vez, ~1 hora)

1. **Python 3.10+** y dependencias:
   ```
   pip install requests jinja2 playwright
   python -m playwright install chromium
   ```
2. **Outscraper** (outscraper.com): crea cuenta, añade 10–20 $ y copia la API key.
   Osona entera son ~150–250 talleres → unos pocos dólares.
3. **Dominio para las demos y el correo** (p. ej. `websosona.cat`, ~10 €/año). No uses el de teamOn.
   - **Correo**: Google Workspace o Zoho Mail en ese dominio. Configura SPF, DKIM y DMARC (el panel te guía).
     Crea una contraseña de aplicación y ponla en `EMAIL_PASS`.
   - **Calentamiento**: un dominio nuevo que manda 25 emails el primer día acaba en spam.
     Semana 1: `MAX_ENVIOS_DIA=8`, semana 2: 15, luego 25.
4. **Netlify** (gratis): *Add new site → Deploy manually* (arrastra cualquier carpeta). En *Site configuration* copia el **Site ID**.
   En *Domain management* añade `demos.websosona.cat`. Crea un token en *User settings → Applications*.
5. `cp config.env.example config.env` y rellénalo.

## Uso

```
python pipeline.py preparar          # busca, filtra, genera y publica
python 5_enviar.py --prueba tu@gmail.com   # te mandas los 3 emails para revisarlos
python 5_enviar.py                   # simulación: ves exactamente qué se enviaría
python 5_enviar.py --real            # envía
```

**Automatizarlo cada día** (ordenador encendido a esa hora):
- Mac/Linux: `crontab -e` → `30 9 * * 1-5 cd /ruta/webs-osona && python3 5_enviar.py --real >> envios.log 2>&1`
- Windows: Programador de tareas → diaria, L–V 9:30 → `python 5_enviar.py --real` con "Iniciar en" = la carpeta.

Con 25/día tardarás ~1 semana en cubrir Osona; los seguimientos salen solos.

## Modo 100 % delegado (Claude lleva las respuestas) — coste 0

**Cuentas**: todo sale de **webscatalunya@gmail.com** (Gmail gratuito). Claude lee las conversaciones en
jesusvicens8@gmail.com, pero nunca escribe a un taller desde ahí: redacta la respuesta y se la pasa a
`7_relay.py`, que la envía desde webscatalunya.

Configurar una vez:
1. **webscatalunya@gmail.com**: verificación en 2 pasos → contraseña de aplicación → `EMAIL_PASS`.
   Ajustes → Reenvío y POP/IMAP → *Añadir dirección de reenvío* → jesusvicens8@gmail.com
   (confirma el código) → «Reenviar una copia… y conservar la copia en la bandeja de entrada». IMAP activado.
2. **Netlify** (gratis): crea un sitio vacío llamado `websosona` → `NETLIFY_SITE_ID` y token.
3. **Stripe** (sin cuota fija, solo comisión por cobro): Payment Link con 390 € (pago único) + 29 €/mes,
   y una clave restringida con lectura de Checkout Sessions → `STRIPE_SECRET_KEY`. Pásame la URL del enlace.
4. **Cron** (ordenador encendido en horario laboral):
   ```
   35 9 * * 1-5      cd /ruta/webs-osona && python3 pipeline.py enviar --real >> envios.log 2>&1
   */15 9-19 * * 1-5 cd /ruta/webs-osona && python3 7_relay.py >> relay.log 2>&1
   ```
   Windows: dos tareas en el Programador de tareas con esos comandos.

La tarea programada de Claude (9:47 y 14:47, L–V) contesta según el guion, envía el enlace de pago,
recuerda, etiqueta en Gmail (`Webs/…`) y te avisa al móvil y por email solo de lo que necesita tu mano.

**Cuando un cliente paga**: `6_entregar.py` (dentro del cron) publica su web final y le manda el enlace.
**Dominio propio del cliente**: `python 6_entregar.py --dominio <slug> sudominio.cat` y cambia en su
registrador solo los registros A (@ → 75.2.60.5) y CNAME (www → su-sitio.netlify.app). Los MX (correo) NO se tocan,
y que no dé de baja su hosting antiguo hasta saber si su correo va con él.
**Cambios que pidan**: pídemelos en un chat y luego `python 6_entregar.py --actualitzar <slug>`.

## Cuando alguien responde

El script lo marca `respondido` y deja de escribirle. Tú:
1. Llama (más rápido que el email). Apunta cambios: fotos del taller, servicios, color.
2. Cobra: enlace de pago de Stripe con pago único + suscripción mensual.
3. `python 3_generar.py --final <slug>` → versión sin la franja de "proposta".
4. Nuevo sitio en Netlify con esa carpeta + su dominio (o compra uno a su nombre).
5. Pon `"estado": "cliente"` en `datos/leads.json`.

Los `solo_telefono` (taller sin email) también tienen demo y captura `movil.png`: llámalos o mándales la captura por WhatsApp.

## Otros sectores

Copia `plantilla/taller.html`, cambia `CONSULTAS`/`CATEGORIAS_OK` en `comun.py` y `SERVICIOS`/`TITULARES` en `3_generar.py`.

## Ojo

- La LSSI prohíbe en España el email comercial sin consentimiento previo. El riesgo es tuyo; el volumen bajo y personalizado,
  la línea de baja y no reenviar nunca a quien dice "no" lo reducen, pero no lo eliminan.
- Las demos usan reseñas públicas de Google y llevan `noindex` y la franja "Proposta de disseny": no se presentan como su web oficial.
