import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def responder_con_llm(pregunta: str, contexto: str) -> str:
    prompt = f"""
Eres un asistente experto en motocicletas llamado MOTOFIX, especializado en mantenimiento,
fallas mecánicas y características técnicas de motos. Usa el siguiente contexto del manual
para responder de forma técnica, clara y profesional.

Si el manual no menciona directamente la información solicitada, brinda una respuesta razonada
basada en conocimientos técnicos generales de motocicletas similares (sin inventar datos falsos).

---
Contexto del manual:
{contexto}
---
Pregunta del usuario:
{pregunta}
---

Responde con:
- Una explicación técnica detallada (mínimo 2 párrafos si es posible).
- Si no hay información directa, ofrece una recomendación o consejo técnico alternativo.
- Usa tono profesional, cercano y sin ser redundante.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un mecánico experto en motocicletas y mantenimiento."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=400
    )

    return response.choices[0].message.content.strip()
