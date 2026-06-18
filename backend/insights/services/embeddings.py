import logging
from typing import List, Optional
import numpy as np
from django.conf import settings
from langchain_community.embeddings import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingService:
    """LangChain-based embedding service using Ollama."""

    def __init__(self) -> None:
        """Initialize the Ollama embedding client."""
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_EMBEDDING_MODEL', 'qwen3-embedding:0.6b')

        try:
            self.embeddings = OllamaEmbeddings(
                base_url=self.base_url,
                model=self.model
            )
            logger.info(f"EmbeddingService initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OllamaEmbeddings: {str(e)}")
            self.embeddings = None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using Ollama via LangChain."""
        if not self.embeddings:
            logger.error("Embeddings client not initialized")
            return None

        try:
            if not text or not isinstance(text, str):
                logger.warning("Invalid text input for embedding")
                return None

            embedding = self.embeddings.embed_query(text.strip())
            logger.debug(f"Generated embedding of dimension: {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        if not self.embeddings:
            return [None] * len(texts)

        try:
            embeddings = self.embeddings.embed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error in batch embedding: {str(e)}")
            return [None] * len(texts)

    @staticmethod
    def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(vec1, vec2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
