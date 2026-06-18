import re
import logging
from typing import Dict, Any

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from insights.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# LangChain intent nodes
# Each node receives the shared state dict, enriches it, and returns it.
# ─────────────────────────────────────────────────────────────────────────────

def _node_price(state: Dict) -> Dict:
    """
    Extracts price constraints.
    Handles typos: "then/than", missing currency symbols, ranges.
    Examples:
      "less then 200"  → price_max=200
      "under ₹500"     → price_max=500
      "above 1000"     → price_min=1000
      "between 100 and 500" → price_min=100, price_max=500
    """
    q = state["query"].lower()
    # normalise currency symbols so patterns are simpler
    q = re.sub(r'₹|rs\.?|inr', '', q)

    # Range first (must come before single-side to avoid partial match)
    # handles: between, inbetween, in between, inbeetween, from
    range_pat = r'(?:in\s*be+twe+en|between|from)\s*(\d+(?:\.\d+)?)\s*(?:to|and|-)\s*(\d+(?:\.\d+)?)'
    m = re.search(range_pat, q)
    if m:
        state["price_min"] = float(m.group(1))
        state["price_max"] = float(m.group(2))
        return state

    # Less-than / max  (allow "then" typo)
    max_pat = r'(?:less\s+th[ae]n|under|below|cheaper\s+th[ae]n|<)\s*(\d+(?:\.\d+)?)'
    m = re.search(max_pat, q)
    if m:
        state["price_max"] = float(m.group(1))
        return state

    # Greater-than / min  (allow "then" typo)
    min_pat = r'(?:more\s+th[ae]n|above|greater\s+th[ae]n|over|>)\s*(\d+(?:\.\d+)?)'
    m = re.search(min_pat, q)
    if m:
        state["price_min"] = float(m.group(1))
        return state

    # Bare number with "rupees" after
    m = re.search(r'(\d+(?:\.\d+)?)\s*rupees?', q)
    if m:
        state["price_max"] = float(m.group(1))

    return state


def _node_category(state: Dict) -> Dict:
    """
    Detects category from query by matching against actual DB category names.
    Falls back to a hardcoded keyword list.
    """
    from store.models import Category

    q = state["query"].lower()

    # Try to match against actual category names in DB
    for cat in Category.objects.values("id", "name"):
        if cat["name"].lower() in q or q in cat["name"].lower():
            state["category_id"] = cat["id"]
            state["category_name"] = cat["name"]
            return state

    # Keyword fallback (catches singular/plural variants)
    keywords = {
        "laptop": ["laptop", "notebooks"],
        "phone": ["phone", "mobile", "smartphone"],
        "camera": ["camera", "dslr", "lens"],
        "headphone": ["headphone", "earphone", "earbuds", "headset"],
        "watch": ["watch", "smartwatch"],
        "tablet": ["tablet", "ipad"],
        "speaker": ["speaker", "bluetooth speaker"],
        "charger": ["charger", "adapter"],
        "bag": ["bag", "backpack", "purse"],
    }
    for cat_name, terms in keywords.items():
        if any(t in q for t in terms):
            state["category_name"] = cat_name
            break

    return state


def _node_stock(state: Dict) -> Dict:
    """Detects if user wants in-stock products only."""
    q = state["query"].lower()
    state["only_in_stock"] = any(kw in q for kw in [
        "in stock", "available", "stock mein", "available hai", "stocked"
    ])
    return state


def _node_sort(state: Dict) -> Dict:
    """Detects sort preference from query."""
    q = state["query"].lower()
    if any(w in q for w in ["cheapest", "lowest price", "budget", "sabse sasta", "affordable"]):
        state["sort_by"] = "price_asc"
    elif any(w in q for w in ["expensive", "premium", "highest", "best quality", "most costly"]):
        state["sort_by"] = "price_desc"
    else:
        state["sort_by"] = "relevance"
    return state


# ─────────────────────────────────────────────────────────────────────────────
# LangChain LCEL pipeline  (4 sequential nodes)
# ─────────────────────────────────────────────────────────────────────────────

_intent_chain = (
    RunnablePassthrough()
    | RunnableLambda(_node_price)
    | RunnableLambda(_node_category)
    | RunnableLambda(_node_stock)
    | RunnableLambda(_node_sort)
)


