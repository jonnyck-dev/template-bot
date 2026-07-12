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
- **Ollama** corriendo localmente en `localhost:11434`
- **Modelo** `gemma4:e2b-it-qat` descargado (`ollama pull gemma4:e2b-it-qat`)
- Librerias: `requests`, `sentence-transformers`, `numpy` (`pip install requests sentence-transformers numpy`)

---

## 🚀 Como usar

### 1. Forkea este repositorio

Haz fork a este template para tener tu propia copia.

### 2. Configura tu negocio

Edita `config.json`:

```json
{
  "business_name": "Tu Negocio",
  "tagline": "Tu eslogan aqui",
  "language": "es"
}
```

### 3. Agrega tu base de conocimiento

Reemplaza los archivos en `CONOCIMIENTOBASE/` con la informacion de TU negocio. Crea tantos archivos `.md` como temas necesites:

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

Esto genera `knowledge.json` con toda la informacion estructurada.

### 5. Genera embeddings (RAG)

```bash
python build_embeddings.py
```

Esto genera `embeddings.json` con vectores semanticos de cada seccion.
El bot solo inyectara al prompt las **2 secciones mas relevantes** a cada pregunta, en lugar de toda la base.

### 6. Inicia el chat

```bash
python test_bot.py
```

### Comandos disponibles en el chat:

| Comando | Descripcion |
|---------|-------------|
| `/help` | Mostrar ayuda |
| `/think` | Mostrar/ocultar pensamiento del modelo |
| `/model modelo` | Cambiar modelo de Ollama |
| `/context numero` | Cambiar tamano de contexto |
| `/rag numero` | Cambiar top-K de RAG (ej: /rag 3) |
| `/session nombre` | Cambiar nombre de sesion |
| `/showthink` | Ver ultimo pensamiento del modelo |
| `/debug` | Ver prompt completo enviado |
| `/test` | Ejecutar bateria de pruebas rapidas |
| `/salir` | Terminar la sesion |

### 7. Inicia el servidor API

```bash
python api.py
```

El servidor corre en `http://localhost:8010`.

Endpoints:
- `POST /api/chat` - Streaming SSE
- `POST /api/chat/sync` - Respuesta completa
- `GET /health` - Estado del servidor

### 8. Despliega el frontend

La carpeta `FRONTEND/` contiene una interfaz de chat lista para desplegar en **Vercel**:

```bash
cd FRONTEND
```

Conecta la carpeta a Vercel o simplemente arrastra la carpeta a vercel.com.

**Importante**: En `FRONTEND/app.js` cambia `API_BASE` por la URL de tu API (ej: tu tunel de Cloudflare).

### 9. Widget embebido (flotante)

Agrega el asistente a **cualquier pagina web** con una sola linea:

```html
<script src="widget.js" data-api-base="http://localhost:8010" data-business="Tu Negocio"></script>
```

Aparecera un boton flotante en la esquina inferior derecha. Sin iframes, sin configuracion extra.

---

## 🎨 Personalizacion

### Colores del chat

Edita `FRONTEND/style.css` y cambia los valores de `#00BFFF` (azul electrico) por los colores de tu marca.

### System prompt

Edita `api.py` y `test_bot.py` para ajustar el tono, reglas y comportamiento del asistente.

### Modelo de IA

Por defecto usa `gemma4:e2b-it-qat`. Cambialo en `api.py`.

## 📁 Estructura del proyecto

```
template-bot/
├── config.json                   # Configuracion del negocio
├── CONOCIMIENTOBASE/             # Archivos fuente de conocimiento (.md)
│   └── 01-ejemplo-barberking.md  # Ejemplo incluido
├── build_knowledge.py            # Compila .md -> knowledge.json
├── build_embeddings.py           # Genera embeddings para RAG
├── rag.py                        # Busqueda semantica (RAG)
├── knowledge.json                # Base de conocimiento compilada (generado)
├── embeddings.json               # Vectores semanticos (generado)
├── api.py                        # Servidor FastAPI (puerto 8010)
├── test_bot.py                   # Chat interactivo por consola
├── FRONTEND/                     # Interfaz de chat para Vercel + widget
│   ├── index.html                # Pagina completa
│   ├── style.css                 # Estilos
│   ├── app.js                    # Logica de la pagina completa
│   ├── widget.js                 # Widget flotante embebible
│   └── widget-demo.html          # Demo del widget
├── vercel.json                   # Config para Vercel
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

Para que tu API sea accesible desde internet:

```bash
cloudflared tunnel --url http://localhost:8010
```

Luego actualiza `FRONTEND/app.js` con la URL generada.

---

## 📝 Requisitos del concurso

Este template cumple con:

- ✅ 10+ datos concretos en la base de conocimiento
- ✅ Respuesta "No dispongo de esa informacion" cuando falta data
- ✅ Tono y personalidad definidos en el system prompt
- ✅ Rechazo de preguntas fuera de dominio
- ✅ Embeddable como widget chat (frontend listo para Vercel + widget flotante)
- ✅ RAG (busqueda semantica) — solo inyecta la informacion relevante a cada pregunta

---

Hecho con ❤️ por [Jonnyck Dev](https://github.com/jonnyckdev)
