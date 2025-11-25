"""
Queue Management Routes

This module contains Flask routes for monitoring and managing the prescription queue
and ThingSpeak synchronization.
"""

from flask import Blueprint, jsonify
from services.queue_service import persistent_queue
from services.sync_service import sync_queue
from services.thingspeak_bulk_service import thingspeak_bulk_service
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


@queue_bp.route("/sync-status", methods=["GET"])
def get_sync_status():
    """
    Get ThingSpeak synchronization status.
    
    Returns:
        JSON response with sync status information including:
        - Pending sync operations
        - Failed sync operations
        - Last synced entry IDs per channel
        - Sync statistics
    """
    try:
        status = sync_queue.get_status()
        return success_response(data=status)
    except Exception as e:
        return error_response(str(e), 500)


@queue_bp.route("/sync-clear-failed", methods=["POST"])
def clear_failed_sync_items():
    """
    Clear all failed sync items from the queue.
    
    Returns:
        JSON response with number of items cleared
    """
    try:
        count = sync_queue.clear_failed_items()
        return success_response(
            message=f"Cleared {count} failed sync items",
            data={"cleared_count": count}
        )
    except Exception as e:
        return error_response(str(e), 500)


@queue_bp.route("/thingspeak-health", methods=["GET"])
def get_thingspeak_health():
    """
    Get ThingSpeak backup database health status.
    
    Uses REST API to check status of all configured channels.
    
    Returns:
        JSON response with health status for each ThingSpeak channel
    """
    try:
        health = thingspeak_bulk_service.health_check()
        return success_response(data=health)
    except Exception as e:
        return error_response(str(e), 500)
