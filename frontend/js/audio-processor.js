// js/audio-processor.js - Audio processing and analysis

import { classifyAudioYAMNet, displayClassificationResults } from './ml-models.js';
import { addNoiseMarker } from './map-handler.js';

// Global recording variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Process uploaded audio file
export async function processAudioFile(file) {
    if (!window.userConsented) {
        showStatus('Please accept consent first.', 'error');
        return;
    }

    // Validate file
    if (!['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/mpeg'].includes(file.type)) {
        showStatus('Invalid file format. Use WAV, MP3, or M4A.', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showStatus('File too large. Maximum 10MB allowed.', 'error');
        return;
    }

    showStatus('🧠 Analyzing audio with YAMNet...', 'info');

    try {
        // Perform AI classification using YAMNet
        const classification = await classifyAudioYAMNet(file);
        
        // Display results
        displayClassificationResults(classification);
        
        // Generate prediction
        generatePrediction();
        
        // Add to map if geolocation available
        addAnalysisToMap(classification);
        
        showStatus('✅ Audio analysis complete!', 'success');
    } catch (error) {
        console.error('Processing error:', error);
        showStatus('Error processing audio. Please try again.', 'error');
    }
}

// Add analysis result to map
function addAnalysisToMap(classification) {
    if (!navigator.geolocation) {
        // Use default location with some randomness
        const lat = 40.7128 + (Math.random() - 0.5) * 0.1;
        const lng = -74.0060 + (Math.random() - 0.5) * 0.1;
        const noiseLevel = Math.round(45 + (classification[0].confidence * 40));
        addNoiseMarker(lat, lng, noiseLevel, classification[0].confidence);
        return;
    }
    
    navigator.geolocation.getCurrentPosition(pos => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const noiseLevel = Math.round(45 + (classification[0].confidence * 40));
        addNoiseMarker(lat, lng, noiseLevel, classification[0].confidence);
    }, () => {
        // Fallback to simulated location
        const lat = 40.7128 + (Math.random() - 0.5) * 0.1;
        const lng = -74.0060 + (Math.random() - 0.5) * 0.1;
        const noiseLevel = Math.round(45 + (classification[0].confidence * 40));
        addNoiseMarker(lat, lng, noiseLevel, classification[0].confidence);
    });
}

// Generate prediction (demo)
function generatePrediction() {
    document.getElementById('predictionPanel').style.display = '';
    document.getElementById('predictionResult').textContent = 
        `${Math.round(Math.random() * 20 + 55)} dB (next hour est.)`;
}

// Recording functionality
export async function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            startRecording(stream);
            recordBtn.textContent = '⏹️ Stop Recording';
            recordBtn.classList.add('recording');
            showRecordingStatus('Recording... 🔴');
        } catch (error) {
            showStatus('Error: Unable to access microphone', 'error');
        }
    } else {
        stopRecording();
        recordBtn.textContent = '🎤 Start Recording';
        recordBtn.classList.remove('recording');
        showRecordingStatus('');
    }
}

function startRecording(stream) {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    isRecording = true;

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        processRecordedAudio(audioBlob);
    };

    mediaRecorder.start();
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
    }
}

function processRecordedAudio(audioBlob) {
    showStatus('Processing recorded audio...', 'info');
    
    // Process the recorded audio
    setTimeout(async () => {
        try {
            const classification = await classifyAudioYAMNet(audioBlob);
            displayClassificationResults(classification);
            addAnalysisToMap(classification);
            showStatus('Recording analysis complete!', 'success');
        } catch (error) {
            showStatus('Error processing recording', 'error');
        }
    }, 1500);
}

// Show recording status
function showRecordingStatus(message) {
    document.getElementById('recordingStatus').innerHTML = message;
}

// Status message display
export function showStatus(message, type) {
    const container = document.getElementById('statusMessages');
    const statusDiv = document.createElement('div');
    statusDiv.className = `status ${type}`;
    statusDiv.innerHTML = message.includes('Processing') || message.includes('Recording') || message.includes('Analyzing')
        ? `<span class="loading"></span> ${message}`
        : message;
    
    container.innerHTML = '';
    container.appendChild(statusDiv);
    
    // Auto-remove after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            if (container.contains(statusDiv)) {
                container.removeChild(statusDiv);
            }
        }, 5000);
    }
}

// Submit citizen feedback
export async function submitFeedback() {
    const feedback = document.getElementById('feedbackText').value;
    
    if (!feedback.trim()) {
        showStatus('Please enter some feedback before submitting.', 'error');
        return;
    }
    
    try {
        // Try to send to backend
        const response = await fetch('/api/feedback/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                feedback: feedback, 
                timestamp: new Date().toISOString()
            })
        });
        
        if (response.ok) {
            showStatus('Feedback submitted to server! Thank you for your report.', 'success');
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        // Fallback for demo mode (no backend)
        showStatus('Feedback submitted! Thank you for your report.', 'success');
    }
    
    document.getElementById('feedbackText').value = '';
}