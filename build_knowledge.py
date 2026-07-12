import os
import json
import glob

KNOWLEDGE_DIR = "CONOCIMIENTOBASE"
OUTPUT_FILE = "knowledge.json"
CONFIG_FILE = "config.json"

# Load config
config = {"business_name": "Mi Negocio", "tagline": "", "language": "es"}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config.update(json.load(f))

sections = []
md_files = sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")))

for filepath in md_files:
    filename = os.path.basename(filepath)
    topic = filename.replace(".md", "").split("-", 1)[1] if "-" in filename else filename.replace(".md", "")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    sections.append({"topic": topic, "file": filename, "content": content})

knowledge = {
    "business_name": config["business_name"],
    "tagline": config["tagline"],
    "language": config["language"],
    "sections": sections,
    "raw_text": "\n\n---\n\n".join([s["content"] for s in sections])
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(knowledge, f, ensure_ascii=False, indent=2)

print(f"Knowledge base compiled: {len(sections)} sections -> {OUTPUT_FILE}")
print(f"Business: {knowledge['business_name']}")
print(f"Total characters in raw_text: {len(knowledge['raw_text'])}")
