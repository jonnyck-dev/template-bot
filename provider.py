import json, os, requests, sys
CONFIG_FILE = "config.json"
_config_cache = None

def load_config():
    global _config_cache
    if _config_cache is None:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                _config_cache = json.load(f)
        else:
            _config_cache = {}
    return _config_cache

def get_default_base_url(provider):
    return {
        "ollama": "http://localhost:11434",
        "openai": "https://api.openai.com/v1",
        "opencode-go": "https://opencode.ai/zen/go/v1",
        "opencode-zen": "https://opencode.ai/zen/v1",
        "gemini": "https://generativelanguage.googleapis.com/v1beta",
        "claude": "https://api.anthropic.com/v1",
    }.get(provider, "")

def resolve_api_key(config):
    provider = config.get("provider", "ollama")
    key = config.get("api_key", "") or os.environ.get(provider.upper().replace("-", "_") + "_API_KEY", "")
    if not key and provider != "ollama":
        key = os.environ.get("API_KEY", "") or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("OPENCODE_API_KEY", "")
    return key

def _chat_ollama(messages, config, model):
    base = config.get("base_url") or get_default_base_url("ollama")
    url = base.rstrip("/") + "/api/chat"
    ctx = config.get("context_size", 131072)
    temp = config.get("temperature", 0.1)
    payload = {"model": model, "messages": messages, "stream": True, "think": True, "options": {"temperature": temp, "num_ctx": ctx}}
    resp = requests.post(url, json=payload, stream=True, timeout=300)
    for line in resp.iter_lines():
        if not line: continue
        chunk = json.loads(line)
        delta = chunk.get("message", {}).get("content", "")
        if delta: yield delta

def _chat_openai(messages, config, model):
    base = config.get("base_url") or get_default_base_url(config.get("provider", "openai"))
    url = base.rstrip("/") + "/chat/completions"
    api_key = resolve_api_key(config)
    temp = config.get("temperature", 0.1)
    payload = {"model": model, "messages": messages, "stream": True, "temperature": temp}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, stream=True, timeout=300)
    for line in resp.iter_lines():
        if not line: continue
        line_str = line.decode() if isinstance(line, bytes) else line
        if not line_str.startswith("data: "): continue
        data_str = line_str[6:].strip()
        if data_str == "[DONE]": continue
        try:
            data = json.loads(data_str)
            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if delta: yield delta
        except json.JSONDecodeError:
            continue

def _chat_gemini(messages, config, model):
    api_key = resolve_api_key(config)
    if not api_key:
        raise ValueError("GEMINI_API_KEY requerida para usar Gemini")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
    contents = []
    system_msg = None
    for msg in messages:
        if msg["role"] == "system": system_msg = msg["content"]
        elif msg["role"] == "user": contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant": contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
    payload = {"contents": contents}
    if system_msg: payload["systemInstruction"] = {"parts": [{"text": system_msg}]}
    resp = requests.post(url, json=payload, stream=True, timeout=300)
    for line in resp.iter_lines():
        if not line: continue
        line_str = line.decode() if isinstance(line, bytes) else line
        if not line_str.startswith("data: "): continue
        try:
            data = json.loads(line_str[6:])
            for c in data.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if p.get("text"): yield p["text"]
        except json.JSONDecodeError:
            continue

def _chat_claude(messages, config, model):
    api_key = resolve_api_key(config)
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY requerida para usar Claude")
    system_msg = None
    claude_msgs = []
    for msg in messages:
        if msg["role"] == "system": system_msg = msg["content"]
        else: claude_msgs.append({"role": msg["role"], "content": msg["content"]})
    temp = config.get("temperature", 0.1)
    payload = {"model": model, "messages": claude_msgs, "max_tokens": 4096, "stream": True, "temperature": temp}
    if system_msg: payload["system"] = system_msg
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    resp = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, stream=True, timeout=300)
    for line in resp.iter_lines():
        if not line: continue
        line_str = line.decode() if isinstance(line, bytes) else line
        if not line_str.startswith("data: "): continue
        try:
            data = json.loads(line_str[6:])
            if data.get("type") == "content_block_delta":
                text = data.get("delta", {}).get("text", "")
                if text: yield text
        except json.JSONDecodeError:
            continue

def chat(messages, stream=True, config=None, model=None):
    if config is None: config = load_config()
    provider = config.get("provider", "ollama")
    actual_model = model or config.get("model", "gemma4:e2b-it-qat")
    if provider == "ollama":
        yield from _chat_ollama(messages, config, actual_model)
    elif provider in ("openai", "opencode-go", "opencode-zen"):
        yield from _chat_openai(messages, config, actual_model)
    elif provider == "gemini":
        yield from _chat_gemini(messages, config, actual_model)
    elif provider == "claude":
        yield from _chat_claude(messages, config, actual_model)
    else:
        raise ValueError(f"Proveedor desconocido: {provider}")

def get_provider_info():
    config = load_config()
    return {"provider": config.get("provider", "ollama"), "model": config.get("model", ""), "api_key_set": bool(resolve_api_key(config))}
