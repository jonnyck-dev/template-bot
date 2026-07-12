import json, os
import numpy as np
KNOWLEDGE_FILE = 'knowledge.json'
EMBEDDINGS_FILE = 'embeddings.json'
_knowledge = None
_embeddings_data = None
_model = None
def get_business_name():
    k = _load_knowledge()
    return k['business_name']
def get_tagline():
    k = _load_knowledge()
    return k.get('tagline', '')
def _load_knowledge():
    global _knowledge
    if _knowledge is None:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            _knowledge = json.load(f)
    return _knowledge
def _load_embeddings():
    global _embeddings_data
    if _embeddings_data is None and os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
            _embeddings_data = json.load(f)
    return _embeddings_data
def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            return None
    return _model
def get_relevant_context(query, k=2):
    knowledge = _load_knowledge()
    sections = knowledge.get('sections', [])
    if not sections:
        return knowledge.get('raw_text', '')
    embeddings_data = _load_embeddings()
    model = _get_model()
    if embeddings_data is None or model is None:
        return knowledge.get('raw_text', '')
    embeddings = np.array(embeddings_data['embeddings'])
    query_vec = model.encode([query])
    dot = np.dot(query_vec, embeddings.T)[0]
    norm_q = np.linalg.norm(query_vec)
    norm_e = np.linalg.norm(embeddings, axis=1)
    sims = dot / (norm_q * norm_e + 1e-10)
    top_indices = np.argsort(sims)[-k:][::-1]
    relevant = [sections[i]['content'] for i in top_indices]
    return '\n\n---\n\n'.join(relevant)
def get_sections_count():
    k = _load_knowledge()
    return len(k.get('sections', []))