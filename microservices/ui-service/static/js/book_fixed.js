
document.addEventListener('DOMContentLoaded', () => {
    flight_duration();
    initSagaToggles();
});

function flight_duration() {
    document.querySelectorAll(".duration").forEach(element => {
        let time = element.dataset.value.split(":");
        let hours = time[0] || "0";
        let minutes = time[1] || "0";
        element.innerText = hours + "h " + minutes + "m";
    });
}

function add_traveller() {
    let div = document.querySelector('.add-traveller-div');
    let fname = div.querySelector('#fname');
    let lname = div.querySelector('#lname');
    let gender = div.querySelectorAll('.gender');
    let gender_val = null
    
    // Validate first name
    if(fname.value.trim().length === 0) {
        alert("Please enter First Name.");
        return false;
    }
    if(fname.value.trim().length < 2 || fname.value.trim().length > 50) {
        alert("First name must be between 2-50 characters.");
        return false;
    }
    if(!/^[A-Za-z\s]+$/.test(fname.value.trim())) {
        alert("First name should contain only letters and spaces.");
        return false;
    }

    // Validate last name
    if(lname.value.trim().length === 0) {
        alert("Please enter Last Name.");
        return false;
    }
    if(lname.value.trim().length < 2 || lname.value.trim().length > 50) {
        alert("Last name must be between 2-50 characters.");
        return false;
    }
    if(!/^[A-Za-z\s]+$/.test(lname.value.trim())) {
        alert("Last name should contain only letters and spaces.");
        return false;
    }

    if (!gender[0].checked) {
        if (!gender[1].checked) {
            alert("Please select gender.");
            return false;
        }
        else {
            gender_val = gender[1].value;
        }
    }
    else {
        gender_val = gender[0].value;
    }

    let passengerCount = div.parentElement.querySelectorAll(".each-traveller-div .each-traveller").length;

    let traveller = '<div class="row each-traveller">' +
                        '<div>' +
                            '<span class="traveller-name">' + fname.value + ' ' + lname.value + '</span><span>,</span>' +
                            '<span class="traveller-gender">' + gender_val.toUpperCase() + '</span>' +
                        '</div>' +
                        '<input type="hidden" name="passenger' + (passengerCount+1) + 'FName" value="' + fname.value + '">' +
                        '<input type="hidden" name="passenger' + (passengerCount+1) + 'LName" value="' + lname.value + '">' +
                        '<input type="hidden" name="passenger' + (passengerCount+1) + 'Gender" value="' + gender_val + '">' +
                        '<div class="delete-traveller">' +
                            '<button class="btn" type="button" onclick="del_traveller(this)">' +
                                '<svg width="1.1em" height="1.1em" viewBox="0 0 16 16" class="bi bi-x-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">' +
                                    '<path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm2.854-8.354a.5.5 0 0 0-.708-.708L8 7.293 5.854 5.146a.5.5 0 1 0-.708.708L7.293 8l-2.147 2.146a.5.5 0 0 0 .708.708L8 8.707l2.146 2.147a.5.5 0 0 0 .708-.708L8.707 8l2.147-2.146z"/>' +
                                '</svg>' +
                            '</button>' +
                        '</div>' +
                    '</div>';

    div.parentElement.querySelector('.each-traveller-div').innerHTML += traveller;
    div.parentElement.querySelector('.no-traveller').style.display = 'none';
    div.parentElement.querySelector('.traveller-head h6 span').innerText = (passengerCount + 1);
    div.parentElement.querySelector('#p-count').value = (passengerCount + 1);

    fname.value = '';
    lname.value = '';
    gender[0].checked = false;
    gender[1].checked = false;
}

function del_traveller(element) {
    let traveller_div = element.parentElement.parentElement;
    let parent_div = traveller_div.parentElement;
    traveller_div.remove();
    
    let remaining_travellers = parent_div.querySelectorAll('.each-traveller').length;
    parent_div.parentElement.querySelector('.traveller-head h6 span').innerText = remaining_travellers;
    parent_div.parentElement.querySelector('#p-count').value = remaining_travellers;
    
    if (remaining_travellers === 0) {
        parent_div.parentElement.querySelector('.no-traveller').style.display = 'block';
    }
}

// SAGA Demo Helper Functions with Enhanced Logging
let sagaLogContainer = null;

