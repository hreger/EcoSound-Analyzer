// js/map-handler.js - Leaflet map integration and geospatial visualization

import { showStatus } from './audio-processor.js';

// Global map variables
export let map = null;
export let heatLayers = {};
let uncertaintyLayer = null;

// Initialize Leaflet map with heat layers
export function initializeMap() {
    try {
        // Create map centered on Bangalore, India
        map = L.map('map').setView([12.9716, 77.5946], 12);

        // Add OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors | EcoSound Analyzer',
            maxZoom: 19
        }).addTo(map);

        // Initialize heat layers for different sound sources
        heatLayers = {
            traffic: L.heatLayer([], { 
                radius: 25, 
                blur: 15, 
                maxZoom: 17,
                gradient: {0.0: '#3498db', 0.5: '#f39c12', 1.0: '#e74c3c'}
            }).addTo(map),
            
            construction: L.heatLayer([], { 
                radius: 25, 
                blur: 15, 
                maxZoom: 17,
                gradient: {0.0: '#f1c40f', 0.5: '#e67e22', 1.0: '#e74c3c'}
            }).addTo(map),
            
            nature: L.heatLayer([], { 
                radius: 20, 
                blur: 12, 
                maxZoom: 17,
                gradient: {0.0: '#2ecc71', 0.5: '#27ae60', 1.0: '#16a085'}
            }).addTo(map)
        };

        // Add sample noise pollution data in Bangalore
        addSampleMarkers();

        // Store map reference globally for other modules
        window.map = map;

        console.log('Map initialized successfully');
        
    } catch (error) {
        console.error('Map initialization error:', error);
        showStatus('Error initializing map', 'error');
    }
}

// Add sample markers with realistic data around Bangalore
function addSampleMarkers() {
    const sampleData = [
        { lat: 12.9716, lng: 77.5946, noise: 78, type: 'traffic', confidence: 0.92 },
        { lat: 12.9735, lng: 77.6011, noise: 85, type: 'construction', confidence: 0.87 },
        { lat: 12.9694, lng: 77.5990, noise: 42, type: 'nature', confidence: 0.94 },
        { lat: 12.9790, lng: 77.5920, noise: 82, type: 'traffic', confidence: 0.89 },
        { lat: 12.9650, lng: 77.5850, noise: 58, type: 'human', confidence: 0.76 },
        { lat: 12.9742, lng: 77.5954, noise: 88, type: 'industrial', confidence: 0.91 },
        { lat: 12.9774, lng: 77.5900, noise: 52, type: 'nature', confidence: 0.83 },
        { lat: 12.9700, lng: 77.6000, noise: 73, type: 'traffic', confidence: 0.85 },
        { lat: 12.9682, lng: 77.5908, noise: 67, type: 'human', confidence: 0.78 }
    ];

    sampleData.forEach(point => {
        const color = getNoiseColor(point.noise);
        const radius = Math.max(8, point.noise / 8);
        const whoStatus = getWHOStatus(point.noise);
        
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: radius,
            fillColor: color,
            color: color,
            weight: 2,
            fillOpacity: point.confidence * 0.8
        }).addTo(map);
        
        marker.bindPopup(`
            <div style="min-width: 200px;">
                <strong>🔊 ${point.noise} dB</strong><br>
                <strong>Source:</strong> ${point.type.charAt(0).toUpperCase() + point.type.slice(1)}<br>
                <strong>Confidence:</strong> ${Math.round(point.confidence * 100)}%<br>
                <strong>WHO Status:</strong> <span style="color: ${whoStatus.color};">${whoStatus.status}</span><br>
                <small>📅 ${new Date().toLocaleString()}</small>
            </div>
        `);
        
        if (heatLayers[point.type]) {
            heatLayers[point.type].addLatLng([point.lat, point.lng, point.noise / 100]);
        }
    });
}

