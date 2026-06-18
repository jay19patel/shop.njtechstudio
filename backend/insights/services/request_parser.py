"""Utilities for extracting user info and request metadata for analytics."""
from typing import Any, Dict


class RequestParserService:
    """Service to extract client properties and user details from HttpRequests."""

    @staticmethod
    def get_client_ip(request: Any) -> str:
        """
        Extract client IP address from request.
        
        :param request: Django HttpRequest object
        :return: Client IP address string
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return str(x_forwarded_for.split(',')[0].strip())
        return str(request.META.get('REMOTE_ADDR', ''))

    @staticmethod
    def get_user_agent(request: Any) -> str:
        """
        Extract user agent from request.
        
        :param request: Django HttpRequest object
        :return: User agent string
        """
        return str(request.META.get('HTTP_USER_AGENT', ''))

    @classmethod
    def extract_user_info(cls, request: Any, user: Any) -> Dict[str, Any]:
        """
        Extract user information for analytics from request and user object.

        :param request: Django HttpRequest object
        :param user: Django User object
        :return: Dict with keys: email, name, ip_address, user_agent
        """
        return {
            'email': user.email,
            'name': user.first_name or user.username,
            'ip_address': cls.get_client_ip(request),
            'user_agent': cls.get_user_agent(request),
        }