function initializeSagaLogger() {
    if (!sagaLogContainer) {
        sagaLogContainer = document.createElement('div');
        sagaLogContainer.id = 'saga-log-container';
        sagaLogContainer.style.cssText = `
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        `;
        sagaLogContainer.innerHTML = `
            <h5 style="color: #495057; margin-bottom: 15px; font-family: Arial, sans-serif;">📋 SAGA Transaction Logs</h5>
            <div id="saga-logs" style="background: #ffffff; padding: 10px; border: 1px solid #dee2e6; border-radius: 4px; min-height: 200px;"></div>
        `;
        
        // Insert after saga demo section
        const demoSection = document.querySelector('.saga-demo-section');
        if (demoSection) {
            demoSection.parentNode.insertBefore(sagaLogContainer, demoSection.nextSibling);
        }
    }
    return document.getElementById('saga-logs');
}

function logSagaEvent(message, type = 'info', timestamp = true) {
    const logsContainer = initializeSagaLogger();
    const time = timestamp ? new Date().toLocaleTimeString() : '';
    
    const typeColors = {
        'info': '#17a2b8',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'compensation': '#fd7e14'
    };
    
    const typeIcons = {
        'info': 'ℹ️',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'compensation': '🔄'
    };
    
    const logEntry = document.createElement('div');
    logEntry.style.cssText = `
        margin-bottom: 5px;
        padding: 5px 8px;
        border-left: 3px solid ${typeColors[type]};
        background: ${type === 'error' ? '#f8d7da' : type === 'success' ? '#d4edda' : type === 'compensation' ? '#fff3cd' : '#d1ecf1'};
        border-radius: 3px;
    `;
    
    logEntry.innerHTML = `
        <span style="color: ${typeColors[type]}; font-weight: bold;">${typeIcons[type]} ${type.toUpperCase()}</span>
        ${time ? `<span style="color: #6c757d; margin-left: 10px;">[${time}]</span>` : ''}
        <span style="margin-left: 10px;">${message}</span>
    `;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function clearSagaLogs() {
    const logsContainer = document.getElementById('saga-logs');
    if (logsContainer) {
        logsContainer.innerHTML = '';
    }
}

function getFailureDescription(failureType) {
    const descriptions = {
        'simulate_reserveseat_fail': 'Seat Reservation Failure (Step 1)',
        'simulate_authorizepayment_fail': 'Payment Authorization Failure (Step 2)',
        'simulate_awardmiles_fail': 'Miles Award Failure (Step 3)',
        'simulate_confirmbooking_fail': 'Booking Confirmation Failure (Step 4)'
    };
    return descriptions[failureType] || 'Unknown Failure Type';
}

function initSagaToggles() {
    // Ensure only one checkbox is selected at a time
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="simulate_"]');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // Uncheck all other checkboxes
                checkboxes.forEach(other => {
                    if (other !== this) {
                        other.checked = false;
                    }
                });
                
                // Show selected failure type and demonstrate
                const failureType = this.name;
                logSagaEvent(`Selected failure simulation: ${getFailureDescription(failureType)}`, 'warning');
                demonstrateSagaSteps(failureType);
            } else {
                // Clear logs when unchecked
                clearSagaLogs();
            }
        });
    });
}

