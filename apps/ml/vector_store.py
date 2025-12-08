import faiss, numpy as np, os, pickle

INDEX_PATH = '/data/faiss_index.index'
META_PATH = '/data/faiss_meta.pkl'

def load_index(dim):
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, 'rb') as f:
            meta = pickle.load(f)
    else:
        index = faiss.IndexFlatIP(dim)
        meta = []
    return index, meta

def add_vector_to_index(kind, obj_id, vector):
    dim = len(vector)
    index, meta = load_index(dim)
    vec = np.array([vector]).astype('float32')
    index.add(vec)
    meta.append((kind, obj_id))
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, 'wb') as f:
        pickle.dump(meta, f)

def search(query_vector, k=5):
    index, meta = load_index(len(query_vector))
    D, I = index.search(np.array([query_vector]).astype('float32'), k)
    results = []
    for i in I[0]:
        if i < len(meta):
            results.append(meta[i])
    return results