import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from loader import cargar_vectorstore
from local_llm import responder_con_llm

# =========================================================
# Configuración base
# =========================================================
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORES_DIR = os.path.join(BASE_DIR, "vectores")

app = FastAPI(
    title="MOTOFIX - API de Asistente Técnico",
    description="Asistente experto en mantenimiento de motocicletas basado en IA.",
    version="1.2.0"
)

# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes cambiarlo a ["https://tuapp.vercel.app"] si deseas restringir
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Función para cargar todos los vectores
# =========================================================
def cargar_todos_los_vectores():
    vectorstores = {}

    if not os.path.exists(VECTORES_DIR):
        print(f"Carpeta de vectores no encontrada en {VECTORES_DIR}")
        return vectorstores

    for modelo in os.listdir(VECTORES_DIR):
        ruta = os.path.join(VECTORES_DIR, modelo)
        if os.path.isdir(ruta):
            try:
                vectorstores[modelo] = cargar_vectorstore(modelo)
                print(f"Vectorstore del modelo '{modelo}' cargado correctamente.")
            except Exception as e:
                print(f"Error cargando vectorstore '{modelo}': {e}")

    return vectorstores


vectorstores = cargar_todos_los_vectores()
modelos_disponibles = list(vectorstores.keys())

print("Modelos cargados en memoria:", modelos_disponibles)

# =========================================================
# Modelos de datos
# =========================================================
class Pregunta(BaseModel):
    modelo: str
    pregunta: str

# =========================================================
# Rutas principales
# =========================================================
@app.get("/")
def home():
    return {
        "mensaje": "API de MOTOFIX en ejecución correctamente",
        "modelos_disponibles": modelos_disponibles,
    }

@app.get("/modelos")
def obtener_modelos():
    """Devuelve los modelos disponibles en la carpeta vectores"""
    return {"modelos": modelos_disponibles}

@app.get("/modelos/normalizados")
def obtener_modelos_normalizados():
    """Devuelve modelos listos para usar en dropdowns"""
    modelos_normalizados = [
        {
            "value": modelo.upper().replace("_", " ").strip(),
            "label": f"Italika {modelo.upper().replace('_', ' ').strip()}"
        }
        for modelo in modelos_disponibles
    ]
    return {"modelos": modelos_normalizados}

# =========================================================
# Endpoint de diagnóstico
# =========================================================
@app.get("/health")
def health_check():
    return {
        "ok": True,
        "ruta_vectores": VECTORES_DIR,
        "existe": os.path.exists(VECTORES_DIR),
        "contenido": os.listdir(VECTORES_DIR) if os.path.exists(VECTORES_DIR) else [],
        "modelos_cargados": list(vectorstores.keys())
    }

# =========================================================
# Ruta principal de consulta
# =========================================================
@app.post("/preguntar")
def responder(data: Pregunta):
    modelo_raw = (
        data.modelo.strip()
        .upper()
        .replace("ITALIKA", "")
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )

    coincidencias = {
        m.upper().replace("_", "").replace("-", "").replace(" ", ""): m
        for m in vectorstores.keys()
    }

    if modelo_raw not in coincidencias:
        raise HTTPException(
            status_code=404,
            detail=f"Modelo '{modelo_raw}' no encontrado. Modelos disponibles: {list(vectorstores.keys())}"
        )

    modelo_real = coincidencias[modelo_raw]
    print(f"Consultando modelo: {modelo_real}")

    # Búsqueda semántica
    docs = vectorstores[modelo_real].similarity_search(data.pregunta, k=3)
    contexto = "\n".join([doc.page_content for doc in docs])
    respuesta = responder_con_llm(data.pregunta, contexto)

    return {
        "modelo": modelo_real,
        "pregunta": data.pregunta,
        "respuesta": respuesta
    }

# =========================================================
# Ejecución local
# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
