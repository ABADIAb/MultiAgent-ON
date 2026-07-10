import os
from src.core.llm import create_kimi_llm
from dotenv import load_dotenv

#API_KEY="sk-kimi-kTpMqscas4wHPO5CRFEhW6cRs2VT3up3Cqb9XHfK2clcLZcUoFwUdQRNeACoeMje"
#BASE_URL="https://api.kimi.com/coding/v1"

# --- Configure LLM ---
load_dotenv()
api_key = os.getenv("KIMI_API_KEY", "")
base_url = os.getenv("KIMI_BASE_URL", "")

try:
    llm = create_kimi_llm(api_key=api_key, base_url=base_url, model="moonshot-v1-8k")
    print("Enviando ping al modelo...")
    res = llm.invoke("Di 'hola' en español, ingles e italiano")
    print(f"¡Éxito! Respuesta del modelo: {res.content}")
except Exception as e:
    print(f"Fallo en la API Key o URL. Detalles del error:\n{e}")