// js/main.js

import { processAudioFile, toggleRecording, submitFeedback, showStatus } from './audio-processor.js';
import { initializeMap, toggleLayer, toggleUncertainty } from './map-handler.js';
import { initializeUrbanPlanningMap } from './urban-planning-map.js';

// Global variables
window.userConsented = false;

document.addEventListener('DOMContentLoaded', function() {
    showConsentPopup();
    setupEventListeners();
});

// Consent management
function showConsentPopup() {
    document.getElementById('consentPopup').style.display = 'flex';
}

function acceptConsent() {
    window.userConsented = true;
    document.getElementById('consentPopup').style.display = 'none';
    initializeApp();
    showStatus('Welcome! Your privacy is protected. 🔒', 'success');
}

function declineConsent() {
    showStatus('Cannot proceed without consent for data processing.', 'error');
}

function initializeApp() {
    initializeMap();
    loadSampleData();
    setupGeolocation();
}

function setupViewToggle() {
    const noiseBtn = document.getElementById('noiseMapBtn');
    const urbanBtn = document.getElementById('urbanPlanningBtn');

    noiseBtn.addEventListener('click', () => {
        noiseBtn.classList.add('active');
        urbanBtn.classList.remove('active');
        document.getElementById('noiseMapContainer').style.display = '';
        document.getElementById('urbanPlanningContainer').style.display = 'none';
    });

    urbanBtn.addEventListener('click', () => {
        urbanBtn.classList.add('active');
        noiseBtn.classList.remove('active');
        document.getElementById('noiseMapContainer').style.display = 'none';
        document.getElementById('urbanPlanningContainer').style.display = '';
        initializeUrbanPlanningMap();
    });
}

// Setup event listeners for file upload and drag/drop
function setupEventListeners() {
    const uploadSection = document.getElementById('uploadSection');
    const audioFile = document.getElementById('audioFile');

    // Drag and drop functionality
    uploadSection.addEventListener('dragover', handleDragOver);
    uploadSection.addEventListener('drop', handleDrop);
    uploadSection.addEventListener('dragleave', handleDragLeave);

    // File input change
    audioFile.addEventListener('change', handleFileSelect);

    setupViewToggle();
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processAudioFile(files[0]);
    }
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        processAudioFile(e.target.files[0]);
    }
}

// Geolocation setup
function setupGeolocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                if (window.map) {
                    window.map.setView([latitude, longitude], 13);
                }
                showStatus(`📍 Located at ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`, 'info');
            },
            error => {
                console.log('Geolocation error:', error);
                showStatus('Using default location (geolocation unavailable)', 'info');
            }
        );
    }
}

// Load sample data for demo
function loadSampleData() {
    showStatus('Welcome to EcoSound Analyzer! Upload audio or start recording to begin.', 'info');
}

// Expose functions to global scope for HTML onclick handlers
window.acceptConsent = acceptConsent;
window.declineConsent = declineConsent;
window.toggleRecording = toggleRecording;
window.submitFeedback = submitFeedback;
window.toggleLayer = toggleLayer;
window.toggleUncertainty = toggleUncertainty;
