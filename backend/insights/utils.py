import logging
from typing import List, Dict, Any, Optional
import numpy as np
from django.conf import settings
from langchain_community.embeddings import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingService:
    """LangChain-based embedding service using Ollama"""

    def __init__(self):
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
        """Generate embedding for text using Ollama via LangChain"""
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
        """Generate embeddings for multiple texts"""
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
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(vec1, vec2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def parse_search_intent(self, query: str) -> Dict[str, Any]:
        """Parse user search intent: extract price range, category, quantity filters"""
        import re

        intent = {
            'search_text': query,
            'min_price': None,
            'max_price': None,
            'category': None,
            'min_quantity': None,
        }

        query_lower = query.lower()

        # Price extraction: "less than 50", "under 100", "price < 50", "50 rupees"
        price_patterns = [
            (r'(?:less than|under|below|<)\s*(\d+)', 'max'),
            (r'(?:more than|above|greater than|>)\s*(\d+)', 'min'),
            (r'(?:price\s*(?:is\s*)?(?:between|from))\s*(\d+)\s*(?:to|-)\s*(\d+)', 'range'),
            (r'(\d+)\s*(?:rupees|rs\.?|dollar|usd)', 'max'),
        ]

        for pattern, type_ in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if type_ == 'max':
                    intent['max_price'] = float(match.group(1))
                elif type_ == 'min':
                    intent['min_price'] = float(match.group(1))
                elif type_ == 'range':
                    intent['min_price'] = float(match.group(1))
                    intent['max_price'] = float(match.group(2))
                break

        # Category extraction
        categories = ['laptop', 'phone', 'camera', 'headphone', 'watch', 'tablet', 'speaker', 'charger', 'cable']
        for cat in categories:
            if cat in query_lower:
                intent['category'] = cat
                break

        # Quantity extraction: "stock", "available", "in stock"
        if any(word in query_lower for word in ['stock', 'available', 'quantity', 'qty']):
            intent['min_quantity'] = 1

        return intent

    def search(self, query: str, limit: int = 10, threshold: float = 0.5) -> Dict[str, Any]:
        """Smart search: Text → Intent Parse → Embedding → Filter → Results"""
        from insights.models import ProductEmbedding
        from store.models import Product

        query = query.strip()

        if not query:
            return {'error': 'Query required', 'results': [], 'total_results': 0}

        limit = min(max(1, limit), 100)
        threshold = max(0.0, min(1.0, threshold))

        try:
            # Step 1: Parse user intent (price, category, qty)
            intent = self.parse_search_intent(query)
            logger.info(f"Search intent: {intent}")

            # Step 2: Get semantic embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return {'error': 'Failed to generate embedding', 'results': [], 'total_results': 0}

            # Step 3: Get embeddings with product details
            embeddings_qs = ProductEmbedding.objects.filter(
                embedding_vector__isnull=False
            ).select_related('product')

            # Step 4: Apply filters and semantic search
            results = []
            for emb in embeddings_qs:
                product = emb.product

                # Apply price filter
                if intent['max_price'] and product.base_price > intent['max_price']:
                    continue
                if intent['min_price'] and product.base_price < intent['min_price']:
                    continue

                # Apply category filter
                if intent['category'] and intent['category'] not in product.category.name.lower():
                    continue

                # Apply quantity filter
                if intent['min_quantity'] and product.available_quantity < intent['min_quantity']:
                    continue

                # Calculate similarity
                similarity = self.calculate_similarity(query_embedding, emb.embedding_vector)

                if similarity >= threshold:
                    results.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'slug': product.slug,
                        'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
                        'base_price': float(product.base_price),
                        'discount_percentage': float(product.discount_percentage),
                        'available_quantity': product.available_quantity,
                        'category': product.category.name,
                        'similarity_score': round(similarity, 3),
                        'is_active': product.is_active,
                    })

            # Step 5: Sort and limit
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            results = results[:limit]

            logger.info(f"Search '{query}': {len(results)} results (price: {intent['min_price']}-{intent['max_price']}, cat: {intent['category']})")

            return {
                'query': query,
                'filters_applied': {
                    'price_range': (intent['min_price'], intent['max_price']),
                    'category': intent['category'],
                    'in_stock': intent['min_quantity'] is not None,
                },
                'results': results,
                'total_results': len(results),
            }

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {'error': str(e), 'results': [], 'total_results': 0}
