from sentence_transformers import SentenceTransformer
from researcher_system.core.gpu_manager import DEVICE

model=SentenceTransformer(
"sentence-transformers/all-MiniLM-L6-v2",
device=DEVICE
)

def embed(texts):
    return model.encode(texts,convert_to_tensor=True)
