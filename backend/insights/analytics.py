"""Analytics utilities for extracting user info from requests."""
from typing import Any, Dict, Optional


def get_client_ip(request) -> str:
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_user_agent(request) -> str:
    """Extract user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')


def extract_user_info(request, user) -> Dict[str, Any]:
    """
    Extract user information for analytics from request and user object.

    Returns:
        Dict with keys: email, name, ip_address, user_agent
    """
    return {
        'email': user.email,
        'name': user.first_name or user.username,
        'ip_address': get_client_ip(request),
        'user_agent': get_user_agent(request),
    }
