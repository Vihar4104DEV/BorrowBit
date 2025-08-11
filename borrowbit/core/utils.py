"""
Utility functions for the rental backend application.
"""
from typing import Any, Dict, Optional
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

def make_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    status_code: int = status.HTTP_200_OK
) -> Response:
    """
    Create a standardized API response
    """
    response_data = {
        "success": success,
        "message": message,
        "data": data or {}
    }
    return Response(response_data, status=status_code)

def success_response(message: str, data: Optional[Any] = None) -> Response:
    """
    Create a success response
    """
    return make_response(True, message, data)

def error_response(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """
    Create an error response
    """
    return make_response(False, message, status_code=status_code)

def cache_key_generator(prefix: str, identifier: str) -> str:
    """
    Generate a standardized cache key
    """
    return f"{prefix}:{identifier}"

def set_cache_data(key: str, data: Any, timeout: int = 300) -> None:
    """
    Set data in cache with timeout (default 5 minutes)
    """
    cache.set(key, data, timeout)

def get_cache_data(key: str) -> Optional[Any]:
    """
    Get data from cache
    """
    return cache.get(key)

def delete_cache_data(key: str) -> None:
    """
    Delete data from cache
    """
    cache.delete(key)
