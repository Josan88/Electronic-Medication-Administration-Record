"""
Queue Management Routes

This module contains Flask routes for monitoring and managing the prescription queue.
"""

from flask import Blueprint, jsonify
from services.queue_service import persistent_queue
from utils.errors import success_response, error_response

queue_bp = Blueprint('queue', __name__, url_prefix='/api/queue')


@queue_bp.route("/status", methods=["GET"])
def get_queue_status():
    """
    Get current queue status including size, failed items, and statistics.
    
    Returns:
        JSON response with queue status information
    """
    try:
        status = persistent_queue.get_status()
        return success_response(data=status)
    except Exception as e:
        return error_response(str(e), 500)


@queue_bp.route("/clear-failed", methods=["POST"])
def clear_failed_items():
    """
    Clear all failed items from the queue.
    
    Returns:
        JSON response with number of items cleared
    """
    try:
        count = persistent_queue.clear_failed_items()
        return success_response(
            message=f"Cleared {count} failed items",
            data={"cleared_count": count}
        )
    except Exception as e:
        return error_response(str(e), 500)
