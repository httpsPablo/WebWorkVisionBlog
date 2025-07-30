import os
import json
from datetime import datetime

import requests
from pytrends.request import TrendReq
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

# Cargar variables de entorno del archivo .env (API keys, rutas, etc)
load_dotenv()

# Inicializar Firebase con credenciales almacenadas en .env
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)

# Cliente para Firestore (base de datos NoSQL en Firebase)
db = firestore.client()

# Inicializar pytrends para Google Trends en Estados Unidos
pytrends = TrendReq(hl='en-US', tz=360)

# Construir payload para la palabra "news" y periodo 'last 1 day'
pytrends.build_payload(["news"], cat=0, timeframe='now 1-d', geo='US', gprop='')

# Obtener búsquedas relacionadas con "news"
related_queries = pytrends.related_queries()

# Obtener las 10 principales búsquedas relacionadas con "news"
top_queries = related_queries.get("news", {}).get("top", None)
if top_queries is not None:
    trending_topics = top_queries["query"].tolist()
else:
    trending_topics = ["No trending topics found"]

print("Temas en tendencia:", trending_topics)

# Configurar cliente OpenAI apuntando al router de Hugging Face con token de HF
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HUGGINGFACE_TOKEN"),
)

def generate_article(topic):
    """
    Usar modelo de Hugging Face vía OpenAI API compatible para generar
    un texto corto relacionado con el tema dado.
    """
    prompt = f"Write a short informative article about '{topic}'."

    try:
        # Crear petición de chat completions al modelo Kimi-K2-Instruct
        response = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        # Extraer el contenido del mensaje generado por la IA
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error en Hugging Face: {e}")
        # En caso de error, devolver texto por defecto
        return f"Artículo no disponible para '{topic}'."

# Recorrer todos los temas en tendencia y generar artículos
for topic in trending_topics:
    print(f"Generando artículo para: {topic}")
    article_text = generate_article(topic)

    # Guardar en Firebase Firestore en la colección 'trending_articles'
    doc_ref = db.collection("trending_articles").document(topic)
    doc_ref.set({
        "title": topic,
        "description": article_text,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    })
    print(f"Artículo sobre '{topic}' subido a Firebase.")
