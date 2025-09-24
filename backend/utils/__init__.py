# Backend utils __init__.py
"""
Utility modules for EcoSound Analyzer backend

This module contains utility functions for:
- Audio feature extraction (MFCC, spectral, temporal features)
- Database operations (SQLite with audio metadata, feedback, predictions)
- Data processing and analysis helpers
"""

from .audio_features import (
    extract_mfcc_features,
    extract_spectral_features,
    extract_temporal_features,
    extract_noise_level_features,
    validate_audio_file
)

from .db_handler import (
    save_audio_metadata,
    save_feedback,
    get_feedback_stats,
    get_historical_data,
    DatabaseHandler
)

__all__ = [
    'extract_mfcc_features',
    'extract_spectral_features', 
    'extract_temporal_features',
    'extract_noise_level_features',
    'validate_audio_file',
    'save_audio_metadata',
    'save_feedback',
    'get_feedback_stats',
    'get_historical_data',
    'DatabaseHandler'
]