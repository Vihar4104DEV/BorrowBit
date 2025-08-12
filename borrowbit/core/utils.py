"""
Utility functions for the rental backend application.
"""
from typing import Any, Dict, Optional
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

# def format_validation_errors(errors):
#     """
#     Convert Django validation errors into user-friendly messages.
#     """
#     if isinstance(errors, dict):
#         error_messages = []
#         for field, field_errors in errors.items():
#             if isinstance(field_errors, list):
#                 for error in field_errors:
#                     if hasattr(error, 'code'):
#                         if error.code == 'required':
#                             error_messages.append(f"{field.replace('_', ' ').title()} is required.")
#                         elif error.code == 'blank':
#                             error_messages.append(f"{field.replace('_', ' ').title()} cannot be blank.")
#                         elif error.code == 'invalid':
#                             error_messages.append(f"{field.replace('_', ' ').title()} is invalid.")
#                         elif error.code == 'unique':
#                             error_messages.append(f"{field.replace('_', ' ').title()} already exists.")
#                         elif error.code == 'min_length':
#                             error_messages.append(f"{field.replace('_', ' ').title()} is too short.")
#                         else:
#                             error_messages.append(f"{field.replace('_', ' ').title()}: {str(error)}")
#                     else:
                        
#                         error_messages.append(f"{field.replace('_', ' ').title()}: {str(error)}")
#             else:
#                 error_messages.append(f"{field.replace('_', ' ').title()}: {str(field_errors)}")
#         return " ".join(error_messages)
#     elif isinstance(errors, str):
#         return errors
#     else:
#         return str(errors)


def format_validation_errors(errors):
    """
    Convert Django validation errors into user-friendly messages.
    """
    if isinstance(errors, dict):
        # Special handling if the first key is "non_field_errors"
        first_key = next(iter(errors), None)
        if first_key == "non_field_errors" and isinstance(errors[first_key], list) and errors[first_key]:
            return str(errors[first_key][0])  # Return only the first error message

        error_messages = []
        for field, field_errors in errors.items():
            if isinstance(field_errors, list):
                for error in field_errors:
                    if hasattr(error, 'code'):
                        if error.code == 'required':
                            error_messages.append(f"{field.replace('_', ' ').title()} is required.")
                        elif error.code == 'blank':
                            error_messages.append(f"{field.replace('_', ' ').title()} cannot be blank.")
                        elif error.code == 'invalid':
                            error_messages.append(f"{field.replace('_', ' ').title()} is invalid.")
                        elif error.code == 'unique':
                            error_messages.append(f"{field.replace('_', ' ').title()} already exists.")
                        elif error.code == 'min_length':
                            error_messages.append(f"{field.replace('_', ' ').title()} is too short.")
                        else:
                            error_messages.append(f"{field.replace('_', ' ').title()}: {str(error)}")
                    else:
                        error_messages.append(f"{field.replace('_', ' ').title()}: {str(error)}")
            else:
                error_messages.append(f"{field.replace('_', ' ').title()}: {str(field_errors)}")
        return " ".join(error_messages)
    elif isinstance(errors, str):
        return errors
    else:
        return str(errors)

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

def error_response(message: str, status_code: int = status.HTTP_400_BAD_REQUEST, errors: Any = None) -> Response:
    """
    Create an error response with optional validation errors
    """
    if errors:
        formatted_message = format_validation_errors(errors)
        return make_response(False, formatted_message, status_code=status_code)
    return make_response(False, message, status_code=status_code)

def validation_error_response(errors: Any, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """
    Create a validation error response
    """
    formatted_message = format_validation_errors(errors)
    return make_response(False, formatted_message, status_code=status_code)

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


def prepare_user_data(user: Any) -> Dict[str, Optional[Any]]:
    """
    Build a consistent user payload for API responses.
    Any missing attribute is returned as None.
    """
    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "phone_number": getattr(user, "phone_number", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "prefix": getattr(user, "prefix", None),
        "is_verified": getattr(user, "is_verified", None),
        "email_verified_at": getattr(user, "email_verified_at", None),
        "phone_verified_at": getattr(user, "phone_verified_at", None),
        "is_active": getattr(user, "is_active", None),
        "address_line1": getattr(user, "address_line1", None),
        "address_line2": getattr(user, "address_line2", None),
        "city": getattr(user, "city", None),
        "state": getattr(user, "state", None),
        "country": getattr(user, "country", None),
        "zip_code": getattr(user, "zip_code", None),
        "address": getattr(user, "address", None),
        "profile_picture": getattr(user, "profile_picture", None),
        "is_email_verified": getattr(user, "is_email_verified", None),
        "is_phone_verified": getattr(user, "is_phone_verified", None),
        "date_of_birth": getattr(user, "date_of_birth", None),
        "gender": getattr(user, "gender", None),
        "user_role": user.roles.filter(is_active=True).values_list("role", flat=True),
        
    }