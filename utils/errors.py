"""
Error handling utilities for Electronic Medication Administration Record (eMAR).

This module provides custom exceptions and error response formatting.
"""

from flask import jsonify
from typing import Tuple, Any
import logging

logger = logging.getLogger("eMAR")


class eMarError(Exception):
    """Base exception class for eMAR application."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(eMarError):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(eMarError):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class RateLimitError(eMarError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str):
        super().__init__(message, status_code=429)


def error_response(message: str, status_code: int = 500) -> Tuple[Any, int]:
    """
    Create a standardized error response.

    Args:
        message: Error message to return
        status_code: HTTP status code

    Returns:
        Tuple of (JSON response, status code)
    """
    logger.error(f"Error response: {message} (status: {status_code})")
    return jsonify({
        "success": False,
        "error": message
    }), status_code


def success_response(data: Any = None, message: str = None) -> Tuple[Any, int]:
    """
    Create a standardized success response.

    Args:
        data: Data to return in response
        message: Optional success message

    Returns:
        Tuple of (JSON response, status code)
    """
    response = {"success": True}
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return jsonify(response), 200


def handle_exception(e: Exception) -> Tuple[Any, int]:
    """
    Handle exceptions and return appropriate error response.

    Args:
        e: Exception to handle

    Returns:
        Tuple of (JSON response, status code)
    """
    if isinstance(e, eMarError):
        return error_response(e.message, e.status_code)
    else:
        # Log unexpected exceptions with stack trace
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return error_response("An unexpected error occurred", 500)
