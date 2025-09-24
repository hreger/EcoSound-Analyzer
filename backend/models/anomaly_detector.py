# Anomaly Detection for Audio Noise Analysis
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import joblib
import os

class AnomalyDetector:
    """Detect unusual noise patterns and acoustic anomalies"""
    
    def __init__(self, model_path='../models/anomaly_detector.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.threshold = 0.1  # Anomaly threshold
        self.feature_history = []
        self.max_history = 1000  # Maximum stored feature vectors
        self.load_model()
    
    def load_model(self):
        """Load pre-trained anomaly detection model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"Loaded anomaly detector from {self.model_path}")
            else:
                print("Anomaly model not found, creating new model")
                self.model = self._create_anomaly_model()
        except Exception as e:
            print(f"Error loading anomaly model: {e}, creating new model")
            self.model = self._create_anomaly_model()
    
    def _create_anomaly_model(self):
        """Create new isolation forest model for anomaly detection"""
        return IsolationForest(
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42,
            n_estimators=100
        )
    
    def detect(self, features):
        """Detect anomalies in audio features"""
        try:
            if not features:
                return self._no_anomaly_result()
            
            # Convert features to numpy array
            feature_array = self._prepare_features(features)
            
            if feature_array is None:
                return self._no_anomaly_result()
            
            # Update feature history for model training
            self._update_feature_history(feature_array)
            
            # Retrain model if we have enough data
            if len(self.feature_history) >= 50:
                self._retrain_model()
            
            # Detect anomalies
            anomaly_score = self._calculate_anomaly_score(feature_array)
            
            # Classify anomaly type if detected
            if anomaly_score > self.threshold:
                anomaly_type = self._classify_anomaly_type(feature_array)
                return {
                    'detected': True,
                    'type': anomaly_type,
                    'severity': self._get_anomaly_severity(anomaly_score),
                    'confidence': min(1.0, anomaly_score * 2),
                    'score': float(anomaly_score),
                    'timestamp': datetime.now().isoformat(),
                    'description': self._get_anomaly_description(anomaly_type)
                }
            else:
                return self._no_anomaly_result()
                
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return self._no_anomaly_result()
    
    def _prepare_features(self, features):
        """Prepare features for anomaly detection"""
        try:
            if isinstance(features, list) and len(features) > 0:
                if isinstance(features[0], dict):
                    # Extract numeric features from dictionaries
                    feature_vector = []
                    for feature in features:
                        if isinstance(feature, dict):
                            # Extract energy, zcr, and other numeric features
                            feature_vector.extend([
                                feature.get('energy', 0),
                                feature.get('zcr', 0),
                                feature.get('spectral_centroid', 0),
                                feature.get('spectral_rolloff', 0),
                                feature.get('mfcc_0', 0),
                                feature.get('mfcc_1', 0),
                                feature.get('mfcc_2', 0)
                            ])
                    
                    if feature_vector:
                        return np.array(feature_vector).reshape(1, -1)
                
                elif isinstance(features[0], (int, float)):
                    # Direct numeric features
                    return np.array(features).reshape(1, -1)
            
            return None
            
        except Exception as e:
            print(f"Feature preparation error: {e}")
            return None
    
    def _update_feature_history(self, feature_array):
        """Update feature history for model training"""
        if feature_array is not None:
            self.feature_history.append(feature_array.flatten())
            
            # Maintain maximum history size
            if len(self.feature_history) > self.max_history:
                self.feature_history.pop(0)
    
    def _retrain_model(self):
        """Retrain anomaly detection model with accumulated data"""
        try:
            if len(self.feature_history) >= 50:
                X = np.array(self.feature_history)
                
                # Ensure consistent feature dimensions
                min_features = min(len(x) for x in self.feature_history)
                X = np.array([x[:min_features] for x in self.feature_history])
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Retrain model
                self.model.fit(X_scaled)
                print(f"Retrained anomaly model with {len(X)} samples")
                
        except Exception as e:
            print(f"Model retraining error: {e}")
    
    def _calculate_anomaly_score(self, feature_array):
        """Calculate anomaly score for features"""
        try:
            if self.model is None or feature_array is None:
                return 0.0
            
            # Ensure feature array has correct dimensions
            if len(self.feature_history) > 0:
                expected_features = len(self.feature_history[0])
                if feature_array.shape[1] != expected_features:
                    # Pad or truncate to match expected dimensions
                    if feature_array.shape[1] < expected_features:
                        padding = np.zeros((1, expected_features - feature_array.shape[1]))
                        feature_array = np.hstack([feature_array, padding])
                    else:
                        feature_array = feature_array[:, :expected_features]
            
            # Scale features if scaler is fitted
            if hasattr(self.scaler, 'mean_'):
                try:
                    feature_array = self.scaler.transform(feature_array)
                except:
                    pass  # Skip scaling if it fails
            
            # Get anomaly score
            if hasattr(self.model, 'decision_function'):
                score = self.model.decision_function(feature_array)[0]
                # Convert to 0-1 range where higher is more anomalous
                return max(0, -score / 2)
            elif hasattr(self.model, 'score_samples'):
                score = self.model.score_samples(feature_array)[0]
                return max(0, -score)
            else:
                # Fallback: use simple energy-based detection
                return self._energy_based_anomaly_score(feature_array)
                
        except Exception as e:
            print(f"Anomaly scoring error: {e}")
            return 0.0
    
    def _energy_based_anomaly_score(self, feature_array):
        """Fallback energy-based anomaly detection"""
        try:
            # Simple threshold-based detection on first feature (assumed to be energy)
            if feature_array.shape[1] > 0:
                energy = abs(feature_array[0, 0])
                
                # High energy anomaly
                if energy > 0.8:
                    return min(1.0, energy)
                
                # Very low energy anomaly
                if energy < 0.05:
                    return 0.3
            
            return 0.0
            
        except:
            return 0.0
    
    def _classify_anomaly_type(self, feature_array):
        """Classify the type of anomaly detected"""
        try:
            if feature_array is None or feature_array.shape[1] == 0:
                return 'unknown'
            
            # Simple rule-based classification
            energy = abs(feature_array[0, 0]) if feature_array.shape[1] > 0 else 0
            
            if energy > 0.9:
                return 'high_energy_event'  # Sirens, alarms, explosions
            elif energy > 0.7:
                return 'loud_machinery'     # Construction, industrial
            elif energy < 0.1:
                return 'unusual_quiet'      # Abnormally quiet period
            elif feature_array.shape[1] > 1:
                # Check spectral characteristics if available
                spectral_feature = abs(feature_array[0, 1])
                if spectral_feature > 0.8:
                    return 'unusual_frequency'  # Unusual spectral content
            
            return 'acoustic_anomaly'
            
        except Exception as e:
            print(f"Anomaly classification error: {e}")
            return 'unknown'
    
    def _get_anomaly_severity(self, score):
        """Determine anomaly severity based on score"""
        if score > 0.7:
            return 'critical'
        elif score > 0.4:
            return 'high'
        elif score > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _get_anomaly_description(self, anomaly_type):
        """Get human-readable description of anomaly"""
        descriptions = {
            'high_energy_event': 'Extremely loud sound detected (possible emergency vehicle, alarm, or explosion)',
            'loud_machinery': 'Unusually loud mechanical noise (construction equipment, industrial machinery)',
            'unusual_quiet': 'Abnormally quiet period detected (possible sensor malfunction or unusual conditions)',
            'unusual_frequency': 'Unusual frequency content detected (possible interference or unique sound source)',
            'acoustic_anomaly': 'Unusual acoustic pattern detected',
            'unknown': 'Anomaly detected but type could not be determined'
        }
        return descriptions.get(anomaly_type, 'Unusual noise pattern detected')
    
    def _no_anomaly_result(self):
        """Return result indicating no anomaly detected"""
        return {
            'detected': False,
            'type': None,
            'severity': 'none',
            'confidence': 0.0,
            'score': 0.0,
            'timestamp': datetime.now().isoformat(),
            'description': 'No anomaly detected'
        }
    
    def get_anomaly_stats(self):
        """Get statistics about detected anomalies"""
        return {
            'model_type': type(self.model).__name__,
            'feature_history_size': len(self.feature_history),
            'threshold': self.threshold,
            'model_trained': hasattr(self.scaler, 'mean_'),
            'detection_ready': self.model is not None
        }
    
    def update_threshold(self, new_threshold):
        """Update anomaly detection threshold"""
        if 0.0 <= new_threshold <= 1.0:
            self.threshold = new_threshold
            print(f"Updated anomaly threshold to {new_threshold}")
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def save_model(self, path=None):
        """Save the trained anomaly detection model"""
        try:
            save_path = path or self.model_path
            if self.model is not None:
                joblib.dump(self.model, save_path)
                print(f"Saved anomaly model to {save_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def reset_model(self):
        """Reset the anomaly detection model"""
        self.model = self._create_anomaly_model()
        self.scaler = StandardScaler()
        self.feature_history = []
        print("Anomaly detection model reset")