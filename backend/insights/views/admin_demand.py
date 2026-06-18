from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from collections import defaultdict
import logging

from store.models import Product, Category
from insights.models import UserSemanticProfile

logger = logging.getLogger(__name__)


class AdminDemandForecastView(APIView):
    """API endpoint for superusers to retrieve aggregate product and category demand insights."""

    permission_classes = [permissions.IsAdminUser]

    def get(self, request) -> Response:
        """Fetch and aggregate demand forecasting metrics across all user semantic profiles."""
        try:
            # 1. Fetch all semantic profiles
            profiles = UserSemanticProfile.objects.all()

            # 2. Accumulate interest scores
            product_scores: dict[int, float] = defaultdict(float)
            category_scores: dict[int, float] = defaultdict(float)

            for profile in profiles:
                for pid, score in (profile.product_interests or {}).items():
                    try:
                        product_scores[int(pid)] += float(score)
                    except (ValueError, TypeError):
                        pass
                for cid, score in (profile.category_interests or {}).items():
                    try:
                        category_scores[int(cid)] += float(score)
                    except (ValueError, TypeError):
                        pass

            # 3. Fetch products and categories
            products = {p.id: p for p in Product.objects.all().select_related('category')}
            categories = {c.id: c for c in Category.objects.all()}

            # 4. Build product demand list
            product_demand = []
            for pid, score in product_scores.items():
                if pid in products:
                    prod = products[pid]
                    stock = prod.available_quantity

                    # Determine stock status
                    if stock == 0:
                        stock_status = "OUT OF STOCK"
                        status_color = "red"
                    elif stock < 5:
                        stock_status = "CRITICAL LOW"
                        status_color = "orange"
                    elif stock < 15:
                        stock_status = "LOW STOCK"
                        status_color = "yellow"
                    else:
                        stock_status = "IN STOCK"
                        status_color = "green"

                    # Recommended action: restock if high demand and low stock
                    action = "Restock Immediately" if stock < 10 and score >= 5.0 else "Monitor"

                    product_demand.append({
                        "product_id": prod.id,
                        "name": prod.name,
                        "category_name": prod.category.name,
                        "score": round(score, 1),
                        "stock": stock,
                        "stock_status": stock_status,
                        "status_color": status_color,
                        "action": action
                    })

            # Sort products by score descending
            product_demand.sort(key=lambda x: x["score"], reverse=True)

            # 5. Build category demand list
            category_demand = []
            for cid, score in category_scores.items():
                if cid in categories:
                    cat = categories[cid]
                    category_demand.append({
                        "category_id": cat.id,
                        "name": cat.name,
                        "score": round(score, 1)
                    })
            category_demand.sort(key=lambda x: x["score"], reverse=True)

            return Response({
                "product_demand": product_demand,
                "category_demand": category_demand
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error compiling demand forecast: {str(e)}")
            return Response(
                {"error": "Failed to compile demand forecast data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
