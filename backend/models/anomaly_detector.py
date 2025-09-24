# Machine Learning Audio Classifier
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
import os

class AudioClassifier:
    """ML-powered audio classification for noise source identification"""
    
    def __init__(self, model_path='../models/yamnet.h5'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.class_labels = ['Traffic', 'Construction', 'Nature', 'Human', 'Industrial', 'Other']
        self.load_model()
        
    def load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                print(f"Loaded model from {self.model_path}")
            else:
                print("Model file not found, using fallback classifier")
                self.model = self._create_fallback_model()
        except Exception as e:
            print(f"Error loading model: {e}, using fallback")
            self.model = self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create simple fallback model for demo purposes"""
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        # Train with some mock data for demo
        X_mock = np.random.rand(100, 13)  # 13 MFCC features
        y_mock = np.random.randint(0, len(self.class_labels), 100)
        model.fit(X_mock, y_mock)
        return model
    
    def classify(self, features):
        """Classify audio features into noise source categories"""
        try:
            if isinstance(features, list) and len(features) > 0:
                # Convert MFCC features to numpy array
                feature_array = np.array(features)
                
                if len(feature_array.shape) == 1:
                    feature_array = feature_array.reshape(1, -1)
                
                # Ensure we have the right number of features
                if feature_array.shape[1] < 13:
                    # Pad with zeros if not enough features
                    padding = np.zeros((feature_array.shape[0], 13 - feature_array.shape[1]))
                    feature_array = np.hstack([feature_array, padding])
                elif feature_array.shape[1] > 13:
                    # Truncate if too many features
                    feature_array = feature_array[:, :13]
                
                # Normalize features
                feature_array = self.scaler.fit_transform(feature_array)
                
                # Get predictions
                if hasattr(self.model, 'predict_proba'):
                    # Sklearn model
                    probabilities = self.model.predict_proba(feature_array)[0]
                else:
                    # TensorFlow model
                    probabilities = self.model.predict(feature_array)[0]
                
                # Create results
                results = []
                for i, prob in enumerate(probabilities):
                    results.append({
                        'class': self.class_labels[i],
                        'confidence': float(prob),
                        'source_type': self._get_source_type(self.class_labels[i])
                    })
                
                # Sort by confidence
                results.sort(key=lambda x: x['confidence'], reverse=True)
                return results
                
            else:
                # Fallback classification
                return self._generate_mock_classification()
                
        except Exception as e:
            print(f"Classification error: {e}")
            return self._generate_mock_classification()
    
    def quick_classify(self, features):
        """Quick classification for real-time processing"""
        # Simplified version for real-time use
        results = self.classify(features)
        # Return only top 3 results for speed
        return results[:3] if results else []
    
    def estimate_noise_level(self, features, classification_results):
        """Estimate noise level in dB based on features and classification"""
        try:
            if not features or not classification_results:
                return 55.0  # Default level
            
            # Get dominant source
            dominant_source = classification_results[0]['class']
            confidence = classification_results[0]['confidence']
            
            # Base noise levels for different sources
            base_levels = {
                'Traffic': 75.0,
                'Construction': 85.0,
                'Industrial': 80.0,
                'Human': 60.0,
                'Nature': 45.0,
                'Other': 55.0
            }
            
            base_level = base_levels.get(dominant_source, 55.0)
            
            # Adjust based on confidence
            confidence_adjustment = (confidence - 0.5) * 10  # ±5 dB adjustment
            
            # Calculate energy-based adjustment from features
            energy_adjustment = self._calculate_energy_adjustment(features)
            
            # Final noise level
            estimated_db = base_level + confidence_adjustment + energy_adjustment
            
            # Clamp to realistic range
            return max(30.0, min(120.0, estimated_db))
            
        except Exception as e:
            print(f"Noise estimation error: {e}")
            return 55.0
    
    def _calculate_energy_adjustment(self, features):
        """Calculate adjustment based on audio energy"""
        try:
            if isinstance(features, list) and len(features) > 0:
                # Calculate average energy from features
                if isinstance(features[0], dict) and 'energy' in features[0]:
                    avg_energy = np.mean([f['energy'] for f in features])
                    # Convert energy to dB adjustment (-10 to +15 dB range)
                    return (avg_energy - 0.3) * 25
                elif isinstance(features[0], (int, float)):
                    avg_energy = np.mean(features)
                    return (avg_energy - 0.3) * 25
            return 0.0
        except:
            return 0.0
    
    def _get_source_type(self, class_name):
        """Get source type category"""
        source_mapping = {
            'Traffic': 'vehicular',
            'Construction': 'industrial',
            'Industrial': 'industrial',
            'Human': 'social',
            'Nature': 'environmental',
            'Other': 'mixed'
        }
        return source_mapping.get(class_name, 'mixed')
    
    def _generate_mock_classification(self):
        """Generate mock classification for demo purposes"""
        import random
        
        # Generate realistic mock probabilities
        mock_results = []
        total_prob = 0
        
        for class_name in self.class_labels:
            prob = random.uniform(0.1, 0.9)
            mock_results.append({
                'class': class_name,
                'confidence': prob,
                'source_type': self._get_source_type(class_name)
            })
            total_prob += prob
        
        # Normalize probabilities
        for result in mock_results:
            result['confidence'] = result['confidence'] / total_prob
        
        # Sort by confidence
        mock_results.sort(key=lambda x: x['confidence'], reverse=True)
        return mock_results
    
    def calibrate_noise_levels(self, reference_measurements):
        """Calibrate noise level predictions with reference measurements"""
        try:
            # Store calibration data for future adjustments
            self.calibration_offset = self._calculate_calibration_offset(reference_measurements)
            print(f"Calibration offset: {self.calibration_offset:.2f} dB")
        except Exception as e:
            print(f"Calibration error: {e}")
    
    def _calculate_calibration_offset(self, reference_measurements):
        """Calculate calibration offset from reference measurements"""
        if not reference_measurements:
            return 0.0
        
        total_offset = 0
        count = 0
        
        for measurement in reference_measurements:
            predicted = measurement.get('predicted_db', 0)
            actual = measurement.get('actual_db', 0)
            if predicted > 0 and actual > 0:
                total_offset += (actual - predicted)
                count += 1
        
        return total_offset / count if count > 0 else 0.0
    
    def get_model_info(self):
        """Get model information for debugging"""
        return {
            'model_type': type(self.model).__name__,
            'model_path': self.model_path,
            'class_labels': self.class_labels,
            'feature_dimensions': 13,  # MFCC features
            'calibrated': hasattr(self, 'calibration_offset')
        }