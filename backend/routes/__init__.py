# Backend routes __init__.py
"""
API routes for EcoSound Analyzer backend

This module contains all the Flask blueprints for:
- Audio processing and classification
- Citizen feedback submission
- Noise prediction and forecasting
"""

from .audio import audio_bp
from .feedback import feedback_bp
from .prediction import prediction_bp

__all__ = ['audio_bp', 'feedback_bp', 'prediction_bp']