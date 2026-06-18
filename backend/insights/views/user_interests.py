from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from insights.services import RecommendationService
import logging

logger = logging.getLogger(__name__)


class UserInterestsView(APIView):
    """Retrieves user's top categories and products interest profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        """Handle GET request to retrieve user interest scores."""
        try:
            user_id = request.user.id
            data = RecommendationService.get_user_interests_data(user_id=user_id)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching user interests: {str(e)}")
            return Response(
                {"error": "Failed to fetch user interest profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request) -> Response:
        """Handle DELETE request to reset/clear user interest profile."""
        try:
            user_id = request.user.id
            RecommendationService.reset_user_profile(user_id=user_id)
            return Response({"success": "User interest profile cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error resetting user interests: {str(e)}")
            return Response(
                {"error": "Failed to reset user interest profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
