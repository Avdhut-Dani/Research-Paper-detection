from transformers import pipeline
from core.gpu_manager import DEVICE

detector=pipeline(
"text-classification",
model="roberta-large-mnli",
device=0 if DEVICE=="cuda" else -1
)

def contradiction(claim,evidence):
    return detector(f"{claim} </s></s> {evidence}")
