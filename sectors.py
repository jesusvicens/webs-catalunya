"""Textos de la web segons el sector del negoci. Cada lead té el camp 'sector' (per defecte 'taller')."""
from markupsafe import Markup


def _svg(path):
    return Markup('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                  f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>')


I_EINA = _svg('<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>')
I_CHECK = _svg('<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>')
I_ESCUT = _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>')
I_GOTA = _svg('<path d="M12 2.7s6 6.6 6 11.3a6 6 0 0 1-12 0c0-4.7 6-11.3 6-11.3z"/>')
I_LLAMP = _svg('<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>')
I_CASA = _svg('<path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>')
I_PINZELL = _svg('<path d="M18 3l3 3-9 9-3-3z"/><path d="M9 12l-4 1-2 6 6-2 1-4"/>')
I_FOC = _svg('<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-9-1 2-2 3-3 3 0-2-1-4-3-6 0 4-4 6-4 12a7 7 0 0 0 7 7z"/>')
I_SOL = _svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>')
I_REGLE = _svg('<path d="M3 17 17 3l4 4L7 21z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>')
I_CLAU = _svg('<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.3-9.3M17 6l3 3M14 9l2 2"/>')
I_PANTALLA = _svg('<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M6 14l3-4 3 3 3-5 3 6"/><path d="M8 22h8"/>')

PASSOS_OFICI = [
    ("Truca'ns o escriu-nos", "Explica'ns què necessites i quedem per venir a veure-ho."),
    ("Visita i pressupost", "Ho mirem al lloc i et donem un pressupost clar i per escrit. Tu decideixes."),
    ("Feina feta i neta", "Fem la feina en el termini acordat i ho deixem tot net i recollit."),
]

