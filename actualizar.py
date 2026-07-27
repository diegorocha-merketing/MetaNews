#!/usr/bin/env python3
"""
Actualiza contenido.json para el sitio SPONSORED.
- Rota diariamente una selección del banco curado de datos (cifras, historia,
  algoritmo, curiosidades, memes) usando el día del año como semilla, así
  el contenido cambia cada día pero se mantiene estable durante ese día.
- Descarga titulares reales y recientes sobre "Meta Ads" desde Google News RSS
  (gratis, sin necesidad de API key) para la sección "Últimas noticias".
- Si la descarga de noticias falla (sin internet, cambios en el feed, etc.),
  el script no se cae: simplemente deja esa sección vacía por ese día.
"""

import json
import random
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BANCO = {
    "cifras": [
        {"num": "$240B", "title": "Meta apunta a 240.000 millones de dólares en 2026",
         "text": "Según las proyecciones de WARC Media, los ingresos publicitarios de Meta podrían alcanzar los 240.000 millones de dólares este año, un salto del 22,3% frente a 2025."},
        {"num": "+33%", "title": "Gana más mostrando el mismo anuncio",
         "text": "En el primer trimestre de 2026 las impresiones publicitarias subieron 19% y, al mismo tiempo, el precio promedio por anuncio otro 12%: más volumen y más valor, a la vez."},
        {"num": "11.8M", "title": "11,8 millones de marcas compiten por tu atención",
         "text": "Ese es el número estimado de anunciantes activos que hoy pujan dentro del ecosistema publicitario de Meta, según benchmarks de industria de 2026."},
        {"num": "60/40", "title": "Facebook factura más, Instagram enamora más",
         "text": "Facebook concentra cerca del 60% de los ingresos publicitarios de Meta e Instagram el 40% restante. Aun así, más marketers planean subir su inversión en Instagram este año."},
        {"num": "3.58B", "title": "3.580 millones de personas al día",
         "text": "Ese es el número de personas que, en promedio, usan a diario alguna app de la familia Meta: Facebook, Instagram, WhatsApp y Messenger."},
        {"num": "↑ video", "title": "El video sigue ganando terreno",
         "text": "Los formatos de video como Reels e historias concentran una porción creciente de la inversión publicitaria dentro de Meta, según reportes de industria de 2026."},
    ],
    "historia": [
        {"num": "2004", "title": "El primer anuncio de Facebook costaba 10 dólares al día",
         "text": "Corría 2004 y la red aún vivía dentro de Harvard. Los primeros anuncios se llamaban 'Flyers': banners simples para negocios locales."},
        {"num": "$5 ≈ 1.000", "title": "Con 5 dólares llegabas a mil personas",
         "text": "Cuando Facebook Ads se abrió al público en 2007, un presupuesto mínimo de apenas 5 dólares ya alcanzaba a cerca de 1.000 personas."},
        {"num": "2007–2009", "title": "Beacon: el experimento que casi hunde la confianza",
         "text": "En 2007 Facebook lanzó Beacon, un sistema que publicaba automáticamente las compras de los usuarios como anuncios frente a sus amigos. Cerró en 2009 tras la polémica."},
        {"num": "78% CTR", "title": "El primer banner de la historia tuvo un CTR del 78%",
         "text": "En 1994, AT&T pagó por el primer banner clicable de internet, publicado en HotWired.com — una cifra hoy prácticamente imposible."},
        {"num": "2012", "title": "Nacen los Públicos Personalizados",
         "text": "En 2012 Facebook lanzó Custom Audiences, la función que permitió a las marcas subir sus propias bases de datos de clientes para encontrarlos en la plataforma."},
        {"num": "2004 → hoy", "title": "De banners universitarios a un imperio publicitario",
         "text": "Lo que empezó como anuncios locales para estudiantes de Harvard se convirtió, dos décadas después, en uno de los negocios publicitarios más grandes del mundo."},
    ],
    "algoritmo": [
        {"num": "+40% CPM", "title": "Dejó de mirar clics para predecir el futuro",
         "text": "Desde marzo de 2026, el sistema de Meta ya no optimiza solo por clics: intenta predecir qué usuarios convertirán más adelante. Cuentas con pocos eventos de conversión pueden pagar hasta 40% más."},
        {"num": "Views", "title": "Dos métricas se volvieron una sola",
         "text": "En 2026 la plataforma unificó 'impresiones' y 'reproducciones de video' en un único indicador llamado Views."},
        {"num": "85%", "title": "8 de cada 10 personas ven video sin sonido",
         "text": "Por eso los anuncios que mejor funcionan dependen de subtítulos y un gancho visual en los primeros segundos, no del audio."},
        {"num": "Advantage+", "title": "La automatización dejó de ser opcional",
         "text": "Cada vez más anunciantes delegan la segmentación, el presupuesto y hasta el diseño de sus anuncios a los sistemas automatizados de Meta."},
        {"num": "IA generativa", "title": "El algoritmo también genera los anuncios",
         "text": "Las herramientas de generación de imagen y texto integradas en Meta Ads permiten crear variaciones de un mismo anuncio automáticamente."},
    ],
    "curiosidades": [
        {"num": "$125–145B", "title": "Invierte en IA más que el PIB de países enteros",
         "text": "Meta destinó entre 125.000 y 145.000 millones de dólares a infraestructura de inteligencia artificial en 2026."},
        {"num": "+41% ROAS", "title": "Las campañas automáticas mejoraron el retorno 41%",
         "text": "Los anunciantes que usan Advantage+ reportan hasta 41% más retorno sobre la inversión y 17% menos costo de adquisición de clientes."},
        {"num": "1994", "title": "Todo empezó con un banner",
         "text": "El primer anuncio digital de la historia se publicó en 1994, tres años antes de que naciera el concepto moderno de red social."},
        {"num": "∞ variantes", "title": "Un anuncio nunca se ve igual dos veces",
         "text": "El mismo anuncio puede mostrarse con textos, imágenes o llamados a la acción distintos a cada persona, combinados automáticamente por el sistema."},
    ],
}

