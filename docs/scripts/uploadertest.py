import os
import json
from datetime import datetime
# Librerías externas
import requests
from pytrends.request import TrendReq  # Para obtener tendencias de Google Trends
from dotenv import load_dotenv         # Para leer variables de entorno desde .env
import firebase_admin                  # SDK de Firebase para Python
from firebase_admin import credentials, firestore
from openai import OpenAI              # Cliente compatible con OpenAI API (también funciona con router de Hugging Face)

# Cargar variables de entorno del archivo .env
load_dotenv()

# Inicializar Firebase con credenciales JSON
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS")  # Ruta al archivo JSON de Firebase
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)

# Crear cliente Firestore
db = firestore.client()

# Inicializar pytrends (Google Trends)
pytrends = TrendReq(hl='en-US', tz=360)

# Consultar tendencias relacionadas con "news"
pytrends.build_payload(["news"], cat=0, timeframe='now 1-d', geo='US')
related_queries = pytrends.related_queries()

# Obtener el top de temas relacionados
top_queries = related_queries.get("news", {}).get("top", None)
if top_queries is not None:
    trending_topics = top_queries["query"].tolist()
else:
    trending_topics = ["No trending topics found"]

print("Temas en tendencia:", trending_topics)

# Inicializar cliente OpenAI apuntando al router de Hugging Face
client = OpenAI(
    base_url="https://router.huggingface.co/v1",   # Esto hace que OpenAI use modelos de Hugging Face
    api_key=os.getenv("HUGGINGFACE_TOKEN"),        # Tu token de Hugging Face (necesario para acceso)
)

def generate_article(topic):
    """
    Genera un artículo breve sobre el tema usando el modelo 'moonshotai/Kimi-K2-Instruct'
    """
    prompt = f"""
Write a real, recent, and slightly exaggerated informative article about the latest news {topic}, around 250 words
Format the output as clean and readable HTML, but include only the content section (no <html>, <head>, or <body> tags).
Use:

- <h2> for the article title 

- <h3> for section subtitles 

- <p> for clear, short paragraphs

- <strong> to bold important words

- Optional <br> tags for spacing

The article should be around 230 words. Make it engaging, well-structured, and suitable for blog use.

Do not include styles or extra metadata. Only return the HTML content...
example:
<h2>U.S. Financial System Evolves Rapidly Amid Economic Surprises</h2>

<h3>Economic Growth Exceeds Forecasts</h3>

<p>
The <strong>U.S. economy</strong> continues to defy expectations. In Q2 2025, GDP surged by a surprising <strong>3%</strong>, driven by strong consumer spending and a booming services sector. Despite ongoing geopolitical tensions and tariff pressures, the American financial engine shows no signs of slowing down. <strong>Wall Street</strong> responded with cautious optimism as investors rebalanced portfolios to favor sectors like tech, energy, and fintech.
</p>

<h2>Federal Reserve Holds Rates—For Now</h2>

<p>
The <strong>Federal Reserve</strong>, meanwhile, maintained its key interest rate at 4.25–4.50%, but insiders suggest that a <strong>rate cut</strong> in September is on the table. Inflation, while still present, has begun to cool—particularly in food and housing—which gives the Fed room to maneuver. However, concerns over wage stagnation and a slowing labor market still loom.
</p>



<h2>Banking Meets Crypto</h2>

<p>
In the private sector, major shifts are underway. <strong>JPMorgan Chase</strong> announced a strategic partnership with <strong>Coinbase</strong>, allowing users to convert credit card points directly into <strong>cryptocurrency</strong>. This move marks a new era of cooperation between traditional banking and decentralized finance.
</p>



<h2>Fintech Soars</h2>

<p>
Simultaneously, AI-powered fintech firm <strong>Ramp</strong> secured $500 million in new funding, pushing its valuation to $22.5 billion. It now provides automated financial tools to over 40,000 U.S. companies.
</p>



<h2>Looking Ahead</h2>

<p>
With economic data surprising analysts and financial innovation accelerating, the landscape is changing faster than ever. <strong>Adaptability</strong>, both in policy and technology, will be key to navigating what’s next.
</p>. """
    try:
        response = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error en Hugging Face: {e}")
        return f"Artículo no disponible para '{topic}'."

# Recorrer temas y subir los artículos a Firebase
# Solo tomar el primer tema en tendencia
if trending_topics:
    topic = trending_topics[0]
    print(f"Generando artículo para: {topic}")
    article_text = generate_article(topic)

    # Subir a la colección "trending_articles"
    doc_ref = db.collection("trending_articles").document(topic)
    doc_ref.set({
        "title": topic,
        "description": article_text,
        "date": firestore.SERVER_TIMESTAMP
    })

    print(f"Artículo sobre '{topic}' subido a Firebase.")
else:
    print("No hay temas en tendencia para procesar.")
