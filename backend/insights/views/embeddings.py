from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from insights.chat import SmartSearchChat
import logging

logger = logging.getLogger(__name__)


class SmartSearchChatView(APIView):
    """AI-powered natural language product search"""

    def post(self, request):
        query = request.data.get('query', '').strip()
        limit = int(request.data.get('limit', 16))

        if not query:
            return Response({
                'message': 'What are you looking for?',
                'results': [],
                'total_results': 0,
            })

        try:
            result = SmartSearchChat().chat(query=query, limit=limit)
            return Response(result)
        except Exception as e:
            logger.error(f"Chat search error: {str(e)}")
            return Response(
                {'message': f'Search error: {str(e)}', 'results': [], 'total_results': 0},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
