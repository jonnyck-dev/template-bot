import json, requests, asyncio, re, rag, provider, os, glob
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

md_files = glob.glob("CONOCIMIENTOBASE/*.md")
needs_build = False
if not os.path.exists("knowledge.json"):
    needs_build = True
elif md_files:
    knowledge_mtime = os.path.getmtime("knowledge.json")
    newest_md = max(os.path.getmtime(f) for f in md_files)
    if newest_md > knowledge_mtime:
        needs_build = True

if needs_build:
    import build_knowledge
    build_knowledge.build()
    print("knowledge.json auto-built")

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
    model: str = ""
    provider: str = ""
    context_size: int = 0
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
    pinfo = provider.get_provider_info()
    return {
        "status": "ok",
        "business": BUSINESS_NAME,
        "provider": pinfo["provider"],
        "model": pinfo["model"],
        "knowledge_sections": rag.get_sections_count(),
    }


@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "question is required")

    config = provider.load_config()
    if req.provider: config["provider"] = req.provider
    if req.model: config["model"] = req.model
    if req.context_size: config["context_size"] = req.context_size

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(req.question, k=req.rag_k)},
    ]

    async def generate():
        try:
            for token in provider.chat(messages, stream=True, config=config):
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                await asyncio.sleep(0)
            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.get("/api/stream")
async def chat_stream_get(
    q: str = Query(..., description="Pregunta del usuario"),
    model: str = Query(""),
    provider_name: str = Query(""),
    rag_k: int = Query(2),
):
    if not q.strip():
        raise HTTPException(400, "q is required")

    config = provider.load_config()
    if provider_name: config["provider"] = provider_name
    if model: config["model"] = model

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(q, k=rag_k)},
    ]

    async def generate():
        try:
            for token in provider.chat(messages, stream=True, config=config):
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                await asyncio.sleep(0)
            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat/sync")
async def chat_sync(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "question is required")

    config = provider.load_config()
    if req.provider: config["provider"] = req.provider
    if req.model: config["model"] = req.model
    if req.context_size: config["context_size"] = req.context_size

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(req.question, k=req.rag_k)},
    ]

    try:
        answer = "".join(provider.chat(messages, stream=False, config=config))
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(500, str(e))


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "FRONTEND")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
