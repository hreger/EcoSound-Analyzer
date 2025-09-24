# Citizen feedback routes
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.db_handler import save_feedback, get_feedback_stats
import re

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    """Submit citizen feedback/noise report"""
    try:
        data = request.get_json()
        
        if not data or 'feedback' not in data:
            return jsonify({'error': 'Feedback text is required'}), 400
        
        feedback_text = data['feedback'].strip()
        
        if not feedback_text:
            return jsonify({'error': 'Feedback cannot be empty'}), 400
        
        if len(feedback_text) > 1000:
            return jsonify({'error': 'Feedback too long (max 1000 characters)'}), 400
        
        # Extract metadata
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        noise_level = data.get('noise_level')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Analyze feedback for noise type and urgency
        analysis = analyze_feedback(feedback_text)
        
        # Prepare feedback entry
        feedback_entry = {
            'feedback': feedback_text,
            'latitude': latitude,
            'longitude': longitude,
            'noise_level': noise_level,
            'timestamp': timestamp,
            'analysis': analysis,
            'status': 'submitted'
        }
        
        # Save to database
        feedback_id = save_feedback(feedback_entry)
        
        response = {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your report! Your feedback helps improve urban noise monitoring.',
            'analysis': analysis
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit feedback: {str(e)}'}), 500

@feedback_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get feedback statistics"""
    try:
        stats = get_feedback_stats()
        
        response = {
            'total_reports': stats.get('total', 0),
            'last_24_hours': stats.get('recent', 0),
            'top_sources': stats.get('sources', []),
            'urgent_reports': stats.get('urgent', 0),
            'average_noise_level': stats.get('avg_noise', 0)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@feedback_bp.route('/recent', methods=['GET'])
def get_recent_feedback():
    """Get recent feedback entries"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get recent feedback from database
        recent_feedback = get_recent_feedback_from_db(limit)
        
        # Anonymize personal information
        anonymized_feedback = []
        for entry in recent_feedback:
            anonymized_entry = {
                'id': entry['id'],
                'feedback': entry['feedback'],
                'timestamp': entry['timestamp'],
                'noise_level': entry.get('noise_level'),
                'analysis': entry.get('analysis', {}),
                'location': {
                    'area': approximate_area(entry.get('latitude'), entry.get('longitude'))
                }
            }
            anonymized_feedback.append(anonymized_entry)
        
        return jsonify({'feedback': anonymized_feedback})
        
    except Exception as e:
        return jsonify({'error': f'Failed to get recent feedback: {str(e)}'}), 500

def analyze_feedback(feedback_text):
    """Analyze feedback text for noise type and urgency"""
    feedback_lower = feedback_text.lower()
    
    # Noise source detection
    noise_sources = []
    if any(word in feedback_lower for word in ['car', 'traffic', 'vehicle', 'truck', 'motorcycle']):
        noise_sources.append('traffic')
    if any(word in feedback_lower for word in ['construction', 'drill', 'hammer', 'building', 'work']):
        noise_sources.append('construction')
    if any(word in feedback_lower for word in ['music', 'party', 'loud', 'neighbor', 'voice']):
        noise_sources.append('human')
    if any(word in feedback_lower for word in ['siren', 'alarm', 'emergency']):
        noise_sources.append('emergency')
    if any(word in feedback_lower for word in ['industrial', 'factory', 'machine', 'equipment']):
        noise_sources.append('industrial')
    
    # Urgency detection
    urgency = 'low'
    if any(word in feedback_lower for word in ['urgent', 'emergency', 'extremely', 'unbearable', 'constant']):
        urgency = 'high'
    elif any(word in feedback_lower for word in ['loud', 'disruptive', 'annoying', 'frequent']):
        urgency = 'medium'
    
    # Time of day detection
    time_indicators = []
    if any(word in feedback_lower for word in ['night', 'evening', 'late']):
        time_indicators.append('night')
    if any(word in feedback_lower for word in ['morning', 'early']):
        time_indicators.append('morning')
    if any(word in feedback_lower for word in ['day', 'afternoon']):
        time_indicators.append('day')
    
    return {
        'noise_sources': noise_sources,
        'urgency': urgency,
        'time_indicators': time_indicators,
        'sentiment': analyze_sentiment(feedback_text)
    }

def analyze_sentiment(text):
    """Simple sentiment analysis"""
    negative_words = ['terrible', 'awful', 'annoying', 'disturbing', 'unbearable', 'loud', 'noise']
    positive_words = ['quiet', 'peaceful', 'better', 'improved', 'good']
    
    text_lower = text.lower()
    negative_count = sum(1 for word in negative_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)
    
    if negative_count > positive_count:
        return 'negative'
    elif positive_count > negative_count:
        return 'positive'
    else:
        return 'neutral'

def approximate_area(latitude, longitude):
    """Convert coordinates to approximate area for privacy"""
    if latitude is None or longitude is None:
        return 'Unknown'
    
    # Round coordinates to approximate area (reduces precision for privacy)
    approx_lat = round(latitude, 2)
    approx_lng = round(longitude, 2)
    
    return f"Area near {approx_lat}, {approx_lng}"

def get_recent_feedback_from_db(limit):
    """Get recent feedback from database (mock implementation)"""
    # This would connect to actual database in production
    # For demo, return mock data
    mock_feedback = [
        {
            'id': 1,
            'feedback': 'Construction noise very loud in the morning',
            'timestamp': '2025-09-24T09:30:00',
            'noise_level': 85,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'analysis': {'noise_sources': ['construction'], 'urgency': 'medium'}
        },
        {
            'id': 2,
            'feedback': 'Traffic noise from highway keeps me awake at night',
            'timestamp': '2025-09-24T02:15:00',
            'noise_level': 72,
            'latitude': 40.7589,
            'longitude': -73.9851,
            'analysis': {'noise_sources': ['traffic'], 'urgency': 'high'}
        }
    ]
    
    return mock_feedback[:limit]