function demonstrateSagaSteps(failureType) {
    const steps = [
        { name: 'Reserve Seat', service: 'Backend Service', status: 'pending', action: 'Reserving seat for passenger', compensation: 'Release reserved seat and make it available for other passengers' },
        { name: 'Authorize Payment', service: 'Payment Service', status: 'pending', action: 'Processing payment authorization and charging customer', compensation: 'Reverse payment authorization and refund customer amount' },
        { name: 'Award Miles', service: 'Loyalty Service', status: 'pending', action: 'Adding loyalty miles to customer account', compensation: 'Remove awarded loyalty miles from customer account and restore original balance' },
        { name: 'Confirm Booking', service: 'Backend Service', status: 'pending', action: 'Finalizing booking confirmation and generating ticket', compensation: 'Cancel booking confirmation and invalidate generated ticket' }
    ];
    
    // Clear previous logs and initialize
    clearSagaLogs();
    logSagaEvent('🚀 Starting SAGA transaction demonstration', 'info');
    logSagaEvent(`Simulation mode: ${getFailureDescription(failureType)}`, 'warning');
    
    // Determine which step will fail
    const failureStep = {
        'simulate_reserveseat_fail': 0,
        'simulate_authorizepayment_fail': 1,
        'simulate_awardmiles_fail': 2,
        'simulate_confirmbooking_fail': 3
    }[failureType];
    
    logSagaEvent(`Transaction will fail at step ${failureStep + 1}: ${steps[failureStep].name}`, 'warning');
    logSagaEvent('Steps that will execute before failure:', 'info');
    for (let i = 0; i < failureStep; i++) {
        logSagaEvent(`  ${i + 1}. ${steps[i].name} - ${steps[i].action}`, 'info');
    }
    if (failureStep > 0) {
        logSagaEvent('Steps that will need compensation (in reverse order):', 'info');
        for (let i = failureStep - 1; i >= 0; i--) {
            logSagaEvent(`  ${i + 1}. ${steps[i].name} - ${steps[i].compensation}`, 'compensation');
        }
    }
    logSagaEvent('─'.repeat(50), 'info');
    
    // Execute steps with delays to show progression
    let currentStep = 0;
    const executeStep = () => {
        if (currentStep < steps.length) {
            logSagaEvent(`Starting Step ${currentStep + 1}: ${steps[currentStep].name}`, 'info');
            logSagaEvent(`Service: ${steps[currentStep].service}`, 'info');
            logSagaEvent(`Action: ${steps[currentStep].action}`, 'info');
            
            steps[currentStep].status = 'processing';
            
            setTimeout(() => {
                if (currentStep === failureStep) {
                    // This step fails
                    logSagaEvent(`❌ Step ${currentStep + 1} FAILED: ${steps[currentStep].name}`, 'error');
                    logSagaEvent(`Error: Simulated failure in ${steps[currentStep].service}`, 'error');
                    steps[currentStep].status = 'failed';
                    
                    // Start compensation after a delay
                    setTimeout(() => {
                        startCompensation(steps, currentStep);
                    }, 1000);
                } else {
                    // This step succeeds
                    logSagaEvent(`✅ Step ${currentStep + 1} SUCCESS: ${steps[currentStep].name}`, 'success');
                    logSagaEvent(`Completed: ${steps[currentStep].action}`, 'success');
                    steps[currentStep].status = 'success';
                    currentStep++;
                    setTimeout(executeStep, 1000);
                }
            }, 1500);
        } else {
            // All steps completed successfully
            logSagaEvent('🎉 All steps completed successfully! Transaction committed.', 'success');
        }
    };
    
    setTimeout(executeStep, 500);
}

function startCompensation(steps, failedStepIndex) {
    logSagaEvent('─'.repeat(50), 'compensation');
    logSagaEvent('🔄 SAGA COMPENSATION PHASE STARTED', 'compensation');
    logSagaEvent(`Failure occurred at Step ${failedStepIndex + 1}: ${steps[failedStepIndex].name}`, 'error');
    logSagaEvent(`Rolling back ${failedStepIndex} completed step(s) in reverse order...`, 'compensation');
    
    // Compensate completed steps in reverse order
    let compensationStep = failedStepIndex - 1;
    const compensateStep = () => {
        if (compensationStep >= 0) {
            logSagaEvent(`🔄 Compensating Step ${compensationStep + 1}: ${steps[compensationStep].name}`, 'compensation');
            logSagaEvent(`Service: ${steps[compensationStep].service}`, 'compensation');
            logSagaEvent(`Compensation Action: ${steps[compensationStep].compensation}`, 'compensation');
            
            steps[compensationStep].status = 'compensated';
            
            logSagaEvent(`✅ Step ${compensationStep + 1} compensated successfully`, 'compensation');
            compensationStep--;
            setTimeout(compensateStep, 1000);
        } else {
            // Compensation complete
            logSagaEvent('─'.repeat(50), 'compensation');
            logSagaEvent('🔄 SAGA COMPENSATION COMPLETED', 'compensation');
            logSagaEvent('All completed steps have been rolled back successfully', 'compensation');
            logSagaEvent('❌ SAGA TRANSACTION FAILED - System returned to initial state', 'error');
        }
    };
    
    setTimeout(compensateStep, 1000);
}