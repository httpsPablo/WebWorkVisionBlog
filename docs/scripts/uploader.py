from pytrends.request import TrendReq
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
from dotenv import load_dotenv

# 📂 Cargar variables del entorno
load_dotenv()

# 🔐 Setear API Key de OpenAI
openai.api_key = os.getenv("openai-api-key")

# 🔥 Inicializar Firebase
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 📈 Obtener tendencias de Google Trends (Argentina)
pytrends = TrendReq()
pytrends.build_payload(kw_list=["technology", "health", "business"], geo="AR", timeframe="now 1-d")
trending = pytrends.trending_searches(pn="argentina")

# 📰 Tomar el primer tema en tendencia o usar uno genérico
topic = trending.iloc[0, 0] if not trending.empty else "Latest trend"

# 🤖 Generar artículo con OpenAI
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a professional blog writer."},
        {"role": "user", "content": f"Write a short article (around 200 words) about: {topic}"}
    ]
)

article_text = response.choices[0].message.content

# 🗓️ Fecha actual (opcional)
timestamp = datetime.datetime.now().isoformat()

# 🔄 Subir artículo a Firebase Firestore
db.collection("article").add({
    "title": topic,
    "description": article_text,
})

print(f"✅ Article on '{topic}' uploaded successfully.")
