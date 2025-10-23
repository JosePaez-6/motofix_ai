from dotenv import load_dotenv
load_dotenv()

import os
from loader import crear_vectorstore

# ======================================================
# 🔹 Buscar todos los manuales en la carpeta
# ======================================================
def obtener_modelos_desde_carpeta(carpeta: str):
    """Escanea la carpeta y devuelve {NOMBRE_MODELO: RUTA_TXT}"""
    modelos = {}
    if not os.path.exists(carpeta):
        print(f"⚠️ La carpeta '{carpeta}' no existe. Créala y agrega los manuales TXT.")
        return modelos

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(".txt"):
            nombre_modelo = os.path.splitext(archivo)[0].upper()
            modelos[nombre_modelo] = os.path.join(carpeta, archivo)
    return modelos

# ======================================================
# 🔹 Proceso principal de generación de vectores
# ======================================================
def main():
    carpeta_manuals = "manuales_txt"
    modelos = obtener_modelos_desde_carpeta(carpeta_manuals)

    if not modelos:
        print("⚠️ No se encontraron archivos .txt en la carpeta 'manuales_txt'.")
        return

    print(f"🔍 Se encontraron {len(modelos)} manual(es): {', '.join(modelos.keys())}")

    for modelo, ruta_txt in modelos.items():
        try:
            with open(ruta_txt, "r", encoding="utf-8") as f:
                texto = f.read()

            print(f"\n📦 Procesando modelo: {modelo}")
            crear_vectorstore(modelo, texto)
            print(f"✅ Vectorstore generado y guardado en /vectores/{modelo}")

        except Exception as e:
            print(f"❌ Error procesando {modelo}: {e}")

    print("\n🎉 Proceso completado correctamente. Los vectores están listos en /vectores/")

# ======================================================
# 🔹 Ejecución
# ======================================================
if __name__ == "__main__":
    main()
