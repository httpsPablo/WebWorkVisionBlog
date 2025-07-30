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
    prompt = f"Write an engaging and informative article about the latest news on {topic} of around 200 words. (information real, you can exaggerate a little)"
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
