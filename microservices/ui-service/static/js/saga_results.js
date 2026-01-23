
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
    console.log('[SAGA RESULT] URL failure_type parameter:', urlFailureType);
    
    if (urlFailureType) {
        return urlFailureType;
    }
    
    // Try to get from backend saga_status if available
    const sagaStatusElement = document.querySelector('[data-failed-step]');
    if (sagaStatusElement) {
        const failedStep = sagaStatusElement.getAttribute('data-failed-step');
        const stepMapping = {
            'ReserveSeat': 'reserveseat',
            'AuthorizePayment': 'authorizepayment',
            'AwardMiles': 'awardmiles',
            'ConfirmBooking': 'confirmbooking'
        };
        return stepMapping[failedStep] || 'confirmbooking';
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
    
    // Generate logs for successful steps
    for (let i = 1; i < failedStep.step_number; i++) {
        const step = Object.values(SAGA_STEPS).find(s => s.step_number === i);
        if (step) {
            const stepTime = new Date(currentTime.getTime() + (i * 1000));
            logs.push(createLogEntry(stepTime, step.service, 'INFO', `${step.icon} ${step.name} step initiated for correlation_id: ${getUrlParameter('correlation_id') || '5ad32d0b-0117-49f5-820e-d2ad5a282255'}`));
            logs.push(createLogEntry(new Date(stepTime.getTime() + 500), step.service, 'SUCCESS', `✅ ${step.name} successful for ${getUrlParameter('correlation_id') || '5ad32d0b-0117-49f5-820e-d2ad5a282255'}`));
        }
    }
    
    // Add failed step
    const failTime = new Date(currentTime.getTime() + (failedStep.step_number * 1000));
    logs.push(createLogEntry(failTime, failedStep.service, 'INFO', `${failedStep.icon} ${failedStep.name} step initiated for correlation_id: ${getUrlParameter('correlation_id') || '5ad32d0b-0117-49f5-820e-d2ad5a282255'}`));
    logs.push(createLogEntry(new Date(failTime.getTime() + 500), failedStep.service, 'ERROR', `❌ Simulated failure in ${failedStep.name} for ${getUrlParameter('correlation_id') || '5ad32d0b-0117-49f5-820e-d2ad5a282255'}`));
    
    // Add compensation header
    logs.push(`<div style="background: #ffeaa7; color: #856404; padding: 8px; border-radius: 5px; margin: 10px 0; font-weight: bold;">
        🔄 COMPENSATION PHASE - Rolling back completed steps
    </div>`);
    
    // Add compensation for each completed step (in reverse order)
    for (let i = failedStep.step_number - 1; i >= 1; i--) {
        const step = Object.values(SAGA_STEPS).find(s => s.step_number === i);
        if (step) {
            const compTime = new Date(currentTime.getTime() + ((failedStep.step_number + (failedStep.step_number - i)) * 1000));
            logs.push(createLogEntry(compTime, step.service + ' COMPENSATION', 'WARNING', `🔄 Reverse${step.name} compensation initiated`));
            logs.push(createLogEntry(new Date(compTime.getTime() + 500), step.service + ' COMPENSATION', 'SUCCESS', `✅ ${step.name} compensation completed`));
        }
    }
    
    container.innerHTML = logs.join('');
}

/**
 * Create a log entry HTML
 */
function createLogEntry(timestamp, service, level, message) {
    const timeStr = timestamp.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Calcutta',
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }) + ' IST';
    
    const levelColor = {
        'INFO': '#17a2b8',
        'SUCCESS': '#28a745',
        'ERROR': '#dc3545',
        'WARNING': '#ffc107'
    }[level] || '#6c757d';
    
    return `<div style="margin-bottom: 5px; padding: 3px 0; border-bottom: 1px solid #343a40;">
        <span style="color: #6c757d; margin-right: 10px;">[${timeStr}]</span>
        <span style="color: ${levelColor}; font-weight: bold; margin-right: 10px;">[${service}]</span>
        <span>${message}</span>
    </div>`;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SAGA RESULT] DOM loaded, initializing result page');
    initializeResultPage();
});