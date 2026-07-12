import json, os, sys
KNOWLEDGE_FILE = 'knowledge.json'
EMBEDDINGS_FILE = 'embeddings.json'
def main():
    if not os.path.exists(KNOWLEDGE_FILE):
        print(f'Error: {KNOWLEDGE_FILE} no encontrado. Ejecuta build_knowledge.py primero.')
        sys.exit(1)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print('Error: sentence-transformers no instalado. Ejecuta: pip install sentence-transformers')
        sys.exit(1)
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        knowledge = json.load(f)
    sections = knowledge.get('sections', [])
    if not sections:
        print('No hay secciones en la base de conocimiento.')
        sys.exit(1)
    texts = [s['content'] for s in sections]
    print(f'Generando embeddings para {len(texts)} secciones...')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts).tolist()
    data = {'embeddings': embeddings, 'section_indices': list(range(len(sections)))}
    with open(EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'Embeddings guardados: {len(texts)} secciones -> {EMBEDDINGS_FILE}')
if __name__ == '__main__':
    main()