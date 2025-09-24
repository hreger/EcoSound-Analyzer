# Audio processing routes
from flask import Blueprint, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from models.classifier import AudioClassifier
from models.anomaly_detector import AnomalyDetector
from utils.audio_features import extract_mfcc_features
from utils.db_handler import save_audio_metadata

audio_bp = Blueprint('audio', __name__)

# Initialize ML models
classifier = AudioClassifier()
anomaly_detector = AnomalyDetector()

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@audio_bp.route('/classify', methods=['POST'])
def classify_audio():
    """Classify uploaded audio file"""
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Get optional metadata
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        timestamp = request.form.get('timestamp')
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)
        
        try:
            # Extract MFCC features
            features = extract_mfcc_features(temp_path)
            
            # Classify audio
            classification_results = classifier.classify(features)
            
            # Detect anomalies
            anomaly_result = anomaly_detector.detect(features)
            
            # Estimate noise level
            noise_level = classifier.estimate_noise_level(features, classification_results)
            
            # Save metadata to database
            metadata = {
                'filename': filename,
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp,
                'noise_level': noise_level,
                'classification': classification_results,
                'anomaly': anomaly_result
            }
            save_audio_metadata(metadata)
            
            # Prepare response
            response = {
                'success': True,
                'classification': classification_results,
                'noise_level': noise_level,
                'anomaly': anomaly_result,
                'who_compliance': assess_who_compliance(noise_level),
                'confidence_score': max([result['confidence'] for result in classification_results])
            }
            
            return jsonify(response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@audio_bp.route('/real-time', methods=['POST'])
def real_time_analysis():
    """Process real-time audio stream"""
    try:
        # Get audio data from request
        audio_data = request.get_json()
        
        if not audio_data or 'features' not in audio_data:
            return jsonify({'error': 'No audio features provided'}), 400
        
        features = audio_data['features']
        
        # Quick classification for real-time
        classification = classifier.quick_classify(features)
        noise_level = classifier.estimate_noise_level(features, classification)
        
        response = {
            'noise_level': noise_level,
            'dominant_source': classification[0]['class'] if classification else 'unknown',
            'confidence': classification[0]['confidence'] if classification else 0,
            'who_status': assess_who_compliance(noise_level)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Real-time analysis failed: {str(e)}'}), 500

@audio_bp.route('/calibrate', methods=['POST'])
def calibrate_system():
    """Calibrate noise level measurements"""
    try:
        calibration_data = request.get_json()
        
        if not calibration_data or 'reference_level' not in calibration_data:
            return jsonify({'error': 'Reference level required for calibration'}), 400
        
        reference_level = calibration_data['reference_level']
        measured_level = calibration_data.get('measured_level', 0)
        
        # Calculate calibration offset
        calibration_offset = reference_level - measured_level
        
        # Store calibration in session or database
        # In production, save to user profile or device settings
        
        response = {
            'success': True,
            'calibration_offset': calibration_offset,
            'message': 'System calibrated successfully'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Calibration failed: {str(e)}'}), 500

def assess_who_compliance(noise_level):
    """Assess WHO noise compliance"""
    if noise_level >= 70:
        return {
            'status': 'Critical - Health Risk',
            'color': '#e74c3c',
            'exceeds_limit': True,
            'limit_type': 'Critical Threshold'
        }
    elif noise_level >= 55:
        return {
            'status': 'Exceeds WHO Daytime Limit',
            'color': '#f39c12',
            'exceeds_limit': True,
            'limit_type': 'Daytime Limit'
        }
    else:
        return {
            'status': 'Within Safe Limits',
            'color': '#27ae60',
            'exceeds_limit': False,
            'limit_type': 'Safe'
        }