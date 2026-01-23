
/**
 * SAGA Results Page JavaScript - Dynamic Result Display
 * Handles dynamic log display and visual feedback on result page
 */

// SAGA Step Configuration
const SAGA_STEPS = {
    'reserveseat': {
        name: 'Reserve Seat',
        icon: '💺',
        service: 'Backend Service',
        description: 'Reserve seat on the selected flight',
        step_number: 1
    },
    'authorizepayment': {
        name: 'Authorize Payment',
        icon: '💳',
        service: 'Payment Service', 
        description: 'Authorize payment for the booking',
        step_number: 2
    },
    'awardmiles': {
        name: 'Award Miles',
        icon: '🏆',
        service: 'Loyalty Service',
        description: 'Award loyalty miles to customer',
        step_number: 3
    },
    'confirmbooking': {
        name: 'Confirm Booking',
        icon: '📋',
        service: 'Backend Service',
        description: 'Finalize and confirm the booking',
        step_number: 4
    }
};

/**
 * Get URL parameter value
 */
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

/**
 * Determine failure type from various sources
 */
function determineFailureType() {
    // Try to get from URL parameter first
    const urlFailureType = getUrlParameter('failure_type');
    if (urlFailureType) {
        return urlFailureType;
    }
    
    // Default to confirmbooking failure
    return 'confirmbooking';
}

/**
 * Initialize result page with dynamic content
 */
function initializeResultPage() {
    console.log('[SAGA RESULT] Initializing dynamic result page');
    
    const failureType = determineFailureType();
    console.log('[SAGA RESULT] Detected failure type:', failureType);
    
    // Replace placeholder with dynamic logs
    const placeholder = document.getElementById('dynamic-saga-logs-placeholder');
    if (placeholder) {
        // Create dynamic logs container
        const container = document.createElement('div');
        container.id = 'dynamic-saga-logs';
        container.style.cssText = `
            background: #1e1e1e;
            color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
            margin: 20px 0;
            border: 1px solid #495057;
        `;
        
        // Replace placeholder with container
        placeholder.parentNode.replaceChild(container, placeholder);
        
        // Generate and display logs
        displayResultPageLogs(failureType);
        
        // Add steps progress
        addStepsProgress(failureType);
    }
}

/**
 * Display logs for result page based on failure type
 */
function displayResultPageLogs(failureType) {
    const container = document.getElementById('dynamic-saga-logs');
    const failedStep = SAGA_STEPS[failureType];
    
    if (!failedStep) {
        console.error(`[SAGA RESULT] Unknown failure type: ${failureType}`);
        return;
    }
    
    const currentTime = new Date();
    let logs = [];
    
    // Add header
    logs.push(`<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold;">
        📊 SAGA Transaction Failed - ${failedStep.name} Step
    </div>`);
    
    container.innerHTML = logs.join('');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SAGA RESULT] DOM loaded, initializing result page');
    initializeResultPage();
});