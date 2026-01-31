// DOM Elements
const jobDescription = document.getElementById('jobDescription');
const analyzeBtn = document.getElementById('analyzeBtn');
const charCount = document.getElementById('charCount');
const loadingState = document.getElementById('loadingState');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const riskCard = document.getElementById('riskCard');
const riskScore = document.getElementById('riskScore');
const riskLevel = document.getElementById('riskLevel');
const reasonsList = document.getElementById('reasonsList');

// Configuration
const API_ENDPOINT = '/analyze-job';
const MAX_CHARS = 5000;

// Event Listeners
jobDescription.addEventListener('input', handleTextareaInput);
analyzeBtn.addEventListener('click', handleAnalyze);
newAnalysisBtn.addEventListener('click', handleNewAnalysis);

/**
 * Handle textarea input and character count
 */
function handleTextareaInput() {
    const text = jobDescription.value;
    const length = text.length;

    // Update character count
    charCount.textContent = length;

    // Truncate if exceeds max
    if (length > MAX_CHARS) {
        jobDescription.value = text.substring(0, MAX_CHARS);
        charCount.textContent = MAX_CHARS;
    }

    // Update button state
    analyzeBtn.disabled = length === 0;
}

/**
 * Handle analyze button click
 */
async function handleAnalyze() {
    const text = jobDescription.value.trim();

    // Validation
    if (!text) {
        showError('Please enter a job description');
        return;
    }

    if (text.length < 20) {
        showError('Please enter a more detailed job description (at least 20 characters)');
        return;
    }

    // Hide previous states
    hideAllSections();
    showLoadingState();

    try {
        const response = await fetchAnalysis(text);
        displayResults(response);
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    }
}

/**
 * Fetch analysis from backend
 */
async function fetchAnalysis(jobDescription) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ job_description: jobDescription }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Validate response structure
        if (
            data.risk_score === undefined ||
            data.risk_level === undefined ||
            !Array.isArray(data.reasons)
        ) {
            throw new Error('Invalid response format from server');
        }

        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            throw new Error('Unable to connect to analysis service. Please try again later.');
        }
        throw error;
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    hideLoadingState();

    // Update risk score
    const score = Math.round(data.risk_score);
    riskScore.textContent = score;

    // Update risk level and styling
    const level = data.risk_level.toUpperCase();
    riskLevel.textContent = level;

    // Apply color coding to risk circle
    riskCard.classList.remove('low', 'medium', 'high');
    riskCard.querySelector('.risk-score-circle').classList.remove('low', 'medium', 'high');
    
    const riskClass = getRiskClass(data.risk_level);
    riskCard.querySelector('.risk-score-circle').classList.add(riskClass);

    // Display reasons
    renderReasons(data.reasons, data.risk_level);

    // Show result section
    resultSection.classList.remove('hidden');

    // Scroll to results
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Render reasons list
 */
function renderReasons(reasons, riskLevel) {
    reasonsList.innerHTML = '';

    if (!reasons || reasons.length === 0) {
        const li = document.createElement('li');
        li.className = 'empty';
        li.textContent = 'No scam indicators detected. This job appears legitimate.';
        reasonsList.appendChild(li);
        return;
    }

    reasons.forEach((reason) => {
        const li = document.createElement('li');
        li.textContent = reason;
        reasonsList.appendChild(li);
    });
}

/**
 * Get risk class for styling
 */
function getRiskClass(riskLevel) {
    const level = riskLevel.toLowerCase();
    if (level === 'low') return 'low';
    if (level === 'medium') return 'medium';
    if (level === 'high') return 'high';
    return 'medium';
}

/**
 * Show error message
 */
function showError(message) {
    hideAllSections();
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
}

/**
 * Handle new analysis
 */
function handleNewAnalysis() {
    jobDescription.value = '';
    jobDescription.focus();
    charCount.textContent = '0';
    analyzeBtn.disabled = true;
    hideAllSections();
}

/**
 * Utility functions for visibility
 */
function hideAllSections() {
    loadingState.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

function showLoadingState() {
    loadingState.classList.remove('hidden');
}

function hideLoadingState() {
    loadingState.classList.add('hidden');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    jobDescription.focus();
    analyzeBtn.disabled = true;
});
