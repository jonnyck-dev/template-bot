# Template Bot 🚀

**Un template listo para crear tu propio asistente de IA conversacional "El asistente que responde por tu negocio".**

Solo editas la base de conocimiento, compilas y desplegas.

---

## 🏆 Caso de exito: Janus Bot

Este template esta inspirado en **Janus Bot**, un asistente informativo sobre JANUS Studio (servicio de doblaje automatico de videos con IA).

-En mis pruebas Janus Bot demostro que con buena base de conocimiento + system prompt riguroso + un modelo local, se puede crear un bot que NO alucina y responde solo lo que sabe.
- Este template te da esa misma arquitectura, solo cambias los datos.

👉 **[Janus Bot - Repositorio original](https://github.com/jonnyckdev/janus-bot)**

---

## 📋 Requisitos

- **Python 3.10+**
- Librerias: `pip install requests numpy sentence-transformers`
- Opcional: **Ollama** corriendo en `localhost:11434` (si usas provider ollama)
- Opcional: **API key** de OpenAI, Google, Anthropic u OpenCode (segun el provider)

---

## 🚀 Como usar

### 1. Forkea este repositorio

Haz fork a este template para tener tu propia copia.

### 2. Configura tu negocio y proveedor

Edita `config.json`:

```json
{
  "business_name": "Tu Negocio",
  "tagline": "Tu eslogan aqui",
  "language": "es",
  "provider": "ollama",
  "model": "gemma4:e2b-it-qat",
  "api_key": "",
  "base_url": "",
  "temperature": 0.1,
  "context_size": 131072
}
```

### Proveedores soportados

| Provider | Descripcion | Requiere | Default model |
|----------|------------|----------|---------------|
| `ollama` | Local con Ollama | Tener Ollama instalado | gemma4:e2b-it-qat |
| `openai` | OpenAI API | API key | gpt-4o |
| `gemini` | Google Gemini API | API key (GEMINI_API_KEY) | gemini-2.0-flash |
| `claude` | Anthropic Claude API | API key (ANTHROPIC_API_KEY) | claude-sonnet-4-20250514 |
| `opencode-go` | OpenCode Go (suscripcion $10/mes) | OPENCODE_API_KEY | deepseek-v4-flash |
| `opencode-zen` | OpenCode Zen (modelos gratis + premium) | OPENCODE_API_KEY | deepseek-v4-flash-free |

### Variables de entorno

Las API keys tambien pueden configurarse como variables de entorno en lugar de `config.json`:

| Variable | Proveedor |
|----------|-----------|
| `OPENAI_API_KEY` | OpenAI |
| `GEMINI_API_KEY` | Google Gemini |
| `ANTHROPIC_API_KEY` | Anthropic Claude |
| `OPENCODE_API_KEY` | OpenCode Go / Zen |

Si la variable existe, tiene prioridad sobre `api_key` en `config.json`.
Ollama no requiere API key.
Si `base_url` esta vacio, se usa el endpoint oficial de cada proveedor.

### 3. Agrega tu base de conocimiento

Reemplaza los archivos en `CONOCIMIENTOBASE/` con la informacion de TU negocio:

```
CONOCIMIENTOBASE/
├── 01-servicios.md
├── 02-horarios.md
├── 03-precios.md
├── 04-faq.md
└── ...
```

### 4. Compila base de conocimiento

```bash
python build_knowledge.py
```

### 5. Genera embeddings (RAG)

```bash
python build_embeddings.py
```

Esto permite que el bot solo inyecte al prompt las **2 secciones mas relevantes** a cada pregunta.

### 6. Inicia el chat

```bash
python test_bot.py
```

### Comandos disponibles en el chat (solo terminal de prueba):

Estos comandos solo funcionan en `test_bot.py`. El widget y el API **solo aceptan preguntas** — no exponen comandos ni cambios de configuracion.

| Comando | Descripcion |
|---------|-------------|
| `/help` | Mostrar ayuda |
| `/think` | Mostrar/ocultar pensamiento del modelo |
| `/model modelo` | Cambiar modelo (ej: /model gpt-4o) |
| `/provider nombre` | Cambiar proveedor: ollama, openai, gemini, claude, opencode-go, opencode-zen |
| `/context numero` | Cambiar tamano de contexto |
| `/rag numero` | Cambiar top-K de RAG (ej: /rag 3) |
| `/session` | Activar/desactivar historial |
| `/showthink` | Ver ultimo pensamiento del modelo |
| `/debug` | Ver prompt completo enviado |
| `/test` | Ejecutar bateria de pruebas rapidas |
| `/salir` | Terminar la sesion |

### 7. Inicia el servidor API

```bash
python api.py
```

El servidor corre en `http://localhost:8020`. Endpoints: `/api/chat` (SSE), `/api/chat/sync`, `/health`.

### 8. Despliega el frontend

La carpeta `FRONTEND/` contiene interfaz de chat para Vercel.
En `FRONTEND/app.js` cambia `API_BASE` por la URL de tu API.

### 9. Widget embebido (flotante)

```html
<script src="widget.js" data-api-base="http://localhost:8020" data-business="Tu Negocio"></script>
```

> **Seguridad:** El widget solo procesa preguntas. No expone comandos ni permite cambios de configuracion desde el frontend.

---

## 🎨 Personalizacion

### Colores del chat
Edita `FRONTEND/style.css` - cambia `#00BFFF` por los colores de tu marca.

### System prompt
Edita `api.py` y `test_bot.py` para ajustar tono, reglas y comportamiento.

### Modelo / Proveedor
Edita `config.json` y reinicia el servidor.

## 📁 Estructura del proyecto

```
template-bot/
├── config.json                   # Configuracion (negocio + proveedor)
├── CONOCIMIENTOBASE/             # Archivos fuente de conocimiento (.md)
├── build_knowledge.py            # Compila .md -> knowledge.json
├── build_embeddings.py           # Genera embeddings para RAG
├── rag.py                        # Busqueda semantica (RAG)
├── provider.py                   # Capa de abstraccion de APIs (Ollama, OpenAI, Gemini, Claude, OpenCode Go/Zen)
├── knowledge.json                # Base de conocimiento compilada
├── embeddings.json               # Vectores semanticos
├── api.py                        # Servidor FastAPI
├── test_bot.py                   # Chat interactivo por consola
├── FRONTEND/                     # Interfaz web + widget
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── widget.js
│   └── widget-demo.html
├── vercel.json
└── README.md
```

---

## 🔒 Reglas anti-alucinacion

El system prompt incluye reglas estrictas para que el bot:
- Responda SOLO con la informacion proporcionada
- Rechace preguntas fuera de dominio
- No invente datos, precios ni especificaciones
- No intente vender ni pedir datos personales
- Responda en el idioma de la pregunta

---

## 🌐 Despliegue completo con Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8020
```

Luego actualiza `FRONTEND/app.js` con la URL generada.

---

## 📝 Requisitos del concurso

Este template cumple con:
- ✅ 10+ datos concretos en la base de conocimiento
- ✅ Respuesta "No dispongo de esa informacion" cuando falta data
- ✅ Tono y personalidad definidos en el system prompt
- ✅ Rechazo de preguntas fuera de dominio
- ✅ Embeddable como widget chat
- ✅ RAG (busqueda semantica)
- ✅ Multi-proveedor (Ollama, OpenAI, Gemini, Claude, OpenCode Go/Zen)

---

Hecho con ❤️ por [Jonnyck Dev](https://github.com/jonnyckdev)

