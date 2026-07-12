import json, requests, sys, os, re, rag

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma4:e2b-it-qat"
DEFAULT_CONTEXT = 131072
BUSINESS_NAME = rag.get_business_name()
TAGLINE = rag.get_tagline()

def build_system_prompt(thinking=False):
    base = f"""Eres un asistente informativo automatizado sobre {BUSINESS_NAME}.

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

    if thinking:
        base = base.replace(
            "Eres un asistente",
            "Eres un asistente\n\nAntes de responder, piensa paso a paso y muestra tu razonamiento interno entre las etiquetas  response y luego da tu respuesta final."
        )
    return base

thinking_enabled = False
show_thinking = False
current_model = DEFAULT_MODEL
context_size = DEFAULT_CONTEXT
rag_k = 2
session_on = False
history = []

def get_system_prompt():
    return build_system_prompt(thinking=thinking_enabled)

def get_temperature():
    return 0.5 if thinking_enabled else 0.1

def build_user_message(pregunta):
    context = rag.get_relevant_context(pregunta, k=rag_k)
    return f"""INFORMACION OFICIAL DE {BUSINESS_NAME}:
{context}

INSTRUCCION:
Usa EXCLUSIVAMENTE la informacion de arriba para responder.
Si la pregunta no tiene relacion con {BUSINESS_NAME}, indicalo claramente segun las reglas.
Si la informacion no esta disponible, admitelo sin inventar.