// Add noise marker to map
export function addNoiseMarker(lat, lng, noiseLevel, confidence) {
    if (!map) return;
    
    const color = getNoiseColor(noiseLevel);
    const whoStatus = getWHOStatus(noiseLevel);
    
    const marker = L.circleMarker([lat, lng], {
        radius: Math.max(8, noiseLevel / 10),
        fillColor: color,
        color: color,
        weight: 3,
        fillOpacity: confidence * 0.8 // Use confidence for transparency
    }).addTo(map);
    
    // Enhanced popup with WHO compliance
    marker.bindPopup(`
        <div style="min-width: 200px;">
            <strong>🔊 ${noiseLevel} dB</strong><br>
            <strong>Confidence:</strong> ${Math.round(confidence * 100)}%<br>
            <strong>WHO Status:</strong> <span style="color: ${whoStatus.color};">${whoStatus.status}</span><br>
            <small>📅 ${new Date().toLocaleString()}</small>
        </div>
    `).openPopup();
    
    // Pan to the new marker
    map.panTo([lat, lng]);
    
    return marker;
}

// Get color based on WHO noise standards
function getNoiseColor(noiseLevel) {
    if (noiseLevel >= 70) return '#e74c3c'; // Critical (red)
    if (noiseLevel >= 55) return '#f39c12'; // Exceeds WHO limit (orange)
    if (noiseLevel >= 45) return '#f1c40f'; // Moderate (yellow)
    return '#27ae60'; // Safe (green)
}

// WHO compliance assessment
function getWHOStatus(noiseLevel) {
    if (noiseLevel >= 70) {
        return { status: 'Critical - Health Risk', color: '#e74c3c' };
    } else if (noiseLevel >= 55) {
        return { status: 'Exceeds WHO Daytime Limit', color: '#f39c12' };
    } else {
        return { status: 'Within Safe Limits', color: '#27ae60' };
    }
}

// Toggle heat map layers
export function toggleLayer(layerName) {
    const checkbox = document.getElementById(layerName + 'Layer');
    
    if (checkbox && heatLayers[layerName]) {
        if (checkbox.checked) {
            map.addLayer(heatLayers[layerName]);
        } else {
            map.removeLayer(heatLayers[layerName]);
        }
    }
}

// Toggle uncertainty visualization
export function toggleUncertainty() {
    const checkbox = document.getElementById('uncertaintyLayer');
    
    if (checkbox.checked) {
        if (!uncertaintyLayer) {
            // Create uncertainty layer (demo implementation)
            uncertaintyLayer = L.layerGroup().addTo(map);
            // Add some sample uncertainty circles
            addUncertaintyCircles();
        }
        showStatus('Uncertainty visualization enabled', 'info');
    } else {
        if (uncertaintyLayer) {
            map.removeLayer(uncertaintyLayer);
            uncertaintyLayer = null;
        }
        showStatus('Uncertainty visualization disabled', 'info');
    }
}

// Add uncertainty visualization circles
function addUncertaintyCircles() {
    const sampleUncertaintyPoints = [
        { lat: 40.7589, lng: -73.9851, uncertainty: 0.3 },
        { lat: 40.7505, lng: -73.9934, uncertainty: 0.5 },
        { lat: 40.7282, lng: -73.9942, uncertainty: 0.2 }
    ];
    
    sampleUncertaintyPoints.forEach(point => {
        const radius = point.uncertainty * 500; // Scale uncertainty to meters
        const circle = L.circle([point.lat, point.lng], {
            radius: radius,
            fillColor: '#9b59b6',
            color: '#8e44ad',
            weight: 2,
            fillOpacity: 0.2
        });
        
        circle.bindPopup(`
            <strong>Prediction Uncertainty</strong><br>
            Confidence: ${Math.round((1 - point.uncertainty) * 100)}%<br>
            Uncertainty Radius: ${Math.round(radius)}m
        `);
        
        uncertaintyLayer.addLayer(circle);
    });
}