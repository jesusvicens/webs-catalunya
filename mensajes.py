"""Textos de los emails (en catalán). Edítalos libremente.
Variables: {nombre} {nombre_corto} {municipio} {rating} {n_resenas} {motivo} {url} {precio} {precio_mes} {firma} {remitente}
"""

MOTIVOS = {
    "sin_web": "quan algú busca {cerca} a {municipio} a Google no troba cap web vostra",
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

Soc en {remitente}, faig webs per a negocis {de_zona}. {intro}

Us he preparat una proposta de web ja feta, amb les vostres dades i el vostre horari:
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


CERCA = {"taller": "un taller", "lampista": "un lampista", "electricista": "un electricista",
         "reformes": "una empresa de reformes", "pintor": "un pintor", "fuster": "un fuster"}

# "negocis <DE_COMARCA>"
DE_COMARCA = {
    "Alt Camp": "de l'Alt Camp", "Alt Empordà": "de l'Alt Empordà", "Alt Penedès": "de l'Alt Penedès",
    "Alt Urgell": "de l'Alt Urgell", "Alta Ribagorça": "de l'Alta Ribagorça", "Anoia": "de l'Anoia",
    "Bages": "del Bages", "Baix Camp": "del Baix Camp", "Baix Ebre": "del Baix Ebre", "Baix Empordà": "del Baix Empordà",
    "Baix Llobregat": "del Baix Llobregat", "Baix Penedès": "del Baix Penedès", "Barcelonès": "del Barcelonès",
    "Berguedà": "del Berguedà", "Cerdanya": "de la Cerdanya", "Conca de Barberà": "de la Conca de Barberà",
    "Garraf": "del Garraf", "Garrigues": "de les Garrigues", "Garrotxa": "de la Garrotxa", "Gironès": "del Gironès",
    "Lluçanès": "del Lluçanès", "Maresme": "del Maresme", "Moianès": "del Moianès", "Montsià": "del Montsià",
    "Noguera": "de la Noguera", "Osona": "d'Osona", "Pallars Jussà": "del Pallars Jussà",
    "Pallars Sobirà": "del Pallars Sobirà", "Pla d'Urgell": "del Pla d'Urgell", "Pla de l'Estany": "del Pla de l'Estany",
    "Priorat": "del Priorat", "Ribera d'Ebre": "de la Ribera d'Ebre", "Ripollès": "del Ripollès", "Segarra": "de la Segarra",
    "Segrià": "del Segrià", "Selva": "de la Selva", "Solsonès": "del Solsonès", "Tarragonès": "del Tarragonès",
    "Terra Alta": "de la Terra Alta", "Urgell": "de l'Urgell", "Val d'Aran": "de la Val d'Aran",
    "Vallès Occidental": "del Vallès Occidental", "Vallès Oriental": "del Vallès Oriental",
}
