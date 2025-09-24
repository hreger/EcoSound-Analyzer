# Noise prediction routes
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
from models.classifier import AudioClassifier
from utils.db_handler import get_historical_data

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/forecast', methods=['POST'])
def forecast_noise():
    """Generate noise level predictions"""
    try:
        data = request.get_json()
        
        # Extract parameters
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        time_horizon = data.get('time_horizon', 1)  # hours
        weather_conditions = data.get('weather', 'clear')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        # Get historical data for the location
        historical_data = get_historical_data(latitude, longitude, days=30)
        
        # Generate predictions
        predictions = generate_noise_predictions(
            latitude, longitude, time_horizon, weather_conditions, historical_data
        )
        
        response = {
            'success': True,
            'location': {'latitude': latitude, 'longitude': longitude},
            'time_horizon_hours': time_horizon,
            'weather_conditions': weather_conditions,
            'predictions': predictions,
            'confidence_interval': calculate_confidence_interval(predictions),
            'model_version': '1.0.0'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@prediction_bp.route('/trends', methods=['GET'])
def get_noise_trends():
    """Get noise trends for analysis"""
    try:
        # Get query parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        days = request.args.get('days', 7, type=int)
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        # Get historical trends
        trends = analyze_noise_trends(latitude, longitude, days)
        
        response = {
            'location': {'latitude': latitude, 'longitude': longitude},
            'analysis_period_days': days,
            'trends': trends,
            'peak_hours': identify_peak_hours(trends),
            'seasonal_patterns': identify_seasonal_patterns(trends)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Trend analysis failed: {str(e)}'}), 500

@prediction_bp.route('/hotspots', methods=['GET'])
def get_noise_hotspots():
    """Identify noise pollution hotspots"""
    try:
        # Get query parameters
        radius_km = request.args.get('radius', 5.0, type=float)
        threshold_db = request.args.get('threshold', 70, type=int)
        time_period = request.args.get('period', 'day')  # day, week, month
        
        # Analyze hotspots
        hotspots = identify_noise_hotspots(radius_km, threshold_db, time_period)
        
        response = {
            'parameters': {
                'radius_km': radius_km,
                'threshold_db': threshold_db,
                'time_period': time_period
            },
            'hotspots': hotspots,
            'total_hotspots': len(hotspots),
            'severity_distribution': calculate_severity_distribution(hotspots)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Hotspot analysis failed: {str(e)}'}), 500

def generate_noise_predictions(lat, lng, hours, weather, historical_data):
    """Generate noise level predictions using historical patterns and weather"""
    predictions = []
    current_time = datetime.now()
    
    for i in range(hours):
        future_time = current_time + timedelta(hours=i)
        hour_of_day = future_time.hour
        day_of_week = future_time.weekday()
        
        # Base prediction from historical averages
        base_noise = get_historical_average(historical_data, hour_of_day, day_of_week)
        
        # Weather adjustments
        weather_adjustment = get_weather_adjustment(weather)
        
        # Traffic pattern adjustments
        traffic_adjustment = get_traffic_adjustment(hour_of_day, day_of_week)
        
        # Calculate final prediction
        predicted_noise = base_noise + weather_adjustment + traffic_adjustment
        predicted_noise = max(35, min(100, predicted_noise))  # Clamp to realistic range
        
        # Calculate uncertainty based on historical variance
        uncertainty = calculate_prediction_uncertainty(historical_data, hour_of_day)
        
        prediction = {
            'timestamp': future_time.isoformat(),
            'predicted_db': round(predicted_noise, 1),
            'uncertainty': round(uncertainty, 2),
            'confidence': round((1 - uncertainty/20) * 100, 1),  # Convert to percentage
            'dominant_source': predict_dominant_source(hour_of_day, day_of_week),
            'who_compliance': assess_who_compliance_prediction(predicted_noise)
        }
        
        predictions.append(prediction)
    
    return predictions

def get_historical_average(historical_data, hour, day_of_week):
    """Get historical average for specific hour and day"""
    if not historical_data:
        # Fallback pattern if no historical data
        return get_default_noise_pattern(hour, day_of_week)
    
    # Filter historical data for same hour and day of week
    relevant_data = [
        entry for entry in historical_data 
        if entry['hour'] == hour and entry['day_of_week'] == day_of_week
    ]
    
    if relevant_data:
        return sum(entry['noise_level'] for entry in relevant_data) / len(relevant_data)
    else:
        return get_default_noise_pattern(hour, day_of_week)

def get_default_noise_pattern(hour, day_of_week):
    """Default noise pattern when no historical data available"""
    # Weekend vs weekday
    is_weekend = day_of_week >= 5
    
    if is_weekend:
        if 6 <= hour <= 10:  # Weekend morning
            return 55
        elif 10 <= hour <= 22:  # Weekend day/evening
            return 60
        else:  # Weekend night
            return 45
    else:
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            return 75
        elif 9 <= hour <= 17:  # Business hours
            return 65
        elif 22 <= hour or hour <= 6:  # Night
            return 50
        else:  # Other times
            return 58

def get_weather_adjustment(weather):
    """Adjust prediction based on weather conditions"""
    adjustments = {
        'clear': 0,
        'rain': -5,  # Rain dampens noise
        'heavy_rain': -8,
        'snow': -3,
        'wind': 3,   # Wind can amplify noise
        'fog': -2
    }
    return adjustments.get(weather, 0)

def get_traffic_adjustment(hour, day_of_week):
    """Adjust for traffic patterns"""
    is_weekend = day_of_week >= 5
    
    if is_weekend:
        return -3  # Generally quieter on weekends
    
    # Weekday traffic patterns
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
        return 8
    elif 22 <= hour or hour <= 6:  # Night hours
        return -5
    else:
        return 0

def calculate_prediction_uncertainty(historical_data, hour):
    """Calculate uncertainty based on historical variance"""
    if not historical_data:
        return 5.0  # Default uncertainty
    
    # Get variance for this hour
    hour_data = [entry['noise_level'] for entry in historical_data if entry['hour'] == hour]
    
    if len(hour_data) < 2:
        return 5.0
    
    # Calculate standard deviation as uncertainty measure
    mean = sum(hour_data) / len(hour_data)
    variance = sum((x - mean) ** 2 for x in hour_data) / len(hour_data)
    return min(15.0, variance ** 0.5)  # Cap uncertainty at 15 dB

def predict_dominant_source(hour, day_of_week):
    """Predict dominant noise source based on time patterns"""
    is_weekend = day_of_week >= 5
    
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
        return 'traffic'
    elif 9 <= hour <= 17 and not is_weekend:  # Business hours weekday
        return 'urban_activity'
    elif 22 <= hour or hour <= 6:  # Night
        return 'ambient'
    elif is_weekend and 10 <= hour <= 22:  # Weekend social hours
        return 'human_activity'
    else:
        return 'mixed'

def assess_who_compliance_prediction(predicted_db):
    """Assess WHO compliance for predicted noise level"""
    if predicted_db >= 70:
        return {'status': 'Critical', 'exceeds_limit': True}
    elif predicted_db >= 55:
        return {'status': 'Exceeds Daytime Limit', 'exceeds_limit': True}
    else:
        return {'status': 'Within Safe Limits', 'exceeds_limit': False}

def calculate_confidence_interval(predictions):
    """Calculate overall confidence interval for predictions"""
    if not predictions:
        return {'lower': 0, 'upper': 0, 'average_confidence': 0}
    
    avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
    avg_uncertainty = sum(p['uncertainty'] for p in predictions) / len(predictions)
    
    return {
        'average_confidence': round(avg_confidence, 1),
        'average_uncertainty': round(avg_uncertainty, 2),
        'reliability': 'high' if avg_confidence > 80 else 'medium' if avg_confidence > 60 else 'low'
    }

def analyze_noise_trends(lat, lng, days):
    """Analyze noise trends for a location"""
    # Mock trend analysis - in production, query actual database
    trends = {
        'hourly_averages': generate_hourly_averages(),
        'daily_averages': generate_daily_averages(days),
        'noise_sources': {
            'traffic': 45,
            'construction': 20,
            'human_activity': 25,
            'industrial': 10
        },
        'trend_direction': 'stable',  # increasing, decreasing, stable
        'change_percentage': 2.1
    }
    
    return trends

def generate_hourly_averages():
    """Generate hourly noise averages"""
    return [
        {'hour': h, 'average_db': get_default_noise_pattern(h, 1)} 
        for h in range(24)
    ]

def generate_daily_averages(days):
    """Generate daily averages for trend analysis"""
    import random
    base_level = 62
    
    daily_averages = []
    for i in range(days):
        # Add some realistic variation
        daily_avg = base_level + random.uniform(-5, 5)
        date = (datetime.now() - timedelta(days=days-i)).date().isoformat()
        
        daily_averages.append({
            'date': date,
            'average_db': round(daily_avg, 1)
        })
    
    return daily_averages

def identify_peak_hours(trends):
    """Identify peak noise hours"""
    hourly_data = trends.get('hourly_averages', [])
    
    if not hourly_data:
        return []
    
    # Find hours with noise levels above 70 dB
    peak_hours = [
        {'hour': entry['hour'], 'level': entry['average_db']}
        for entry in hourly_data 
        if entry['average_db'] > 70
    ]
    
    return sorted(peak_hours, key=lambda x: x['level'], reverse=True)

def identify_seasonal_patterns(trends):
    """Identify seasonal noise patterns"""
    # Mock seasonal analysis
    return {
        'current_season': 'autumn',
        'seasonal_adjustment': -2.0,  # dB difference from annual average
        'patterns': {
            'spring': {'avg_adjustment': 1.0, 'peak_months': ['March', 'April']},
            'summer': {'avg_adjustment': 3.0, 'peak_months': ['July', 'August']},
            'autumn': {'avg_adjustment': -2.0, 'peak_months': ['October', 'November']},
            'winter': {'avg_adjustment': -4.0, 'peak_months': ['January', 'February']}
        }
    }

def identify_noise_hotspots(radius_km, threshold_db, time_period):
    """Identify noise pollution hotspots"""
    # Mock hotspot data - in production, query spatial database
    hotspots = [
        {
            'id': 1,
            'location': {'latitude': 40.7589, 'longitude': -73.9851},
            'average_db': 78.5,
            'peak_db': 85.2,
            'dominant_source': 'traffic',
            'severity': 'high',
            'area_description': 'Times Square area',
            'measurement_count': 245
        },
        {
            'id': 2,
            'location': {'latitude': 40.7505, 'longitude': -73.9934},
            'average_db': 82.1,
            'peak_db': 92.3,
            'dominant_source': 'construction',
            'severity': 'critical',
            'area_description': 'Construction zone',
            'measurement_count': 156
        },
        {
            'id': 3,
            'location': {'latitude': 40.7411, 'longitude': -73.9897},
            'average_db': 74.8,
            'peak_db': 81.6,
            'dominant_source': 'traffic',
            'severity': 'high',
            'area_description': 'Major intersection',
            'measurement_count': 189
        }
    ]
    
    # Filter by threshold
    filtered_hotspots = [hs for hs in hotspots if hs['average_db'] >= threshold_db]
    
    return filtered_hotspots

def calculate_severity_distribution(hotspots):
    """Calculate severity distribution of hotspots"""
    if not hotspots:
        return {}
    
    severity_counts = {}
    for hotspot in hotspots:
        severity = hotspot['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    total = len(hotspots)
    return {
        severity: {'count': count, 'percentage': round(count/total*100, 1)}
        for severity, count in severity_counts.items()
    }