SECTORS = {
    "taller": {
        "tipus": "Taller mecànic",
        "schema": "AutoRepair",
        "sub": "Taller mecànic a {muni}. Revisions, reparacions i manteniment de totes les marques, amb pressupost clar abans de començar.",
        "titulars": [("El teu cotxe,", "en bones mans"), ("Mecànica", "de confiança"), ("Reparem.", "Sense sorpreses."), ("Taller de", "tota la vida")],
        "wa": "Hola! Voldria demanar cita al taller.",
        "slip": {"label": "Ordre de treball", "titol": "Revisió completa", "placa": "1234 KLM", "segell": "Revisat",
                 "passes": [("Diagnosi amb màquina", "fet"), ("Pressupost acceptat pel client", "ok!"), ("Reparació i recanvis", "fet"), ("Prova i lliurament", "a punt")]},
        "banda": "Totes les marques",
        "intro_serveis": "Treballem amb totes les marques i t'expliquem què cal fer —i quant costa— abans de tocar res.",
        "passos": [("Truca'ns o escriu-nos", "Explica'ns què li passa al cotxe i et donem dia i hora."),
                   ("Diagnosi i pressupost", "Revisem el cotxe i t'expliquem l'avaria i el preu. Tu decideixes."),
                   ("Recull-lo a punt", "Et truquem quan està llest, amb la feina feta tal com s'havia acordat.")],
        "contacte": ("On som", "Vine a veure'ns"),
        "serveis": [
            ("Mecànica general", "Motor, embragatge, distribució, suspensió i tot el que faci falta perquè el cotxe vagi fi.", I_EINA),
            ("Revisions i manteniment", "Canvi d'oli i filtres segons el pla del fabricant, sense perdre la garantia.", I_CHECK),
            ("Pre-ITV", "Revisem el cotxe abans de la ITV perquè la passis a la primera.", I_ESCUT),
            ("Frens i pneumàtics", "Pastilles, discos, alineació i pneumàtics de totes les mides.", I_EINA),
            ("Diagnosi electrònica", "Llegim les avaries amb màquina i et diem exactament què passa.", I_PANTALLA),
            ("Aire condicionat", "Càrrega de gas, revisió de fuites i neteja del circuit.", I_SOL),
        ],
    },
    "lampista": {
        "tipus": "Lampisteria",
        "schema": "Plumber",
        "sub": "Lampistes a {muni} i rodalia. Aigua, calefacció i gas, reparacions urgents i instal·lacions noves, amb pressupost clar abans de començar.",
        "titulars": [("Lampistes", "de confiança"), ("Una fuita?", "Hi som avui."), ("Aigua, gas", "i calefacció"), ("Ben fet", "i a la primera")],
        "wa": "Hola! Voldria demanar pressupost.",
        "slip": {"label": "Full de feina", "titol": "Reparació de fuita", "placa": "Urgent", "segell": "Fet",
                 "passes": [("Visita i diagnòstic", "fet"), ("Pressupost acceptat", "ok!"), ("Canvi de canonada i aixeta", "fet"), ("Prova de pressió", "a punt")]},
        "banda": "Urgències",
        "intro_serveis": "Des d'una aixeta que goteja fins a una instal·lació sencera. Et diem què cal fer i quant costa abans de començar.",
        "passos": PASSOS_OFICI,
        "contacte": ("Contacte", "Parlem-ne"),
        "serveis": [
            ("Fuites i avaries", "Localitzem i reparem fuites, embussos i avaries, també urgents.", I_GOTA),
            ("Calderes i calefacció", "Instal·lació, revisió i reparació de calderes, radiadors i terra radiant.", I_FOC),
            ("Banys i cuines", "Canvi de banyera per plat de dutxa, sanitaris, aixetes i desguassos.", I_CASA),
            ("Gas", "Instal·lacions i revisions de gas amb el butlletí corresponent.", I_ESCUT),
            ("Aigua calenta", "Termos, escalfadors i aerotèrmia: t'aconsellem el que et convé.", I_SOL),
            ("Manteniment", "Revisions periòdiques per a comunitats, comerços i habitatges.", I_CHECK),
        ],
    },
    "electricista": {
        "tipus": "Electricista",
        "schema": "Electrician",
        "sub": "Electricistes a {muni} i rodalia. Avaries, instal·lacions i butlletins, amb pressupost clar abans de començar.",
        "titulars": [("Llum on", "la necessites"), ("Electricistes", "de confiança"), ("Avaries", "resoltes avui"), ("Instal·lacions", "ben fetes")],
        "wa": "Hola! Voldria demanar pressupost.",
        "slip": {"label": "Full de feina", "titol": "Quadre elèctric nou", "placa": "Butlletí", "segell": "Fet",
                 "passes": [("Visita i revisió", "fet"), ("Pressupost acceptat", "ok!"), ("Canvi de quadre i diferencials", "fet"), ("Proves i butlletí", "a punt")]},
        "banda": "Butlletins",
        "intro_serveis": "Petites avaries o instal·lacions completes, per a casa, comerços i comunitats. Et diem què cal fer i quant costa abans de començar.",
        "passos": PASSOS_OFICI,
        "contacte": ("Contacte", "Parlem-ne"),
        "serveis": [
            ("Avaries", "Salten els ploms? Ho trobem i ho arreglem, també urgent.", I_LLAMP),
            ("Instal·lacions", "Instal·lacions noves i reformes elèctriques completes.", I_EINA),
            ("Butlletins i certificats", "Butlletins per a alta de llum, canvis de potència i inspeccions.", I_ESCUT),
            ("Plaques solars", "Autoconsum fotovoltaic: estudi, instal·lació i tràmits.", I_SOL),
            ("Il·luminació LED", "Canviem l'enllumenat per estalviar a la factura.", I_LLAMP),
            ("Comerços i comunitats", "Manteniment elèctric per a negocis i escales de veïns.", I_CHECK),
        ],
    },
    "reformes": {
        "tipus": "Reformes",
        "schema": "GeneralContractor",
        "sub": "Reformes a {muni} i rodalia. Cuines, banys i pisos sencers, amb pressupost tancat i terminis clars.",
        "titulars": [("Reformes", "sense maldecaps"), ("La teva casa,", "com la vols"), ("Cuines i banys", "a punt"), ("Pressupost tancat,", "feina ben feta")],
        "wa": "Hola! Voldria demanar pressupost per a una reforma.",
        "slip": {"label": "Full d'obra", "titol": "Reforma de bany", "placa": "3 setmanes", "segell": "Acabat",
                 "passes": [("Visita i mesures", "fet"), ("Pressupost tancat acceptat", "ok!"), ("Enderroc, paleta i lampisteria", "fet"), ("Acabats i neteja", "a punt")]},
        "banda": "Pressupost tancat",
        "intro_serveis": "Ens encarreguem de tot, de l'enderroc a la neteja final, amb un sol interlocutor i un pressupost tancat.",
        "passos": [("Truca'ns o escriu-nos", "Explica'ns què vols fer i quedem per venir a veure-ho."),
                   ("Pressupost tancat", "Et fem un pressupost detallat i per escrit, amb terminis. Tu decideixes."),
                   ("Obra acabada", "Complim els terminis i et lliurem l'obra neta i a punt per fer-hi vida.")],
        "contacte": ("Contacte", "Parlem del teu projecte"),
        "serveis": [
            ("Cuines", "Cuines noves o reformades, amb mobles, encimera i instal·lacions.", I_CASA),
            ("Banys", "Canvi de banyera per plat de dutxa, rajoles, sanitaris i mobles.", I_GOTA),
            ("Pisos sencers", "Reformes integrals amb distribució nova i totes les instal·lacions.", I_REGLE),
            ("Paleteria", "Envans, regates, enrajolats i petites obres.", I_EINA),
            ("Façanes i teulades", "Rehabilitació, impermeabilització i reparació de goteres.", I_ESCUT),
            ("Locals comercials", "Adaptem el teu local perquè puguis obrir com més aviat millor.", I_CHECK),
        ],
    },
    "pintor": {
        "tipus": "Pintor",
        "schema": "HousePainter",
        "sub": "Pintors a {muni} i rodalia. Pisos, cases, façanes i locals, nets i en el termini acordat.",
        "titulars": [("Pintem", "sense embrutar"), ("La teva casa,", "com nova"), ("Color", "i feina neta"), ("Pintors", "de confiança")],
        "wa": "Hola! Voldria demanar pressupost de pintura.",
        "slip": {"label": "Full de feina", "titol": "Pintar pis de 80 m²", "placa": "2 dies", "segell": "Fet",
                 "passes": [("Protegir mobles i terres", "fet"), ("Tapar forats i esquerdes", "fet"), ("Dues mans de pintura", "fet"), ("Neteja final", "a punt")]},
        "banda": "Feina neta",
        "intro_serveis": "Interiors i exteriors, amb pintures de qualitat i tot protegit. Et diem quant costa abans de començar.",
        "passos": PASSOS_OFICI,
        "contacte": ("Contacte", "Parlem-ne"),
        "serveis": [
            ("Pisos i cases", "Parets i sostres, amb protecció de mobles i terres.", I_PINZELL),
            ("Façanes", "Pintura i rehabilitació de façanes amb materials per a exterior.", I_CASA),
            ("Gotelé fora", "Eliminem el gotelé i deixem les parets llises.", I_REGLE),
            ("Fusta i ferro", "Portes, finestres, baranes i reixes com noves.", I_EINA),
            ("Humitats", "Tractem les humitats i la floridura abans de pintar.", I_GOTA),
            ("Locals i comunitats", "Escales de veïns, oficines i comerços, també en caps de setmana.", I_CHECK),
        ],
    },
    "fuster": {
        "tipus": "Fusteria",
        "schema": "HomeAndConstructionBusiness",
        "sub": "Fusteria a {muni}. Mobles a mida, portes, armaris i cuines, fets aquí i ben acabats.",
        "titulars": [("Fusta,", "feta a mida"), ("Mobles", "que duren"), ("Fusteria", "de tota la vida"), ("Ho fem", "a la teva mida")],
        "wa": "Hola! Voldria demanar pressupost.",
        "slip": {"label": "Encàrrec", "titol": "Armari encastat", "placa": "A mida", "segell": "Fet",
                 "passes": [("Prendre mides", "fet"), ("Disseny i pressupost", "ok!"), ("Fabricació al taller", "fet"), ("Muntatge a casa", "a punt")]},
        "banda": "Fet a mida",
        "intro_serveis": "Dissenyem, fabriquem i muntem. T'ensenyem el disseny i el preu abans de començar.",
        "passos": PASSOS_OFICI,
        "contacte": ("On som", "Vine al taller"),
        "serveis": [
            ("Armaris encastats", "Aprofitem cada racó amb armaris fets a mida.", I_REGLE),
            ("Cuines", "Cuines de fusta a mida, de disseny o rústiques.", I_CASA),
            ("Portes i finestres", "Portes d'interior i d'entrada, finestres i porticons.", I_EINA),
            ("Mobles a mida", "Prestatgeries, taules, llits i mobles per a negocis.", I_REGLE),
            ("Parquet i tarimes", "Col·locació, polit i envernissat de terres de fusta.", I_PINZELL),
            ("Restauració", "Recuperem mobles i portes antigues.", I_CHECK),
        ],
    },
}

# Paraules de la categoria/cerca de Google → sector
DETECCIO = [
    ("lampista", ["lampist", "fontaner", "fontaner", "plumb", "fontaner", "calefacci", "caldera"]),
    ("electricista", ["electric", "elèctric", "eléctric"]),
    ("reformes", ["reform", "contractor", "construcc", "construcci", "paleta", "albañil", "obras"]),
    ("pintor", ["pintor", "painter", "pintura"]),
    ("fuster", ["fuster", "carpinter", "ebanist", "carpenter"]),
    ("taller", ["taller", "mecàn", "mecán", "car repair", "auto repair", "mechanic"]),
]


def detectar(*textos):
    t = " ".join(x or "" for x in textos).lower()
    for sector, paraules in DETECCIO:
        if any(p in t for p in paraules):
            return sector
    return None
