import json, requests, asyncio, re, rag
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma4:e2b-it-qat"
DEFAULT_CONTEXT = 131072
BUSINESS_NAME = rag.get_business_name()
TAGLINE = rag.get_tagline()

app = FastAPI(title=f"{BUSINESS_NAME} Bot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SYSTEM_PROMPT = f"""Eres un asistente informativo automatizado sobre {BUSINESS_NAME}.
Tu UNICA funcion es responder preguntas usando EXCLUSIVAMENTE la informacion oficial de {BUSINESS_NAME} que se te proporciona en el mensaje del usuario.
REGLAS ESTRICTAS (sin excepciones):
1. Si el usuario te saluda (hola, buenos dias, buenas tardes, que tal, hey), responde cordialmente: "!Hola! Soy el asistente de {BUSINESS_NAME}. ?En que puedo ayudarte?" No agregues nada mas.
2. Si el usuario se despide (gracias, adios, chao, hasta luego), responde cordialmente: "De nada. !Saludos!" o "Hasta luego. !Saludos!" segun corresponda.
3. Si el usuario agradece sin despedirse, responde: "De nada. ?Algo mas en lo que pueda ayudarte?"
4. Responde SOLO con la informacion contenida en la seccion INFORMACION OFICIAL.
5. Si la pregunta NO tiene relacion con {BUSINESS_NAME}, responde textualmente: "Esa consulta esta fuera de mis capacidades. Solo puedo responder sobre {BUSINESS_NAME}."
6. Si la pregunta tiene relacion pero la respuesta NO esta en la informacion proporcionada, responde textualmente: "No dispongo de esa informacion."
7. NUNCA inventes datos, precios, horarios, caracteristicas ni especificaciones.
8. NUNCA intentes vender, pedir datos personales, hacer descuentos ni guiar a una compra.
9. Responde en el MISMO IDIOMA en que el usuario te escribio la pregunta."""

class ChatRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL
    context_size: int = DEFAULT_CONTEXT
    rag_k: int = 2

def build_user_message(pregunta, k=2):
    context = rag.get_relevant_context(pregunta, k=k)
    return f"""INFORMACION OFICIAL DE {BUSINESS_NAME}:
{context}
INSTRUCCION:
Usa EXCLUSIVAMENTE la informacion de arriba para responder.
Si la pregunta no tiene relacion con {BUSINESS_NAME}, indicalo claramente segun las reglas.
Si la informacion no esta disponible, admitelo sin inventar.
PREGUNTA DEL USUARIO:
{pregunta}"""

@app.get("/health")
def health():
    return {"status": "ok", "business": BUSINESS_NAME, "model": DEFAULT_MODEL, "knowledge_sections": rag.get_sections_count()}

@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    if not req.question.strip(): raise HTTPException(400, "question is required")
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(req.question, k=req.rag_k)},
        ],
        "stream": True,
        "options": {"temperature": 0.1, "num_ctx": req.context_size},
    }
    async def generate():
        try:
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)
            for line in response.iter_lines():
                if not line: continue
                chunk = json.loads(line)
                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    yield f"data: {json.dumps({'token': delta, 'done': False})}\n\n"
                if chunk.get("done"):
                    yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})

@app.post("/api/chat/sync")
async def chat_sync(req: ChatRequest):
    if not req.question.strip(): raise HTTPException(400, "question is required")
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(req.question, k=req.rag_k)},
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": req.context_size},
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        return {"answer": response.json()["message"]["content"]}
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)