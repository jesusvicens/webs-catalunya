"""Textos de los emails (en catalán). Edítalos libremente.
Variables: {nombre} {nombre_corto} {municipio} {rating} {n_resenas} {motivo} {url} {precio} {precio_mes} {firma} {remitente}
"""

MOTIVOS = {
    "sin_web": "quan algú busca un taller a {municipio} a Google no troba cap web vostra",
    "web_caida": "la vostra web ara mateix no carrega",
    "no_movil": "la web no es veu bé al mòbil",
    "no_https": "el navegador la marca com a «no segura»",
    "lenta": "triga força a carregar",
    "abandonada": "la web té uns quants anys",
    "anticuada": "la web té uns quants anys",
}

ASUNTO = "Una web per a {nombre_corto}"

PASOS = [
    # Paso 0 · primer contacto
    """Hola,

Soc en {remitente}, faig webs per a negocis d'Osona. He vist que {nombre_corto} té {n_resenas} opinions a Google amb un {rating}, però {motivo}.

Us he preparat una proposta de web ja feta, amb les vostres dades, l'horari i opinions reals de clients:
{url}

Mireu-la des del mòbil, que és com la veuran els clients: botó per trucar, WhatsApp i com arribar.

Si us agrada, és vostra per {precio} € i {precio_mes} €/mes (domini, allotjament i canvis inclosos). La deixo funcionant en 48 hores.

Si no us interessa, responeu «no» i no us tornaré a escriure.

{firma}""",

    # Paso 1 · primer seguimiento
    """Hola de nou,

Només volia saber si heu pogut veure la proposta per a {nombre_corto}:
{url}

Si voleu canviar colors, textos o posar-hi fotos del taller, ho faig sense cost. Amb una trucada de 5 minuts ho deixem enllestit.

{firma}""",

    # Paso 2 · último
    """Hola,

Darrer correu, prometo. La proposta seguirà en línia uns dies més:
{url}

Si més endavant us interessa, només cal que respongueu aquest correu.

Gràcies i bona feina!
{firma}""",
]
