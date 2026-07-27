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
         "text": "Según las proyecciones de WARC Media, los ingresos publicitarios de Meta podrían alcanzar los 240.000 millones de dólares este año, un salto del 22,3% frente a 2025.",
         "fuente": "WARC Media / adobo Magazine", "url": "https://www.adobomagazine.com/insight/metas-ai-advertising-surge-set-to-hit-240-billion-in-2026-says-warc/"},
        {"num": "+33%", "title": "Gana más mostrando el mismo anuncio",
         "text": "En el primer trimestre de 2026 las impresiones publicitarias subieron 19% y, al mismo tiempo, el precio promedio por anuncio otro 12%: más volumen y más valor, a la vez.",
         "fuente": "MediaPost", "url": "https://www.mediapost.com/publications/article/415064/meta-expected-to-boost-advertising-by-22-in-2026.html"},
        {"num": "11.8M", "title": "Millones de marcas compiten por tu atención",
         "text": "Estimaciones de la industria sitúan en varios millones el número de anunciantes activos que hoy pujan dentro del ecosistema publicitario de Meta.",
         "fuente": "WARC Media / adobo Magazine", "url": "https://www.adobomagazine.com/insight/metas-ai-advertising-surge-set-to-hit-240-billion-in-2026-says-warc/"},
        {"num": "60/40", "title": "Facebook factura más, Instagram enamora más",
         "text": "Facebook concentra cerca del 60% de los ingresos publicitarios de Meta e Instagram el 40% restante, según WARC Media.",
         "fuente": "WARC Media / adobo Magazine", "url": "https://www.adobomagazine.com/insight/metas-ai-advertising-surge-set-to-hit-240-billion-in-2026-says-warc/"},
        {"num": "3.5B+", "title": "Más de 3.500 millones de personas al día",
         "text": "Meta reporta más de 3.500 millones de usuarios diarios combinados entre sus aplicaciones: Facebook, Instagram, WhatsApp y Messenger.",
         "fuente": "MarketingReport", "url": "https://marketingreport.one/news/meta-to-earn-240bn-from-advertising-in-2026.html"},
        {"num": "IA + Ads", "title": "El negocio de anuncios financia la carrera de IA",
         "text": "WARC Media describe un 'volante' donde los ingresos publicitarios financian la inversión en IA de Meta, que a su vez mejora el rendimiento de los anuncios y atrae más inversión publicitaria.",
         "fuente": "WARC Media / adobo Magazine", "url": "https://www.adobomagazine.com/insight/metas-ai-advertising-surge-set-to-hit-240-billion-in-2026-says-warc/"},
    ],
    "historia": [
        {"num": "2004", "title": "El primer anuncio de Facebook costaba 10 dólares al día",
         "text": "Corría 2004 y la red aún vivía dentro de Harvard. Los primeros anuncios se llamaban 'Flyers': banners simples para negocios locales.",
         "fuente": "Historia de Facebook — Wikipedia", "url": "https://en.wikipedia.org/wiki/History_of_Facebook"},
        {"num": "$5 ≈ 1.000", "title": "Con 5 dólares llegabas a mil personas",
         "text": "Cuando Facebook Ads se abrió al público en 2007, un presupuesto mínimo de apenas 5 dólares ya alcanzaba a cerca de 1.000 personas.",
         "fuente": "Historia de Facebook — Wikipedia", "url": "https://en.wikipedia.org/wiki/History_of_Facebook"},
        {"num": "2007–2009", "title": "Beacon: el experimento que casi hunde la confianza",
         "text": "En 2007 Facebook lanzó Beacon, un sistema que publicaba automáticamente las compras de los usuarios como anuncios frente a sus amigos. Cerró en 2009 tras una demanda colectiva por privacidad.",
         "fuente": "Wikipedia — Facebook Beacon", "url": "https://en.wikipedia.org/wiki/Facebook_Beacon"},
        {"num": "44% CTR", "title": "El primer banner de la historia tuvo un CTR del 44%",
         "text": "En 1994, AT&T pagó 30.000 dólares por el primer banner clicable de internet, publicado en HotWired.com. Obtuvo un 44% de clics — una cifra hoy prácticamente imposible.",
         "fuente": "Digiday", "url": "https://digiday.com/marketing/how-the-banner-ad-was-born/"},
        {"num": "2012", "title": "Nacen los Públicos Personalizados",
         "text": "En 2012 Facebook lanzó Custom Audiences, la función que permitió a las marcas subir sus propias bases de datos de clientes para encontrarlos en la plataforma.",
         "fuente": "Jon Loomer Digital", "url": "https://www.jonloomer.com/facebook-ads-custom-audiences-guide/"},
        {"num": "2004 → hoy", "title": "De banners universitarios a un imperio publicitario",
         "text": "Lo que empezó como anuncios locales para estudiantes de Harvard se convirtió, dos décadas después, en uno de los negocios publicitarios más grandes del mundo.",
         "fuente": "Historia de Facebook — Wikipedia", "url": "https://en.wikipedia.org/wiki/History_of_Facebook"},
    ],
    "algoritmo": [
        {"num": "25/semana", "title": "El umbral de conversiones bajó en 2026",
         "text": "Las actualizaciones de Advantage+ en 2026 redujeron el mínimo de eventos de conversión semanales necesarios de 50 a 25, haciendo que las campañas con IA sean accesibles para cuentas más pequeñas.",
         "fuente": "Benly", "url": "https://benly.ai/learn/meta-ads/advantage-plus-updates-2026"},
        {"num": "10.000x", "title": "El motor detrás del feed se llama Andromeda",
         "text": "Desde finales de 2024, Meta despliega 'Andromeda', un motor de recuperación de anuncios con 10.000 veces más capacidad de modelo que su predecesor. Para 2026 corre en la totalidad de las cuentas de Facebook e Instagram.",
         "fuente": "Common Thread Collective", "url": "https://commonthreadco.com/blogs/coachs-corner/meta-andromeda-roas-creative-strategy-2026"},
        {"num": "3–8seg", "title": "El gancho se decide en los primeros segundos",
         "text": "Bajo el sistema actual, el 'hook rate' —el porcentaje de personas que sigue viendo un video pasados los primeros segundos— es el indicador que más predice si un anuncio en video va a funcionar.",
         "fuente": "The Interconnections", "url": "https://www.theinterconnections.com/blog/meta-ads-2026"},
        {"num": "Advantage+", "title": "La automatización dejó de ser opcional",
         "text": "Cada vez más anunciantes delegan la segmentación, el presupuesto y hasta la creatividad de sus campañas a los sistemas automatizados de Meta, en vez de configurarlos manualmente.",
         "fuente": "AdAmigo", "url": "https://www.adamigo.ai/blog/meta-ads-roas-benchmarks-by-industry-2026"},
        {"num": "IA generativa", "title": "El algoritmo también genera los anuncios",
         "text": "Las herramientas de generación de imagen y texto integradas en Meta Ads permiten crear variaciones de un mismo anuncio automáticamente, algo impensado hace pocos años."},
    ],
    "curiosidades": [
        {"num": "$125–145B", "title": "Invierte en IA más que el PIB de países enteros",
         "text": "Meta anunció planes para destinar entre 125.000 y 145.000 millones de dólares a infraestructura de inteligencia artificial: la misma tecnología que hoy decide qué anuncio ves.",
         "fuente": "MediaNews4u", "url": "https://www.medianews4u.com/meta-to-earn-240bn-from-advertising-in-2026-outpacing-global-social-media-ad-growth-warc/"},
        {"num": "4.52x vs 3.70x", "title": "Las campañas automáticas rinden ~22% más",
         "text": "Las campañas Advantage+ Shopping promedian un ROAS de 4.52x frente a 3.70x de las campañas manuales equivalentes, según benchmarks de la industria en 2026.",
         "fuente": "AdAmigo", "url": "https://www.adamigo.ai/blog/meta-ads-roas-benchmarks-by-industry-2026"},
        {"num": "1994", "title": "Todo empezó con un banner de 30.000 dólares",
         "text": "El primer banner publicitario de internet se publicó el 27 de octubre de 1994 en HotWired.com — tres años antes de que naciera el concepto moderno de red social.",
         "fuente": "Digiday", "url": "https://digiday.com/marketing/how-the-banner-ad-was-born/"},
        {"num": "∞ variantes", "title": "Un anuncio nunca se ve igual dos veces",
         "text": "El mismo anuncio puede mostrarse con textos, imágenes o llamados a la acción distintos a cada persona, combinados automáticamente por el sistema para maximizar resultados."},
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
    "El primer banner de internet (1994) tuvo un <b>44% de clics</b>",
    "Facebook representa el <b>60%</b> de los ingresos de Meta, Instagram el 40%",
    "Con <b>$5</b> alcanzabas 1.000 personas en el Facebook de 2007",
    "Andromeda, el motor de anuncios de Meta, tiene <b>10.000x</b> más capacidad",
    "Advantage+ Shopping promedia <b>22% más ROAS</b> que las campañas manuales",
    "Meta invierte hasta <b>$145.000M</b> en infraestructura de IA",
    "Más de <b>3.500M</b> de personas usan una app de Meta cada día",
    "En 2012 nacieron los Públicos Personalizados en Facebook Ads",
    "El umbral de conversiones de Advantage+ bajó de 50 a <b>25 por semana</b> en 2026",
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
