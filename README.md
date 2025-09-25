# EcoSound Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow.js](https://img.shields.io/badge/TensorFlow.js-v4.10.0-green.svg)](https://www.tensorflow.org/js)
[![Leaflet](https://img.shields.io/badge/Leaflet-v1.9.4-red.svg)](https://leafletjs.com/)

## Introduction

**EcoSound Analyzer** is an innovative, AI-driven web application designed for real-time urban noise pollution monitoring, classification, and geospatial mapping. Leveraging advanced machine learning models and interactive visualization, it empowers researchers, urban planners, and citizens to identify, analyze, and mitigate noise pollution in urban environments.

### Key Capabilities
- **Real-Time Audio Analysis**: Upload or record audio files for instant classification using Google's YAMNet model via TensorFlow.js.
- **AI-Powered Classification**: Identifies noise sources such as traffic, construction, human activity, nature sounds, and industrial noise with confidence scores.
- **Anomaly Detection**: Detects unusual acoustic patterns using Isolation Forest algorithms for early identification of environmental anomalies.
- **Noise Level Prediction**: Forecasts future noise levels based on historical patterns, time-of-day, weather, and traffic data.
- **Interactive Mapping**: Visualizes noise pollution hotspots on an interactive Leaflet map with heat layers for different sound sources and uncertainty visualization.
- **WHO Compliance Assessment**: Evaluates noise levels against World Health Organization (WHO) standards for daytime (55 dB), nighttime (40 dB), and critical thresholds (70 dB).
- **Citizen Feedback Integration**: Allows users to submit reports on noise issues, contributing to community-driven urban noise monitoring.
- **Privacy-Focused Design**: Processes only anonymized audio features (e.g., MFCC coefficients) without storing raw audio, ensuring user privacy.
- **Hybrid Architecture**: Supports standalone frontend demo (browser-based) and full backend integration with Flask API for scalable deployment.

This project addresses critical urban health challenges, as chronic noise pollution affects millions globally, contributing to stress, sleep disturbances, and cardiovascular issues. By providing actionable insights, EcoSound Analyzer supports evidence-based urban planning and environmental policy-making.

## Features

### Core Functionalities
- **Audio Input Methods**: Supports file uploads (WAV, MP3, M4A) and live microphone recording for flexible user interaction.
- **Sound Classification**: Categorizes audio into 6 main classes (Traffic, Construction, Nature, Human, Industrial, Other) with weighted confidence scores.
- **Noise Level Estimation**: Computes estimated decibel (dB) levels based on spectral features and source classification, with calibration support.
- **Anomaly Detection**: Identifies outliers like high-energy events (sirens), unusual quiet periods, or spectral anomalies using machine learning.
- **Forecasting & Trends**: Predicts noise levels for the next hour/day with uncertainty intervals; analyzes historical trends and peak hours.
- **Geospatial Visualization**: 
  - Interactive map centered on user location (with fallback to sample areas like Bangalore/VIT Vellore).
  - Toggleable heat layers for traffic, construction, and nature sounds.
  - Noise hotspots identification and severity distribution.
  - Uncertainty visualization for prediction reliability.
- **Regulatory Compliance**: Real-time WHO assessment with color-coded status (Green: Safe, Yellow: Moderate, Orange: Exceeds Limit, Red: Critical).
- **Citizen Engagement**: Text-based feedback submission with sentiment analysis, noise source extraction, and urgency detection; aggregates stats for community insights.
- **Demo Mode**: Fully functional frontend without backend; mock data for testing.

### Technical Highlights
- **Frontend**: Modern ES6 modules, responsive design with CSS Grid/Flexbox.
- **Machine Learning**: TensorFlow.js for browser-based inference; Scikit-learn for backend anomaly detection; YAMNet pre-trained model for audio classification.
- **Backend**: RESTful Flask API with CORS support; SQLite database for metadata storage; secure file handling.
- **Privacy & Ethics**: No raw audio storage; geolocation approximated for anonymity; consent popup for data processing.

## Architecture

### High-Level Overview
```
EcoSound Analyzer Architecture
├── Frontend (Browser)
│   ├── UI: HTML/CSS/JS (index.html, styles.css, main.js)
│   ├── Audio Processing: Web Audio API + Meyda.js (audio-processor.js)
│   ├── ML Inference: TensorFlow.js + YAMNet (ml-models.js)
│   ├── Mapping: Leaflet.js + Heatmaps (map-handler.js)
|   └── Urban Planning: Zone Overlays + Tools (urban-planning-map.js)
│
├── Backend (Flask API)
│   ├── Server: app.py (CORS, Error Handling)
│   ├── Routes: /api/audio (classification), /api/feedback (reports), /api/prediction (forecasts), /api/urban_planning (planning)
│   ├── Models: classifier.py (YAMNet/Sklearn), anomaly_detector.py (Isolation Forest)
│   └── Utils: audio_features.py (MFCC extraction), db_handler.py (SQLite ops), infrastructure_planner.py, zoning_analysis.py
│
├── Data Flow
│   ├── Audio Input → Feature Extraction (MFCC) → ML Classification → Map Visualization
│   ├── Feedback → Analysis (NLP-like) → DB Storage → Stats Aggregation
│   └── Historical Data → Prediction Models → Uncertainty Calculation
│
└── External Dependencies
    ├── ML: TensorFlow.js, Scikit-learn, Keras
    ├── Mapping: Leaflet, Leaflet.Heat
    ├── Audio: Meyda.js
    └── DB: SQLite (ecosound.db)
```

### Component Breakdown
- **Frontend**: Handles user interactions, real-time processing, and visualization. Runs entirely in the browser for demo purposes.
- **Backend**: Provides scalable API for production; handles file uploads, database persistence, and advanced ML (e.g., model training/calibration).
- **Models Directory**: Stores pre-trained models like `yamnet.h5` for audio classification.
- **Data**: Sample JSON for historical noise data; uploads folder for temporary audio files.

## Installation & Setup

### Prerequisites
- Node.js (optional, for dev tools)
- Python 3.8+
- Web browser (Chrome/Firefox recommended for Web Audio API)

### Frontend-Only Demo (No Backend Required)
1. Clone or download the repository.
2. Open `frontend/index.html` in a modern web browser.
3. Grant microphone permissions when prompted.
4. Upload/record audio to see classification and mapping in action.

### Full Setup (Frontend + Backend)
1. **Backend Setup**:
   ```
   cd backend
   python -m venv venv  # Create virtual environment
   venv\Scripts\activate  # Windows: activate venv
   # Or on macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
   - The server runs on `http://localhost:5000`.
   - Database (`ecosound.db`) auto-creates in `backend/`.

2. **Frontend Setup**:
   - Serve the `frontend/` directory via a local server (e.g., Python: `python -m http.server 8000` from project root).
   - Access at `http://localhost:8000` (ensure CORS allows backend at port 5000).

3. **Model Download**:
   - YAMNet model loads automatically via CDN.
   - Place custom models in `models/` if extending.

### Development
- Install VS Code extensions: Python, Live Server.
- Run backend in debug mode: `python app.py` (debug=True).
- Test API: Use Postman or curl for endpoints.

## Usage

### Quick Start
1. **Launch Demo**: Open `frontend/index.html`.
2. **Record/Upload Audio**: Click "Start Recording" or upload a file.
3. **View Analysis**: See classification results, noise level, WHO status, and anomaly alerts.
4. **Interact with Map**: Toggle layers (Traffic, Construction, Nature); add markers from analysis.
5. **Submit Feedback**: Describe issues in the textarea and submit.
6. **Get Predictions**: Analysis triggers a sample forecast for the next hour.

### Example Workflow
- Record urban traffic noise → Classified as "Traffic (85% confidence)" → 72 dB (Exceeds WHO Limit) → Marker added to map → Forecast: 68 dB next hour.
- Submit feedback: "Loud construction at night" → Analyzed as high urgency, stored for trends.

### API Usage (Backend)
See API Documentation below for integration.

## API Documentation

The Flask backend exposes RESTful endpoints under `/api/`. All responses are JSON.

### Audio Processing (`/api/audio`)
- **POST /classify**: Upload audio for classification.
  - Body: Multipart form with `audio` file, optional `latitude`, `longitude`, `timestamp`.
  - Response: `{ classification: [...], noise_level: 72, anomaly: {...}, who_compliance: {...} }`
- **POST /real-time**: Stream features for live analysis.
  - Body: `{ features: [...] }`
  - Response: `{ noise_level: 65, dominant_source: "traffic", confidence: 0.85 }`
- **POST /calibrate**: Adjust noise measurements.
  - Body: `{ reference_level: 70, measured_level: 68 }`

### Feedback (`/api/feedback`)
- **POST /submit**: Submit citizen report.
  - Body: `{ feedback: "Loud traffic...", latitude: 12.97, longitude: 77.59, noise_level: 75 }`
  - Response: `{ success: true, feedback_id: 123, analysis: { noise_sources: ["traffic"], urgency: "high" } }`
- **GET /stats**: Aggregate feedback stats.
  - Response: `{ total_reports: 150, urgent_reports: 20, top_sources: ["traffic", "construction"] }`
- **GET /recent?limit=10**: Recent anonymized reports.

### Prediction (`/api/prediction`)
- **POST /forecast**: Noise level forecast.
  - Body: `{ latitude: 12.97, longitude: 77.59, time_horizon: 1, weather: "clear" }`
  - Response: `{ predictions: [...], confidence_interval: { average_confidence: 85 } }`
- **GET /trends?latitude=12.97&longitude=77.59&days=7**: Historical trends.
  - Response: `{ trends: {...}, peak_hours: [...] }`
- **GET /hotspots?radius=5&threshold=70&period=day**: Identify hotspots.
  - Response: `{ hotspots: [...], severity_distribution: {...} }`

### Health & Status
- **GET /**: Serves frontend `index.html`.
- **GET /health**: `{ status: "healthy", timestamp: "..." }`
- **GET /api/status**: API endpoint overview.

Error Handling: Standard HTTP codes (400, 404, 500) with JSON error messages.

## Research & Environmental Impact

### Scientific Contributions
- **AI for Acoustics**: Integrates YAMNet for edge-computing audio analysis, reducing latency for real-time urban monitoring.
- **Anomaly Detection**: Novel use of Isolation Forest on MFCC features to flag environmental events (e.g., emergency sirens).
- **Predictive Modeling**: Time-series forecasting incorporating weather/traffic, aiding proactive noise mitigation.
- **Privacy-Preserving ML**: Demonstrates federated learning potential by processing features client-side.

### Broader Impacts
- **Public Health**: Noise pollution causes 1.6 million healthy life years lost annually in Europe (WHO). EcoSound enables targeted interventions.
- **Urban Planning**: Hotspot mapping supports zoning laws, green space allocation, and infrastructure improvements.
- **Citizen Science**: Empowers communities to contribute data, fostering environmental awareness and participatory governance.
- **Sustainability**: Aligns with UN SDG 11 (Sustainable Cities) by promoting quieter, healthier urban spaces.
- **Scalability**: Deployable on low-cost devices; potential for city-wide sensor networks.

### Limitations & Future Work
- Current predictions use mock/historical data; integrate real IoT sensors.
- Expand ML models for more languages/cultures.
- Add mobile app support.

## Screenshots

### Home Page
![Home Page](home_page.png)

### Recording & Analysis
![Recording Details](recording_details.png)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

### Guidelines
- Use Python type hints and JS ESLint.
- Add tests for new features.
- Update documentation.
- Prefix branches: `feature/`, `bugfix/`, `docs/`.

For major changes, open an issue first.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google for YAMNet model.
- Leaflet team for mapping library.
- WHO for noise guidelines.
- OpenStreetMap for base tiles.

---

*Built with ❤️ for a quieter world. Questions? Open an issue!*
