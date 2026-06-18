"""
Recommendation and User Semantic Profile Services.
Manages updates to user preference vectors and queries similar items.
"""
import logging
import math
from typing import Any, Dict, List, Optional
from django.contrib.auth import get_user_model

from store.models import Product, Category
from insights.models import ProductEmbedding, CategoryEmbedding, UserSemanticProfile

logger = logging.getLogger(__name__)

User = get_user_model()

# Scoring weights for implicit feedback
EVENT_WEIGHTS = {
    'PRODUCT_VIEWED': 1.0,
    'PRODUCT_LIKED': 3.0,
    'PRODUCT_UNLIKED': -3.0,
    'CART_ITEM_ADDED': 5.0,
    'ORDER_CREATED': 10.0,
}

DECAY_RATE = 0.25  # Lambda for exponential moving average (newer items weigh more)


class RecommendationService:
    """Service class to calculate recommendations and maintain user interest profiles."""

    @staticmethod
    def _normalize_vector(vector: List[float]) -> List[float]:
        """Normalize a vector to unit length (L2 norm = 1.0)."""
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude == 0:
            return vector
        return [x / magnitude for x in vector]

    @staticmethod
    def _dot_product(v1: List[float], v2: List[float]) -> float:
        """Calculate the dot product of two vectors."""
        if len(v1) != len(v2):
            return 0.0
        return sum(x * y for x, y in zip(v1, v2))

    @classmethod
    def update_user_profile(cls, user_id: int, product_id: int, event_type: str) -> None:
        """
        Update a user's semantic preference vector and interest scores based on an event.

        :param user_id: ID of the user
        :param product_id: ID of the product
        :param event_type: The type of event (e.g. PRODUCT_VIEWED, PRODUCT_LIKED)
        """
        weight = EVENT_WEIGHTS.get(event_type)
        if weight is None:
            logger.debug(f"Event type {event_type} has no defined interest weight, skipping.")
            return

        try:
            # Fetch the product and its category
            try:
                product = Product.objects.select_related('category').get(id=product_id)
            except Product.DoesNotExist:
                logger.warning(f"Product {product_id} not found in DB during profile update.")
                return

            category = product.category
            if not category:
                logger.warning(f"Product {product_id} has no category. Skipping update.")
                return

            # Fetch product embedding
            prod_emb = ProductEmbedding.objects.filter(product=product).first()
            product_vector: Optional[List[float]] = prod_emb.embedding_vector if prod_emb else None

            # Fetch or create the user profile
            profile, created = UserSemanticProfile.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'preference_vector': None,
                    'category_interests': {},
                    'product_interests': {}
                }
            )

            # 1. Update Category & Product scores
            cat_id_str = str(category.id)
            prod_id_str = str(product.id)

            # Update category score
            cat_interests = dict(profile.category_interests or {})
            cat_interests[cat_id_str] = max(0.0, float(cat_interests.get(cat_id_str, 0.0)) + weight)
            profile.category_interests = cat_interests

            # Update product score
            prod_interests = dict(profile.product_interests or {})
            prod_interests[prod_id_str] = max(0.0, float(prod_interests.get(prod_id_str, 0.0)) + weight)
            profile.product_interests = prod_interests

            # 2. Merge Product Embedding into User Preference Vector
            if product_vector:
                user_vector = profile.preference_vector

                if not user_vector:
                    # First interaction: copy the product vector and normalize it
                    profile.preference_vector = cls._normalize_vector(product_vector)
                else:
                    # Merge using moving average with decay
                    merged = []
                    for v_old_val, v_prod_val in zip(user_vector, product_vector):
                        merged.append((1.0 - DECAY_RATE) * v_old_val + DECAY_RATE * weight * v_prod_val)

                    profile.preference_vector = cls._normalize_vector(merged)

            profile.save()
            logger.info(f"Updated semantic profile for user {user_id} based on event {event_type} on product {product_id}")

        except Exception as e:
            logger.error(f"Failed to update semantic profile for user {user_id}: {str(e)}")

    @classmethod
    def get_top_categories(cls, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top N semantically matching categories for a user based on preference vector.

        :param user_id: ID of the user
        :param limit: Maximum categories to return
        :return: List of category dicts with similarity scores
        """
        try:
            profile = UserSemanticProfile.objects.filter(user_id=user_id).first()
            if not profile or not profile.preference_vector:
                return []

            user_vector = profile.preference_vector
            active_embeddings = CategoryEmbedding.objects.filter(
                embedding_vector__isnull=False
            ).select_related('category')

            scores = []
            for emb in active_embeddings:
                sim = cls._dot_product(user_vector, emb.embedding_vector)
                scores.append((emb.category, sim))

            # Sort by similarity score descending
            scores.sort(key=lambda x: x[1], reverse=True)
            top_items = scores[:limit]

            return [
                {
                    "category_id": item[0].id,
                    "name": item[0].name,
                    "score": round(item[1], 4)
                }
                for item in top_items
            ]

        except Exception as e:
            logger.error(f"Error retrieving top categories for user {user_id}: {str(e)}")
            return []

    @classmethod
    def get_user_interests_data(cls, user_id: int) -> Dict[str, Any]:
        """
        Get user category and product interest scores resolved with DB details.
        Prioritizes semantic matches from preference vectors.

        :param user_id: ID of the user
        :return: Dict with top_categories and top_products list
        """
        try:
            profile = UserSemanticProfile.objects.filter(user_id=user_id).first()
            if not profile:
                return {"top_categories": [], "top_products": []}

            # 1. Try semantic matching first
            if profile.preference_vector:
                top_cats = cls.get_top_categories(user_id=user_id, limit=5)
                top_prods = cls.get_top_products(user_id=user_id, limit=5)
                if top_cats or top_prods:
                    return {
                        "top_categories": top_cats,
                        "top_products": top_prods
                    }

            # 2. Fall back to raw category interests
            cat_scores = profile.category_interests or {}
            sorted_cat_ids = sorted(cat_scores.keys(), key=lambda k: cat_scores[k], reverse=True)[:5]
            
            categories = {
                str(c.id): c.name 
                for c in Category.objects.filter(id__in=[int(cid) for cid in sorted_cat_ids])
            }
            
            top_categories = [
                {
                    "category_id": int(cid),
                    "name": categories.get(cid, f"Category #{cid}"),
                    "score": round(float(cat_scores[cid]), 2)
                }
                for cid in sorted_cat_ids if cid in categories
            ]

            # Resolve product interests fallback
            prod_scores = profile.product_interests or {}
            sorted_prod_ids = sorted(prod_scores.keys(), key=lambda k: prod_scores[k], reverse=True)[:5]
            
            products = {
                str(p.id): p.name 
                for p in Product.objects.filter(id__in=[int(pid) for pid in sorted_prod_ids])
            }
            
            top_products = [
                {
                    "product_id": int(pid),
                    "name": products.get(pid, f"Product #{pid}"),
                    "score": round(float(prod_scores[pid]), 2)
                }
                for pid in sorted_prod_ids if pid in products
            ]

            return {
                "top_categories": top_categories,
                "top_products": top_products
            }

        except Exception as e:
            logger.error(f"Error fetching user interests data: {str(e)}")
            return {"top_categories": [], "top_products": []}

    @classmethod
    def get_top_products(cls, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top N semantically matching products for a user based on preference vector.

        :param user_id: ID of the user
        :param limit: Maximum products to return
        :return: List of product dicts with similarity scores
        """
        try:
            profile = UserSemanticProfile.objects.filter(user_id=user_id).first()
            if not profile or not profile.preference_vector:
                return []

            user_vector = profile.preference_vector
            active_embeddings = ProductEmbedding.objects.filter(
                embedding_vector__isnull=False,
                product__is_active=True
            ).select_related('product')

            scores = []
            for emb in active_embeddings:
                sim = cls._dot_product(user_vector, emb.embedding_vector)
                scores.append((emb.product, sim))

            # Sort by similarity score descending
            scores.sort(key=lambda x: x[1], reverse=True)
            top_items = scores[:limit]

            return [
                {
                    "product_id": item[0].id,
                    "name": item[0].name,
                    "score": round(item[1], 4)
                }
                for item in top_items
            ]

        except Exception as e:
            logger.error(f"Error retrieving top products for user {user_id}: {str(e)}")
            return []

    @classmethod
    def get_similar_categories(cls, category_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch semantically similar categories based on category embeddings.

        :param category_id: ID of the source category
        :param limit: Maximum similar categories to return
        :return: List of Category details with similarity scores
        """
        try:
            source_emb = CategoryEmbedding.objects.filter(category_id=category_id).first()
            if not source_emb or not source_emb.embedding_vector:
                return []

            src_vector = source_emb.embedding_vector
            other_embeddings = CategoryEmbedding.objects.filter(
                embedding_vector__isnull=False
            ).exclude(category_id=category_id).select_related('category')

            scores = []
            for emb in other_embeddings:
                sim = cls._dot_product(src_vector, emb.embedding_vector)
                scores.append((emb.category, sim))

            scores.sort(key=lambda x: x[1], reverse=True)
            top_items = scores[:limit]

            return [
                {
                    "category_id": item[0].id,
                    "name": item[0].name,
                    "score": round(item[1], 4)
                }
                for item in top_items
            ]

        except Exception as e:
            logger.error(f"Error retrieving similar categories for category {category_id}: {str(e)}")
            return []

    @classmethod
    def reset_user_profile(cls, user_id: int) -> None:
        """
        Reset user's semantic profile interests and preference vector.
        """
        try:
            profile = UserSemanticProfile.objects.filter(user_id=user_id).first()
            if profile:
                profile.preference_vector = None
                profile.category_interests = {}
                profile.product_interests = {}
                profile.save()
                logger.info(f"Reset semantic profile for user {user_id}")
        except Exception as e:
            logger.error(f"Error resetting semantic profile for user {user_id}: {str(e)}")
            raise e
