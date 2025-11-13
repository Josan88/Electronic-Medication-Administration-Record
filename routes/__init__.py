"""
Routes Module

This module provides centralized blueprint registration for the eMAR application.
It organizes routes into logical modules:
- patients: Patient management endpoints
- prescriptions: Prescription management endpoints
- tracking: Medication tracking endpoints
"""

from flask import Flask
from .patients import patients_bp
from .prescriptions import prescriptions_bp, init_prescription_routes
from .tracking import tracking_bp


def register_blueprints(app: Flask, prescription_queue, queue_lock):
    """
    Register all application blueprints with the Flask app.
    
    Args:
        app: Flask application instance
        prescription_queue: Global prescription queue (deque)
        queue_lock: Global queue lock (Lock)
    """
    # Initialize prescription routes with queue access
    init_prescription_routes(prescription_queue, queue_lock)
    
    # Register all blueprints
    app.register_blueprint(patients_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(tracking_bp)
