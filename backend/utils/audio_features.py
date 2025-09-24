# Audio Feature Extraction Utilities
import librosa
import numpy as np
import scipy.signal
from scipy.io import wavfile
import tempfile
import os

def extract_mfcc_features(audio_path, n_mfcc=13, n_fft=2048, hop_length=512):
    """
    Extract MFCC features from audio file for privacy-preserving analysis
    
    Args:
        audio_path: Path to audio file
        n_mfcc: Number of MFCC coefficients to extract
        n_fft: FFT window size
        hop_length: Hop length for STFT
    
    Returns:
        Dictionary containing MFCC features and metadata
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(
            y=y, 
            sr=sr, 
            n_mfcc=n_mfcc,
            n_fft=n_fft,
            hop_length=hop_length
        )
        
        # Calculate statistical features from MFCCs
        mfcc_stats = {
            'mfcc_mean': np.mean(mfccs, axis=1).tolist(),
            'mfcc_std': np.std(mfccs, axis=1).tolist(),
            'mfcc_delta': np.mean(librosa.feature.delta(mfccs), axis=1).tolist()
        }
        
        # Extract additional spectral features
        spectral_features = extract_spectral_features(y, sr)
        
        # Extract temporal features
        temporal_features = extract_temporal_features(y, sr)
        
        # Combine all features
        features = {
            'mfcc': mfcc_stats,
            'spectral': spectral_features,
            'temporal': temporal_features,
            'metadata': {
                'sample_rate': sr,
                'duration': len(y) / sr,
                'n_samples': len(y)
            }
        }
        
        return features
        
    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None

def extract_spectral_features(y, sr):
    """Extract spectral features from audio signal"""
    try:
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        return {
            'spectral_centroid_mean': float(np.mean(spectral_centroids)),
            'spectral_centroid_std': float(np.std(spectral_centroids)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'spectral_rolloff_std': float(np.std(spectral_rolloff)),
            'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'spectral_bandwidth_std': float(np.std(spectral_bandwidth)),
            'zcr_mean': float(np.mean(zcr)),
            'zcr_std': float(np.std(zcr)),
            'chroma_mean': np.mean(chroma, axis=1).tolist(),
            'chroma_std': np.std(chroma, axis=1).tolist()
        }
        
    except Exception as e:
        print(f"Spectral feature extraction error: {e}")
        return {}

def extract_temporal_features(y, sr):
    """Extract temporal features from audio signal"""
    try:
        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        
        # Tempo estimation
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        return {
            'rms_mean': float(np.mean(rms)),
            'rms_std': float(np.std(rms)),
            'tempo': float(tempo) if tempo else 0.0,
            'onset_rate': len(onset_times) / (len(y) / sr),  # onsets per second
            'energy_entropy': calculate_energy_entropy(y),
            'silence_ratio': calculate_silence_ratio(y)
        }
        
    except Exception as e:
        print(f"Temporal feature extraction error: {e}")
        return {}

def calculate_energy_entropy(signal, frame_length=2048):
    """Calculate energy entropy of audio signal"""
    try:
        # Frame the signal
        frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=frame_length//2)
        
        # Calculate energy for each frame
        energies = np.sum(frames**2, axis=0)
        energies = energies / np.sum(energies)  # Normalize
        
        # Calculate entropy
        energies = energies[energies > 0]  # Remove zeros
        entropy = -np.sum(energies * np.log2(energies))
        
        return float(entropy)
        
    except:
        return 0.0

def calculate_silence_ratio(signal, threshold=0.01):
    """Calculate ratio of silent frames in audio signal"""
    try:
        frame_length = 2048
        frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=frame_length//2)
        
        # Calculate RMS for each frame
        frame_rms = np.sqrt(np.mean(frames**2, axis=0))
        
        # Count silent frames
        silent_frames = np.sum(frame_rms < threshold)
        total_frames = len(frame_rms)
        
        return silent_frames / total_frames if total_frames > 0 else 0.0
        
    except:
        return 0.0

def extract_noise_level_features(audio_path):
    """Extract features specifically for noise level estimation"""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        
        # A-weighting filter for perceptual noise measurement
        y_weighted = apply_a_weighting(y, sr)
        
        # Calculate equivalent sound level (Leq)
        leq = calculate_leq(y_weighted)
        
        # Statistical measures
        rms = np.sqrt(np.mean(y**2))
        peak = np.max(np.abs(y))
        
        # Frequency analysis
        f, psd = scipy.signal.welch(y, sr, nperseg=2048)
        
        # Dominant frequency
        dominant_freq = f[np.argmax(psd)]
        
        return {
            'leq_db': leq,
            'rms': float(rms),
            'peak': float(peak),
            'dominant_frequency': float(dominant_freq),
            'frequency_spread': float(np.std(f[psd > np.max(psd) * 0.1])),
            'low_freq_energy': float(np.sum(psd[f < 500])),
            'mid_freq_energy': float(np.sum(psd[(f >= 500) & (f < 2000)])),
            'high_freq_energy': float(np.sum(psd[f >= 2000]))
        }
        
    except Exception as e:
        print(f"Noise level feature extraction error: {e}")
        return {}

def apply_a_weighting(signal, sr):
    """Apply A-weighting filter to audio signal for perceptual noise measurement"""
    try:
        # A-weighting filter coefficients (simplified)
        # In production, use proper A-weighting filter implementation
        nyquist = sr / 2
        
        # High-pass filter to approximate A-weighting
        from scipy.signal import butter, filtfilt
        b, a = butter(2, 500 / nyquist, btype='high')
        weighted_signal = filtfilt(b, a, signal)
        
        return weighted_signal
        
    except:
        return signal  # Return original if filtering fails

def calculate_leq(signal, reference_pressure=20e-6):
    """Calculate equivalent sound level (Leq) in dB"""
    try:
        # RMS calculation
        rms = np.sqrt(np.mean(signal**2))
        
        # Convert to dB SPL (approximate)
        if rms > 0:
            leq_db = 20 * np.log10(rms / reference_pressure)
            # Calibration offset (would need proper calibration in production)
            leq_db += 94  # Approximate calibration for digital audio
            return float(max(0, min(140, leq_db)))  # Clamp to realistic range
        else:
            return 0.0
            
    except:
        return 0.0

def extract_features_from_blob(audio_blob):
    """Extract features from audio blob (for real-time processing)"""
    try:
        # Save blob to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_blob)
            temp_path = temp_file.name
        
        try:
            # Extract features
            features = extract_mfcc_features(temp_path)
            return features
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"Blob feature extraction error: {e}")
        return None

def normalize_features(features):
    """Normalize feature values for ML model input"""
    try:
        if not features:
            return features
        
        normalized = {}
        
        # Normalize MFCC features
        if 'mfcc' in features:
            mfcc_data = features['mfcc']
            if 'mfcc_mean' in mfcc_data:
                # Z-score normalization
                mean_vals = np.array(mfcc_data['mfcc_mean'])
                std_vals = np.array(mfcc_data['mfcc_std'])
                normalized_mfcc = (mean_vals - np.mean(mean_vals)) / (np.std(mean_vals) + 1e-8)
                normalized['mfcc_normalized'] = normalized_mfcc.tolist()
        
        # Normalize spectral features
        if 'spectral' in features:
            spectral_data = features['spectral']
            normalized['spectral_normalized'] = {}
            for key, value in spectral_data.items():
                if isinstance(value, (int, float)):
                    # Min-max normalization for spectral features
                    normalized['spectral_normalized'][key] = max(0, min(1, value))
        
        return {**features, **normalized}
        
    except Exception as e:
        print(f"Feature normalization error: {e}")
        return features

def validate_audio_file(file_path):
    """Validate audio file format and quality"""
    try:
        # Check file exists
        if not os.path.exists(file_path):
            return False, "File not found"
        
        # Try to load with librosa
        y, sr = librosa.load(file_path, sr=None, duration=1.0)  # Load first second
        
        # Check basic properties
        if len(y) == 0:
            return False, "Empty audio file"
        
        if sr < 8000:
            return False, "Sample rate too low (minimum 8kHz)"
        
        if sr > 192000:
            return False, "Sample rate too high (maximum 192kHz)"
        
        # Check for silence
        if np.max(np.abs(y)) < 1e-6:
            return False, "Audio appears to be silent"
        
        return True, "Valid audio file"
        
    except Exception as e:
        return False, f"Audio validation error: {str(e)}"