// js/ml-models.js - Machine Learning model integration and sound classification

// Sound class configuration with WHO compliance data
const SOUND_CLASSES = {
    'Traffic': { weight: 0.8, color: '#e74c3c', baseline_db: 75 },
    'Construction': { weight: 0.9, color: '#f39c12', baseline_db: 85 },
    'Nature': { weight: 0.2, color: '#27ae60', baseline_db: 45 },
    'Human': { weight: 0.4, color: '#3498db', baseline_db: 60 },
    'Industrial': { weight: 0.85, color: '#8e44ad', baseline_db: 80 },
    'Other': { weight: 0.5, color: '#95a5a6', baseline_db: 55 }
};

// WHO Noise Standards
const WHO_STANDARDS = {
    DAY_LIMIT: 55,
    NIGHT_LIMIT: 40,
    CRITICAL_LIMIT: 70
};

// YAMNet audio classification
export async function classifyAudioYAMNet(audioBlob) {
    try {
        // Load YAMNet model if not already loaded
        if (!window.yamnetModel) {
            console.log('Loading YAMNet model...');
            window.yamnetModel = await yamnet.load();
            console.log('YAMNet model loaded successfully');
        }

        // Convert audio blob to audio buffer
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const buffer = await audioBlob.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(buffer);
        const waveform = audioBuffer.getChannelData(0);

        // Classify audio using YAMNet
        const scores = await window.yamnetModel.classify(waveform);
        
        // Map YAMNet classes to our sound classes and return top 5
        return mapYAMNetToSoundClasses(scores.slice(0, 10));
        
    } catch (error) {
        console.error('YAMNet classification error:', error);
        // Fallback to mock classification for demo
        return generateMockClassification();
    }
}

// Map YAMNet classes to our simplified sound categories
function mapYAMNetToSoundClasses(yamnetResults) {
    const mappedResults = {};
    
    // Initialize all our categories
    Object.keys(SOUND_CLASSES).forEach(cls => {
        mappedResults[cls] = 0;
    });
    
    // Map YAMNet results to our categories
    yamnetResults.forEach(result => {
        const className = result.className.toLowerCase();
        
        if (className.includes('vehicle') || className.includes('car') || className.includes('traffic') || 
            className.includes('truck') || className.includes('motor')) {
            mappedResults['Traffic'] += result.score;
        } else if (className.includes('construction') || className.includes('drill') || 
                   className.includes('hammer') || className.includes('saw')) {
            mappedResults['Construction'] += result.score;
        } else if (className.includes('bird') || className.includes('wind') || className.includes('water') ||
                   className.includes('rain') || className.includes('nature')) {
            mappedResults['Nature'] += result.score;
        } else if (className.includes('speech') || className.includes('voice') || className.includes('human') ||
                   className.includes('conversation') || className.includes('people')) {
            mappedResults['Human'] += result.score;
        } else if (className.includes('machine') || className.includes('industrial') || 
                   className.includes('factory') || className.includes('engine')) {
            mappedResults['Industrial'] += result.score;
        } else {
            mappedResults['Other'] += result.score;
        }
    });
    
    // Convert to array and sort by confidence
    const results = Object.entries(mappedResults).map(([name, confidence]) => ({
        name,
        confidence: Math.min(confidence, 1.0), // Ensure confidence doesn't exceed 1
        class: name.toLowerCase()
    }));
    
    results.sort((a, b) => b.confidence - a.confidence);
    return results;
}

// Fallback mock classification for demo purposes
function generateMockClassification() {
    const results = Object.keys(SOUND_CLASSES).map(className => ({
        name: className,
        confidence: Math.random() * 0.8 + 0.2, // Random confidence between 0.2 and 1.0
        class: className.toLowerCase()
    }));
    
    results.sort((a, b) => b.confidence - a.confidence);
    return results;
}

// Display classification results with WHO compliance
export function displayClassificationResults(results) {
    const container = document.getElementById('analysisResults');
    
    // Determine dominant source and estimate noise level
    const dominant = results[0];
    const config = SOUND_CLASSES[dominant.name] || { weight: 0.5, baseline_db: 45 };
    let estimatedDb = config.baseline_db + (dominant.confidence * 10 * config.weight);
    
    // Assess WHO status
    const whoStatus = getWHOStatus(estimatedDb);
    
    // Update regulatory info section
    document.getElementById('regulatoryInfo').style.display = '';
    document.getElementById('whoStatus').textContent = whoStatus.status;
    document.getElementById('whoStatus').style.color = whoStatus.color;
    
    // Update estimated noise level
    document.getElementById('noiseLevel').textContent = `${Math.round(estimatedDb)} dB`;
    
    // Display top 5 results with weights
    container.innerHTML = results.slice(0, 5).map(result => {
        const weight = SOUND_CLASSES[result.name]?.weight || 0.5;
        return `
            <div class="sound-item">
                <span><strong>${result.name}</strong> (${weight}x weight)</span>
                <div class="confidence-bar">
                    <div class="confidence-fill ${result.class}" style="width: ${result.confidence * 100}%"></div>
                </div>
                <span>${Math.round(result.confidence * 100)}%</span>
            </div>
        `;
    }).join('');
}

// WHO compliance assessment
function getWHOStatus(noiseLevel) {
    if (noiseLevel >= WHO_STANDARDS.CRITICAL_LIMIT) {
        return { status: 'Critical - Health Risk', color: '#e74c3c' };
    } else if (noiseLevel >= WHO_STANDARDS.DAY_LIMIT) {
        return { status: 'Exceeds WHO Daytime Limit', color: '#f39c12' };
    } else {
        return { status: 'Within Safe Limits', color: '#27ae60' };
    }
}

// Enhanced anomaly detection
export function detectAnomalies(features) {
    const avgEnergy = features.reduce((sum, f) => sum + f.energy, 0) / features.length;
    const avgZCR = features.reduce((sum, f) => sum + f.zcr, 0) / features.length;
    
    // Detect high energy anomalies (emergency vehicles, alarms)
    if (avgEnergy > 0.7) {
        return { detected: true, type: 'High Energy Anomaly (possible emergency vehicle or alarm)' };
    }
    
    // Detect unusual spectral characteristics
    if (avgZCR > 0.3) {
        return { detected: true, type: 'Unusual Spectral Pattern (possible construction/industrial activity)' };
    }
    
    return { detected: false, type: null };
}

// Noise level prediction (simplified demo)
export function predictNoiseLevel(currentLevel, timeOfDay, weather = 'clear') {
    let prediction = currentLevel;
    
    // Time-based adjustments
    const hour = new Date().getHours();
    if (hour >= 6 && hour <= 9) { // Morning rush
        prediction += 5;
    } else if (hour >= 17 && hour <= 19) { // Evening rush
        prediction += 3;
    } else if (hour >= 22 || hour <= 6) { // Night
        prediction -= 8;
    }
    
    // Weather adjustments
    if (weather === 'rain') {
        prediction -= 3; // Rain dampens traffic noise
    } else if (weather === 'wind') {
        prediction += 2; // Wind can increase background noise
    }
    
    return Math.max(30, Math.min(100, Math.round(prediction)));
}