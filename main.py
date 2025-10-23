import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from loader import cargar_vectorstore
from local_llm import responder_con_llm

load_dotenv()

app = FastAPI(
    title="MOTOFIX - API de Asistente Técnico",
    description="Asistente experto en mantenimiento de motocicletas basado en IA.",
    version="1.0.0"
)

# =========================================================
# 🔹 Configuración CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 🔹 Cargar todos los modelos automáticamente
# =========================================================
def cargar_todos_los_vectores():
    vectorstores = {}
    carpeta = "vectores"

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        return vectorstores

    for modelo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, modelo)
        if os.path.isdir(ruta):
            try:
                vectorstores[modelo] = cargar_vectorstore(modelo)
                print(f"✅ Vectorstore del modelo '{modelo}' cargado correctamente.")
            except Exception as e:
                print(f"⚠️ Error cargando vectorstore '{modelo}': {e}")
    return vectorstores


vectorstores = cargar_todos_los_vectores()
modelos_disponibles = list(vectorstores.keys())

# =========================================================
# 🔹 Modelos de datos
# =========================================================
class Pregunta(BaseModel):
    modelo: str
    pregunta: str

# =========================================================
# 🔹 Rutas principales
# =========================================================
@app.get("/")
def home():
    return {
        "mensaje": "🚀 API de MOTOFIX en ejecución",
        "modelos_disponibles": modelos_disponibles
    }

@app.get("/modelos")
def obtener_modelos():
    """Devuelve los modelos disponibles en la carpeta vectores"""
    return {"modelos": modelos_disponibles}

@app.post("/preguntar")
def responder(data: Pregunta):
    modelo = data.modelo.upper()

    if modelo not in vectorstores:
        raise HTTPException(
            status_code=404,
            detail=f"Modelo '{modelo}' no encontrado. Modelos disponibles: {modelos_disponibles}"
        )

    print(f"🧠 Consultando modelo: {modelo}")
    docs = vectorstores[modelo].similarity_search(data.pregunta, k=3)
    contexto = "\n".join([doc.page_content for doc in docs])
    respuesta = responder_con_llm(data.pregunta, contexto)

    return {
        "modelo": modelo,
        "pregunta": data.pregunta,
        "respuesta": respuesta
    }

# =========================================================
# 🔹 Punto de entrada (solo si se ejecuta directamente)
# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