def parse_intent(query: str) -> Dict:
    return _intent_chain.invoke({
        "query": query,
        "price_min": None,
        "price_max": None,
        "category_id": None,
        "category_name": None,
        "only_in_stock": False,
        "sort_by": "relevance",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Friendly response builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_message(query: str, intent: Dict, count: int) -> str:
    if count == 0:
        hints = []
        if intent["price_max"]:
            hints.append(f"under ₹{int(intent['price_max'])}")
        if intent["category_name"]:
            hints.append(intent["category_name"])
        hint_str = " ".join(hints)
        return f'No products found{" " + hint_str if hint_str else ""}. Try different keywords!'

    parts = []
    if intent["price_min"] and intent["price_max"]:
        parts.append(f"between ₹{int(intent['price_min'])}–₹{int(intent['price_max'])}")
    elif intent["price_max"]:
        parts.append(f"under ₹{int(intent['price_max'])}")
    elif intent["price_min"]:
        parts.append(f"above ₹{int(intent['price_min'])}")

    if intent["category_name"]:
        parts.append(intent["category_name"])
    if intent["only_in_stock"]:
        parts.append("in stock")

    suffix = f" — {', '.join(parts)}" if parts else f' matching "{query}"'
    return f'Found {count} product{"s" if count > 1 else ""}{suffix}!'


# ─────────────────────────────────────────────────────────────────────────────
# Main search class
# ─────────────────────────────────────────────────────────────────────────────

class SmartSearch:

    def __init__(self):
        self.service = EmbeddingService()

    def search(self, query: str, limit: int = 16) -> Dict[str, Any]:
        query = query.strip()
        if not query:
            return {"message": "What are you looking for?", "results": [], "total_results": 0}

        # Step 1: parse intent through LangChain chain
        intent = parse_intent(query)
        logger.info(f"Search intent parsed: {intent}")

        has_price_filter = intent["price_min"] is not None or intent["price_max"] is not None
        has_category_filter = intent["category_id"] or intent["category_name"]

        # Step 2: generate query embedding
        query_embedding = self.service.generate_embedding(query)
        if not query_embedding:
            return {
                "message": "AI search unavailable — Ollama may not be running.",
                "results": [],
                "total_results": 0,
            }

        # Step 3: fetch all stored embeddings
        from insights.models import ProductEmbedding
        qs = ProductEmbedding.objects.filter(
            embedding_vector__isnull=False,
            product__is_active=True,
        ).select_related("product__category")

        # Step 4: apply hard filters + compute similarity score
        # When explicit filters exist, lower semantic threshold so filter
        # results always show regardless of phrasing similarity.
        semantic_threshold = 0.2 if (has_price_filter or has_category_filter) else 0.4

        results = []
        for emb in qs:
            p = emb.product

            # Hard filter: price max
            if intent["price_max"] is not None and float(p.base_price) > intent["price_max"]:
                continue

            # Hard filter: price min
            if intent["price_min"] is not None and float(p.base_price) < intent["price_min"]:
                continue

            # Hard filter: category (by DB id first, then name keyword)
            if intent["category_id"]:
                if p.category_id != intent["category_id"]:
                    continue
            elif intent["category_name"]:
                if intent["category_name"].lower() not in p.category.name.lower():
                    continue

            # Hard filter: stock
            if intent["only_in_stock"] and p.available_quantity < 1:
                continue

            # Semantic score
            score = self.service.calculate_similarity(query_embedding, emb.embedding_vector)
            if score < semantic_threshold:
                continue

            results.append({**self._fmt(p), "similarity_score": round(score, 3)})

        # Step 5: sort
        if intent["sort_by"] == "price_asc":
            results.sort(key=lambda x: x["base_price"])
        elif intent["sort_by"] == "price_desc":
            results.sort(key=lambda x: x["base_price"], reverse=True)
        else:
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

        results = results[:limit]

        return {
            "message": _build_message(query, intent, len(results)),
            "results": results,
            "total_results": len(results),
            "filters_applied": {
                "price_min": intent["price_min"],
                "price_max": intent["price_max"],
                "category": intent["category_name"],
                "in_stock": intent["only_in_stock"],
                "sort_by": intent["sort_by"],
            },
            "query": query,
        }

    @staticmethod
    def _fmt(p) -> Dict:
        from store.models import ProductImage
        img = ProductImage.objects.filter(
            product=p, is_primary=True
        ).values_list("image_url", flat=True).first()
        return {
            "product_id": p.id,
            "product_name": p.name,
            "slug": p.slug,
            "description": (p.description[:90] + "…") if len(p.description) > 90 else p.description,
            "base_price": float(p.base_price),
            "discount_percentage": float(p.discount_percentage),
            "available_quantity": p.available_quantity,
            "category": p.category.name,
            "image": img,
        }
