import os
import json
from datetime import datetime
import requests
from pytrends.request import TrendReq
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar Firebase
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)

# Cliente Firestore
db = firestore.client()

# Inicializar pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Temas base
topics_base = ["Inversiones",
               "Criptomonedas",
               "Bolsa de valores",
               "Préstamos",
               "Seguros",
               "Hipotecas",
               "Tarjetas de crédito",
               "Bancos digitales",
               "Trading online"]

# Obtener temas relacionados desde Google Trends
trending_topics = []

for topic in topics_base:
    try:
        pytrends.build_payload([topic], cat=0, timeframe='now 1-d', geo='US')
        related = pytrends.related_queries()
        top = related.get(topic, {}).get("top", None)
        if top is not None:
            trending_topics.extend(top["query"].tolist()[:3])  # Máximo 3 por tema
    except Exception as e:
        print(f"Error con el tema '{topic}': {e}")


# Obtener los temas más buscados
trending_topics = []
for topic in topics_base:
    top = related.get(topic, {}).get("top", None)
    if top is not None:
        trending_topics.extend(top["query"].tolist()[:3])  # Máximo 3 por tema

if not trending_topics:
    trending_topics = ["No trending topics found"]

print("Temas en tendencia:", trending_topics)

# Inicializar cliente OpenAI con Hugging Face router
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HUGGINGFACE_TOKEN"),
)

def generate_article(topic):
    prompt = f"""
Write a recent and informative article about the trending topic "{topic}", around 230 words.
Format it using HTML elements ONLY in the content section (no head or body tags):

- Use <h2> for the title
- <h3> for subtitles
- <p> for short, clear paragraphs
- <strong> to emphasize words
- Keep it engaging and well-structured for blogs
    """.strip()

    try:
        response = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generando artículo: {e}")
        return f"<p>Error generando artículo sobre '{topic}'</p>"

# Generar artículos y subir a Firebase solo si no existen
for topic in trending_topics:
    print(f"Verificando si ya existe: {topic}")
    doc_id = topic.replace(" ", "_").lower()
    doc_ref = db.collection("finance_articles").document(doc_id)
    
    if not doc_ref.get().exists:
        print(f"Generando artículo para: {topic}")
        article = generate_article(topic)
        doc_ref.set({
            "title": topic,
            "description": article,
            "date": firestore.SERVER_TIMESTAMP
        })
        print(f"Artículo sobre '{topic}' subido a Firebase.")
    else:
        print(f"Ya existe artículo sobre '{topic}', omitido.")