MEMES = [
    {"top": "Yo subiendo el presupuesto $10 al día", "emoji": "📈", "badge": "CPM +37%",
     "bottom": "El CPM: \"gracias por el aumento\"", "art": "a"},
    {"top": "El cliente: \"¿por qué el anuncio no vende?\"", "emoji": "🧠", "badge": "FASE DE APRENDIZAJE",
     "bottom": "Yo: \"el algoritmo todavía está aprendiendo\"", "art": "b"},
    {"top": "Encuentras el anuncio ganador", "emoji": "🔁", "badge": "DUPLICAR",
     "bottom": "Lo duplicas 6 veces antes de dormir", "art": "c"},
    {"top": "Meta lanza una actualización sin avisar", "emoji": "🌀", "badge": "LUNES 8:00 AM",
     "bottom": "Todo el equipo de Ads, a la vez", "art": "a"},
    {"top": "Advantage+ optimizando la campaña", "emoji": "🤖", "badge": "AUTO-PILOTO",
     "bottom": "Yo, sin tocar nada, mirando el ROAS subir", "art": "b"},
    {"top": "Día 1 del mes: el CPM despierta", "emoji": "☕", "badge": "PRESUPUESTO",
     "bottom": "Y decide subir \"porque sí\"", "art": "c"},
]

TICKER_BASE = [
    "Meta proyecta <b>$240.000M</b> en ingresos publicitarios para 2026",
    "El primer banner de internet (1994) tuvo un <b>78% de clics</b>",
    "<b>11.8M</b> anunciantes activos compiten hoy en Meta Ads",
    "Con <b>$5</b> alcanzabas 1.000 personas en el Facebook de 2007",
    "El algoritmo ahora predice conversiones, no solo clics",
    "<b>85%</b> de las personas ve video sin sonido",
    "Meta invierte hasta <b>$145.000M</b> en infraestructura de IA",
    "Advantage+ mejora el ROAS hasta un <b>41%</b>",
    "<b>3.580M</b> de personas usan una app de Meta cada día",
    "En 2012 nacieron los Públicos Personalizados en Facebook Ads",
]


def elegir_diario(lista, cantidad):
    """Elige `cantidad` elementos de `lista`, distinto cada día del año pero
    estable durante ese mismo día (útil para que no cambie a cada rato)."""
    hoy = datetime.now(timezone.utc).timetuple().tm_yday
    rng = random.Random(hoy)
    copia = lista[:]
    rng.shuffle(copia)
    return copia[:cantidad]


def obtener_noticias(consulta="Meta Ads", maximo=5):
    """Trae titulares recientes desde Google News RSS. Gratis, sin API key.
    Si algo falla, retorna lista vacía (el sitio sigue funcionando igual)."""
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(consulta)
        + "&hl=es-419&gl=CO&ceid=CO:es-419"
    )
    noticias = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        for item in root.findall(".//item")[:maximo]:
            titulo = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            fuente_el = item.find("source")
            fuente = (fuente_el.text or "Google News").strip() if fuente_el is not None else "Google News"
            if titulo and link:
                noticias.append({"titulo": titulo, "link": link, "fuente": fuente})
    except Exception as e:
        print(f"Aviso: no se pudieron obtener noticias en vivo ({e}). Se deja la sección vacía por hoy.")
    return noticias


def main():
    contenido = {
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "ticker": elegir_diario(TICKER_BASE, 8),
        "cifras": elegir_diario(BANCO["cifras"], 4),
        "historia": elegir_diario(BANCO["historia"], 4),
        "algoritmo": elegir_diario(BANCO["algoritmo"], 3),
        "curiosidades": elegir_diario(BANCO["curiosidades"], 3),
        "memes": elegir_diario(MEMES, 6),
        "noticias": obtener_noticias(),
    }

    with open("contenido.json", "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=2)

    print("contenido.json actualizado correctamente.")
    print(f"Noticias encontradas hoy: {len(contenido['noticias'])}")


if __name__ == "__main__":
    main()