PREGUNTA DEL USUARIO:
{pregunta}"""

def strip_reasoning(texto):
    return re.sub(r"<reasoning>[\s\S]*?</reasoning>", "", texto).strip()

def ask(pregunta):
    global history, session_on, thinking_enabled, current_model, show_thinking, context_size
    user_msg = build_user_message(pregunta)

    if session_on:
        messages = [
            {"role": "system", "content": get_system_prompt()},
            *history,
            {"role": "user", "content": user_msg},
        ]
    else:
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_msg},
        ]

    payload = {
        "model": current_model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": get_temperature(), "num_ctx": context_size},
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)
    full_content = ""

    for line in response.iter_lines():
        if not line:
            continue
        chunk = json.loads(line)
        delta = chunk.get("message", {}).get("content", "")
        if not delta:
            continue
        full_content += delta
        sys.stdout.write(delta)
        sys.stdout.flush()

    print()

    if not show_thinking:
        full_content = strip_reasoning(full_content)

    if session_on:
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": full_content})

    return full_content

def mostrar_status():
    print()
    print("=" * 50)
    print(f"  Negocio:    {BUSINESS_NAME}")
    print(f"  Modelo:     {current_model}")
    print(f"  Contexto:   {context_size}")
    print(f"  RAG top-K:  {rag_k}")
    print(f"  Sesion:     {'ACTIVADA' if session_on else 'DESACTIVADA'}")
    print(f"  Thinking:   {'ACTIVADO' if thinking_enabled else 'DESACTIVADO'}")
    print(f"  ShowThink:  {'VISIBLE' if show_thinking else 'OCULTO'}")
    print(f"  Temperatura: {get_temperature()}")
    print(f"  Secciones:  {rag.get_sections_count()}")
    if session_on:
        print(f"  Historial:  {len(history)//2} intercambios")
    print("=" * 50)

def procesar_comando(entrada):
    global session_on, thinking_enabled, current_model, context_size, history, show_thinking, rag_k

    texto = entrada.lower()
    if texto.startswith("/"):
        texto = texto[1:]
    partes = texto.split()
    comando = partes[0]

    if comando in ("salir", "exit", "quit"):
        print(f"Asistente {BUSINESS_NAME}: Hasta luego.")
        return "exit"

    if comando == "help":
        print()
        print("  Comandos:")
        print("  /salir                 Terminar sesion")
        print("  /session               Activar/desactivar historial")
        print("  /think                 Activar/desactivar razonamiento del modelo")
        print("  /showthink             Mostrar/ocultar el razonamiento en pantalla")
        print("  /model <nombre>        Cambiar modelo (ej: /model qwen3.5:9b)")
        print("  /context <numero>      Cambiar contexto (ej: /context 65536)")
        print("  /rag <numero>          Cambiar top-K de RAG (ej: /rag 3)")
        print("  /status                Ver configuracion actual")
        print("  /debug                 Ver prompt del sistema")
        print("  /test                  Pruebas rapidas")
        print()
        return "ok"

    if comando == "status":
        mostrar_status()
        return "ok"

    if comando == "session":
        session_on = not session_on
        history = []
        print(f"Sesion {'ACTIVADA' if session_on else 'DESACTIVADA'}.")
        return "ok"

    if comando == "think":
        thinking_enabled = not thinking_enabled
        print(f"Thinking {'ACTIVADO' if thinking_enabled else 'DESACTIVADO'}.")
        return "ok"

    if comando == "showthink":
        show_thinking = not show_thinking
        print(f"ShowThink {'ACTIVADO' if show_thinking else 'DESACTIVADO'}.")
        return "ok"

    if comando == "model":
        if len(partes) < 2:
            print(f"Modelo actual: {current_model}")
            print("Usa: /model <nombre>  (ej: /model qwen3.5:9b)")
        else:
            current_model = partes[1]
            history = []
            print(f"Modelo cambiado a: {current_model}")
        return "ok"

    if comando == "context":
        if len(partes) < 2:
            print(f"Contexto actual: {context_size}")
            print("Usa: /context <numero>  (ej: /context 65536)")
        else:
            try:
                nuevo = int(partes[1])
                if nuevo < 1024:
                    print("El contexto minimo es 1024.")
                else:
                    context_size = nuevo
                    print(f"Contexto cambiado a: {context_size}")
            except ValueError:
                print(f"Valor invalido: {partes[1]}. Debe ser un numero.")
        return "ok"

    if comando == "rag":
        if len(partes) < 2:
            print(f"RAG top-K actual: {rag_k}")
            print("Usa: /rag <numero>  (ej: /rag 3)")
        else:
            try:
                nuevo = int(partes[1])
                if nuevo < 1:
                    print("El minimo es 1.")
                else:
                    rag_k = nuevo
                    print(f"RAG top-K cambiado a: {rag_k}")
            except ValueError:
                print(f"Valor invalido: {partes[1]}. Debe ser un numero.")
        return "ok"

    if comando == "debug":
        sample_msg = build_user_message("[PRUEBA]")
        print("\n" + "=" * 60)
        print(f"SYSTEM PROMPT ({len(get_system_prompt())} chars):")
        print(get_system_prompt())
        print("\n---")
        print(f"USER MESSAGE ({len(sample_msg)} chars):")
        print(sample_msg[:600] + f"\n... (truncado, total: {len(sample_msg)})")
        print("=" * 60)
        return "ok"

    if comando == "test":
        print("\nEjecutando pruebas rapidas...")
        tests = [
            f"Que es {BUSINESS_NAME}?",
            "Cuales son los servicios disponibles?",
            "hola",
            "gracias",
        ]
        for t in tests:
            print(f"\n>>> {t}")
            try:
                ask(t)
            except Exception as e:
                print(f"<<< Error: {e}")
        return "ok"

    return "unknown"

def main():
    global session_on, thinking_enabled, current_model, context_size, history, show_thinking

    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print(f"  {BUSINESS_NAME} - Chat interactivo")
    if TAGLINE:
        print(f"  {TAGLINE}")
    print("=" * 60)
    mostrar_status()
    print("  Usa /help para ver comandos")
    print()

    while True:
        try:
            entrada = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not entrada:
            continue

        if entrada.startswith("/"):
            resultado = procesar_comando(entrada)
            if resultado == "exit":
                break
            continue

        try:
            ask(entrada)
        except requests.exceptions.ConnectionError:
            print("\nError: No se puede conectar con Ollama.")
        except requests.exceptions.Timeout:
            print("\nError: La consulta excedio el tiempo de espera (300s).")
        except json.JSONDecodeError:
            print(f"\nError: Respuesta invalida. Usa /model <otro>.")
        except Exception as e:
            print(f"\nError inesperado: {e}")

if __name__ == "__main__":
    main()