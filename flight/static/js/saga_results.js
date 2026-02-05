
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
    
    // CRITICAL FIX: Check if dynamic logs container already exists
    const existingContainer = document.getElementById('dynamic-saga-logs');
    if (existingContainer) {
        console.log('[SAGA RESULT] Found existing dynamic logs container, fetching real logs...');
        // Get correlation ID and fetch real logs
        const correlationId = getCorrelationIdFromPage();
        if (correlationId) {
            fetchRealSagaLogs(correlationId, existingContainer, SAGA_STEPS[failureType]);
        } else {
            console.log('[SAGA RESULT] No correlation ID found, showing static demo logs');
            displayStaticDemoLogs(existingContainer, SAGA_STEPS[failureType]);
        }
        return;
    }
    
    // Legacy code for placeholder replacement (if needed)
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
    
    // DIAGNOSTIC: Add comprehensive logging for debugging
    console.log('[SAGA RESULT DEBUG] ===== DISPLAY LOGS FUNCTION CALLED =====');
    console.log('[SAGA RESULT DEBUG] Failure type:', failureType);
    console.log('[SAGA RESULT DEBUG] Failed step:', failedStep);
    console.log('[SAGA RESULT DEBUG] Container element:', container);
    
    // Get correlation ID from URL or page
    const correlationId = getCorrelationIdFromPage();
    console.log('[SAGA RESULT DEBUG] Correlation ID:', correlationId);
    
    if (!correlationId) {
        console.error('[SAGA RESULT DEBUG] No correlation ID found - cannot fetch real logs');
        displayStaticDemoLogs(container, failedStep);
        return;
    }
    
    // CRITICAL FIX: Fetch real logs from backend API
    console.log('[SAGA RESULT DEBUG] Attempting to fetch real logs from backend...');
    fetchRealSagaLogs(correlationId, container, failedStep);
}

/**
 * Get correlation ID from page URL or DOM
 */
function getCorrelationIdFromPage() {
    // Try window variable first (set by template)
    if (window.sagaCorrelationId) {
        console.log('[SAGA RESULT DEBUG] Found correlation ID in window variable:', window.sagaCorrelationId);
        return window.sagaCorrelationId;
    }
    
    // Try URL parameter
    const urlCorrelationId = getUrlParameter('correlation_id');
    if (urlCorrelationId) {
        console.log('[SAGA RESULT DEBUG] Found correlation ID in URL:', urlCorrelationId);
        return urlCorrelationId;
    }
    
    // Try DOM data attribute
    const correlationElement = document.querySelector('[data-correlation-id]');
    if (correlationElement) {
        const domCorrelationId = correlationElement.getAttribute('data-correlation-id');
        console.log('[SAGA RESULT DEBUG] Found correlation ID in DOM:', domCorrelationId);
        return domCorrelationId;
    }
    
    // Try to extract from page text
    const pageText = document.body.innerText;
    const correlationMatch = pageText.match(/Correlation ID:\s*([a-f0-9-]+)/i);
    if (correlationMatch) {
        const textCorrelationId = correlationMatch[1];
        console.log('[SAGA RESULT DEBUG] Found correlation ID in page text:', textCorrelationId);
        return textCorrelationId;
    }
    
    console.error('[SAGA RESULT DEBUG] No correlation ID found anywhere on page');
    return null;
}

/**
 * Fetch real SAGA logs from backend API
 */
function fetchRealSagaLogs(correlationId, container, failedStep) {
    console.log('[SAGA RESULT DEBUG] Fetching logs for correlation ID:', correlationId);
    
    // Show loading indicator
    container.innerHTML = `
        <div style="text-align: center; padding: 20px; color: #6c757d;">
            <div style="font-size: 18px; margin-bottom: 10px;">📊</div>
            <div>Loading SAGA transaction logs...</div>
            <div style="font-size: 12px; margin-top: 10px;">Correlation ID: ${correlationId}</div>
        </div>
    `;
    
    // Make API call to backend
    fetch(`/api/saga/logs/${correlationId}/`)
        .then(response => {
            console.log('[SAGA RESULT DEBUG] API response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('[SAGA RESULT DEBUG] API response data:', data);
            if (data.success && data.logs && data.logs.length > 0) {
                displayRealLogs(container, data.logs, correlationId);
            } else {
                console.warn('[SAGA RESULT DEBUG] No logs found, showing demo logs');
                displayStaticDemoLogs(container, failedStep);
            }
        })
        .catch(error => {
            console.error('[SAGA RESULT DEBUG] Error fetching logs:', error);
            displayStaticDemoLogs(container, failedStep);
        });
}

/**
 * Display real logs from backend API
 */
function displayRealLogs(container, logs, correlationId) {
    console.log('[SAGA RESULT DEBUG] Displaying real logs:', logs.length, 'entries');
    
    let logHtml = `
        <div style="background: #28a745; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold;">
            📊 SAGA Transaction Logs - Correlation ID: ${correlationId}
        </div>
        <div style="background: #17a2b8; color: white; padding: 8px; border-radius: 5px; margin-bottom: 10px; font-size: 12px;">
            🔄 Streaming logs in real-time...
        </div>
    `;
    
    logs.forEach(log => {
        const levelClass = `log-level-${log.log_level}`;
        const compensationIndicator = log.is_compensation ? ' [COMPENSATION]' : '';
        
        logHtml += `
            <div class="log-entry">
                <span class="log-timestamp">[${log.timestamp}]</span>
                <span class="${levelClass}">[${log.service}${compensationIndicator}]</span> ${log.message}
            </div>
        `;
    });
    
    container.innerHTML = logHtml;
}

/**
 * Display static demo logs as fallback
 */
function displayStaticDemoLogs(container, failedStep) {
    console.log('[SAGA RESULT DEBUG] Displaying static demo logs for:', failedStep.name);
    
    const currentTime = new Date();
    let logs = [];
    
    // Add header
    logs.push(`<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold;">
        📊 SAGA Transaction Failed - ${failedStep.name} Step (Demo Logs)
    </div>`);
    
    container.innerHTML = logs.join('');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SAGA RESULT] DOM loaded, initializing result page');
    initializeResultPage();
});