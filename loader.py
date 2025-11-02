from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORES_DIR = os.path.join(BASE_DIR, "vectores")

# ======================================================
# 🔹 Configurar embeddings
# ======================================================
def obtener_embeddings():
    print("Usando embeddings de OpenAI (text-embedding-3-small)")
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

# ======================================================
# Crear vectorstore desde texto
# ======================================================
def crear_vectorstore(nombre_modelo: str, texto_manual: str):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documentos = [Document(page_content=chunk) for chunk in splitter.split_text(texto_manual)]

    embeddings = obtener_embeddings()
    vectores = FAISS.from_documents(documentos, embeddings)

    os.makedirs(VECTORES_DIR, exist_ok=True)
    ruta_guardado = os.path.join(VECTORES_DIR, nombre_modelo)
    vectores.save_local(ruta_guardado)
    print(f"Vectorstore guardado en {ruta_guardado}")
    return vectores

# ======================================================
# Cargar vectorstore existente
# ======================================================
def cargar_vectorstore(nombre_modelo: str):
    embeddings = obtener_embeddings()
    ruta = os.path.join(VECTORES_DIR, nombre_modelo)

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el vectorstore para {nombre_modelo} en {ruta}")

    print(f"Cargando vectorstore: {ruta}")
    return FAISS.load_local(ruta, embeddings, allow_dangerous_deserialization=True)
