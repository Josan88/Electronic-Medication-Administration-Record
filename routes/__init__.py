"""
Routes Module

This module provides centralized blueprint registration for the eMAR application.
It organizes routes into logical modules:
- patients: Patient management endpoints
- prescriptions: Prescription management endpoints
- tracking: Medication tracking endpoints
- queue: Queue monitoring and management endpoints
"""

from flask import Flask
from .patients import patients_bp
from .prescriptions import prescriptions_bp, init_prescription_routes
from .tracking import tracking_bp
from .queue import queue_bp


def register_blueprints(app: Flask, persistent_queue):
    """
    Register all application blueprints with the Flask app.
    
    Args:
        app: Flask application instance
        persistent_queue: Global persistent queue instance
    """
    # Initialize prescription routes with queue access
    init_prescription_routes(persistent_queue)
    
    # Register all blueprints
    app.register_blueprint(patients_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(queue_bp)
