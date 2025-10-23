from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# ======================================================
# 🔹 Configurar embeddings (corregido para API nueva)
# ======================================================
def obtener_embeddings():
    print("🔹 Usando embeddings de OpenAI (text-embedding-3-small)")

    # El parámetro 'client' evita que LangChain intente crear uno antiguo con 'proxies'
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

# ======================================================
# 🔹 Crear vectorstore desde texto
# ======================================================
def crear_vectorstore(nombre_modelo: str, texto_manual: str):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documentos = [Document(page_content=chunk) for chunk in splitter.split_text(texto_manual)]

    embeddings = obtener_embeddings()
    vectores = FAISS.from_documents(documentos, embeddings)

    os.makedirs("vectores", exist_ok=True)
    vectores.save_local(f"vectores/{nombre_modelo}")
    print(f"✅ Vectorstore guardado en vectores/{nombre_modelo}")
    return vectores

# ======================================================
# 🔹 Cargar vectorstore existente
# ======================================================
def cargar_vectorstore(nombre_modelo: str):
    embeddings = obtener_embeddings()
    ruta = f"vectores/{nombre_modelo}"

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el vectorstore para {nombre_modelo} en {ruta}")

    print(f"📂 Cargando vectorstore: {ruta}")
    return FAISS.load_local(ruta, embeddings, allow_dangerous_deserialization=True)
