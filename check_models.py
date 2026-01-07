import google.generativeai as genai
import os

# --- IMPORTANTE: PEGA TU CLAVE AQUÍ ---
api_key = "AIzaSyAK_n05ya2vOBirWKSciBRwfjYo7hadEgo" 
# --------------------------------------

genai.configure(api_key=api_key)

print("📡 Consultando a Google...")
try:
    available = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ MODELO DISPONIBLE: {m.name}")
            available = True
    
    if not available:
        print("❌ No se encontraron modelos de generación de texto.")

except Exception as e:
    print(f"❌ Error crítico: {e}")