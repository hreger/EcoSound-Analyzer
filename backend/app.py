# Flask backend - Main application
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# Import route modules
from routes.audio import audio_bp
from routes.feedback import feedback_bp
from routes.prediction import prediction_bp
from routes.urban_planning import urban_planning_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Register blueprints
app.register_blueprint(audio_bp, url_prefix='/api/audio')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(prediction_bp, url_prefix='/api/prediction')
app.register_blueprint(urban_planning_bp, url_prefix='/api/urban-planning')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'message': 'EcoSound Analyzer API is running',
        'endpoints': {
            'audio_classification': '/api/audio/classify',
            'feedback_submission': '/api/feedback/submit',
            'noise_prediction': '/api/prediction/forecast'
        }
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)