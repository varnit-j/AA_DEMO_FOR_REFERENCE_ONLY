
/**
 * SAGA Results Page JavaScript - Dynamic Real Logs Display with Streaming
 * Shows logs appearing in real-time to simulate SAGA execution and compensation
 */

// Get URL parameter value
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Add CSS animation for log entries
function addLogAnimationCSS() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .log-entry {
            transition: all 0.3s ease;
        }
        .streaming-indicator {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

// Get CSS class for log level
function getLogLevelClass(level) {
    switch(level.toLowerCase()) {
        case 'info': return 'log-level-info';
        case 'error': return 'log-level-error';
        case 'success': return 'log-level-success';
        case 'warning': return 'log-level-warning';
        default: return 'log-level-info';
    }
}

// Get icon for log entry
function getLogIcon(level, isCompensation) {
    if (isCompensation) {
        return '🔄';
    }
    
    switch(level.toLowerCase()) {
        case 'info': return '📝';
        case 'error': return '❌';
        case 'success': return '✅';
        case 'warning': return '⚠️';
        default: return '📝';
    }
}

// Stream logs with realistic delays
function streamLogsWithDelay(logs, index) {
    if (index === undefined) index = 0;
    
    const container = document.getElementById('dynamic-saga-logs');
    if (!container || index >= logs.length) {
        // Streaming complete
        const indicator = container.querySelector('.streaming-indicator');
        if (indicator) {
            indicator.innerHTML = '✅ Log streaming complete';
            indicator.classList.remove('streaming-indicator');
        }
        return;
    }
    
    const log = logs[index];
    const levelClass = getLogLevelClass(log.log_level || 'info');
    const icon = getLogIcon(log.log_level || 'info', log.is_compensation);
    
    const logEntry = `<div class="log-entry" style="opacity: 0; animation: fadeIn 0.5s ease-in forwards;">
        <span class="log-timestamp">[${log.timestamp}]</span>
        <span class="${levelClass}">[${log.service}]</span>
        <span class="log-message">${icon} ${log.message}</span>
    </div>`;
    
    container.insertAdjacentHTML('beforeend', logEntry);
    
    // Scroll to bottom to show new log
    container.scrollTop = container.scrollHeight;
    
    setTimeout(function() {
        streamLogsWithDelay(logs, index + 1);
    }, 1000);
}

// Initialize result page with real dynamic logs
function initializeResultPage() {
    console.log('[SAGA RESULT] Initializing dynamic result page with real logs');
    
    const correlationId = getUrlParameter('correlation_id') || 'unknown';
    console.log('[SAGA RESULT] Correlation ID:', correlationId);
    
    // Add CSS animations
    addLogAnimationCSS();
    
    // Get saga logs from the template context
    const sagaLogsElement = document.getElementById('saga-logs-data');
    let sagaLogs = [];
    
    console.log('[SAGA RESULT] DIAGNOSTIC - Looking for saga-logs-data element');
    console.log('[SAGA RESULT] DIAGNOSTIC - sagaLogsElement found:', !!sagaLogsElement);
    
    if (sagaLogsElement) {
        console.log('[SAGA RESULT] DIAGNOSTIC - Element content length:', sagaLogsElement.textContent.length);
        console.log('[SAGA RESULT] DIAGNOSTIC - Element content preview:', sagaLogsElement.textContent.substring(0, 200));
        try {
            sagaLogs = JSON.parse(sagaLogsElement.textContent);
            console.log('[SAGA RESULT] Found ' + sagaLogs.length + ' real logs from backend');
            if (sagaLogs.length > 0) {
                console.log('[SAGA RESULT] First log sample:', sagaLogs[0]);
            }
        } catch (e) {
            console.error('[SAGA RESULT] Error parsing saga logs:', e);
            console.error('[SAGA RESULT] Raw content that failed:', sagaLogsElement.textContent);
        }
    } else {
        console.warn('[SAGA RESULT] No saga-logs-data element found, using empty logs');
    }
    
    // Replace placeholder with dynamic logs
    const placeholder = document.getElementById('dynamic-saga-logs-placeholder');
    if (placeholder) {
        // Create dynamic logs container
        const container = document.createElement('div');
        container.id = 'dynamic-saga-logs';
        container.style.cssText = 'background: #1e1e1e; color: #f8f9fa; border-radius: 8px; padding: 20px; font-family: "Courier New", monospace; font-size: 13px; max-height: 400px; overflow-y: auto; margin: 20px 0; border: 1px solid #495057;';
        
        // Replace placeholder with container
        placeholder.parentNode.replaceChild(container, placeholder);
        
        // Display real logs with streaming
        displayRealSagaLogs(correlationId, sagaLogs);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SAGA RESULT] DOM loaded, initializing result page with real logs');
    initializeResultPage();
});

// Display real SAGA logs from backend with streaming animation
function displayRealSagaLogs(correlationId, sagaLogs) {
    const container = document.getElementById('dynamic-saga-logs');
    
    if (!container) {
        console.error('[SAGA RESULT] No dynamic-saga-logs container found');
        return;
    }
    
    console.log('[SAGA RESULT] Starting dynamic log streaming for correlation_id: ' + correlationId);
    
    // Clear container and add header
    container.innerHTML = '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold;">📊 SAGA Transaction Logs - Correlation ID: ' + correlationId + '<div style="font-size: 12px; margin-top: 5px; opacity: 0.8;">🔄 Streaming logs in real-time...</div></div>';
    
    // If no logs available, show message for now
    if (sagaLogs.length === 0) {
        container.innerHTML += '<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">⚠️ No real-time logs available for this transaction.</div>';
        return;
    }
    
    // Stream real logs with delays
    streamLogsWithDelay(sagaLogs, 0);
}