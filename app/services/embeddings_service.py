from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Initialize the model
@lru_cache()
def get_model():
    return SentenceTransformer('BAAI/bge-small-en-v1.5')

def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for given text using BGE model.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of float values representing the embedding
    """
    return get_model().encode(text).tolist()

