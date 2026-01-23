document.addEventListener('DOMContentLoaded', () => {
    flight_duration();
    initSagaToggles();
});

function flight_duration() {
    document.querySelectorAll(".duration").forEach(element => {
        let time = element.dataset.value.split(":");
        element.innerText = time[0]+"h "+time[1]+"m";
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

    let traveller = `<div class="row each-traveller">
                        <div>
                            <span class="traveller-name">${fname.value} ${lname.value}</span><span>,</span>
                            <span class="traveller-gender">${gender_val.toUpperCase()}</span>
                        </div>
                        <input type="hidden" name="passenger${passengerCount+1}FName" value="${fname.value}">
                        <input type="hidden" name="passenger${passengerCount+1}LName" value="${lname.value}">
                        <input type="hidden" name="passenger${passengerCount+1}Gender" value="${gender_val}">
                        <div class="delete-traveller">
                            <button class="btn" type="button" onclick="del_traveller(this)">
                                <svg width="1.1em" height="1.1em" viewBox="0 0 16 16" class="bi bi-x-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                    <path fill-rule="evenodd" d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                                </svg>
                            </button>
                        </div>
                    </div>`;
    div.parentElement.querySelector(".each-traveller-div").innerHTML += traveller;
    div.parentElement.querySelector("#p-count").value = passengerCount+1;
    div.parentElement.querySelector(".traveller-head h6 span").innerText = passengerCount+1;
    div.parentElement.querySelector(".no-traveller").style.display = 'none';
    fname.value = "";
    lname.value = "";
    gender.forEach(radio => {
        radio.checked = false;
    });

    let pcount = document.querySelector("#p-count").value;
    let fare = document.querySelector("#basefare").value;
    let fee = document.querySelector("#fee").value;
    if (parseInt(pcount)!==0) {
        // Format amounts properly with INR currency symbol
        let baseFareTotal = parseInt(fare) * parseInt(pcount);
        let totalFareAmount = baseFareTotal + parseInt(fee);
        
        document.querySelector(".base-fare-value span").innerText = formatINR(baseFareTotal);
        document.querySelector(".total-fare-value span").innerText = formatINR(totalFareAmount);
    }

}

function del_traveller(btn) {
    let traveller = btn.parentElement.parentElement;
    let tvl = btn.parentElement.parentElement.parentElement.parentElement;
    let cnt = tvl.querySelector("#p-count");
    cnt.value = parseInt(cnt.value)-1;
    tvl.querySelector(".traveller-head h6 span").innerText = cnt.value;
    if(parseInt(cnt.value) <= 0) {
        tvl.querySelector('.no-traveller').style.display = 'block';
    }
    traveller.remove();
    
    let pcount = document.querySelector("#p-count").value;
    let fare = document.querySelector("#basefare").value;
    let fee = document.querySelector("#fee").value;
    if (parseInt(pcount) !== 0) {
        // Format amounts properly with INR currency symbol
        let baseFareTotal = parseInt(fare) * parseInt(pcount);
        let totalFareAmount = baseFareTotal + parseInt(fee);
        
        document.querySelector(".base-fare-value span").innerText = formatINR(baseFareTotal);
        document.querySelector(".total-fare-value span").innerText = formatINR(totalFareAmount);
    }
}

function book_submit() {
    console.log("[DEBUG] book_submit() called");
    let pcount = document.querySelector("#p-count");
    console.log("[DEBUG] Passenger count:", pcount ? pcount.value : "null");
    
    // Check if any SAGA demo checkbox is selected
    const sagaCheckboxes = document.querySelectorAll('.saga-demo-section input[type="checkbox"]:checked');
    console.log("[DEBUG] SAGA checkboxes checked:", sagaCheckboxes.length);
    
    if (sagaCheckboxes.length > 0) {
        console.log("[DEBUG] SAGA DEMO MODE - Allowing form submission with SAGA parameters");
        
        if(parseInt(pcount.value) > 0) {
            const checkedCheckbox = sagaCheckboxes[0];
            console.log(`[DEBUG] SAGA MODE - Submitting with failure type: ${checkedCheckbox.name}`);
            
            // Add a hidden field to indicate SAGA mode
            const form = document.querySelector('form');
            let sagaModeInput = document.querySelector('input[name="saga_demo_mode"]');
            if (!sagaModeInput) {
                sagaModeInput = document.createElement('input');
                sagaModeInput.type = 'hidden';
                sagaModeInput.name = 'saga_demo_mode';
                form.appendChild(sagaModeInput);
            }
            sagaModeInput.value = 'true';
            
            // Allow form submission to proceed with SAGA parameters
            return true;
        } else {
            alert("Please add at least one passenger before starting SAGA demo.");
            return false;
        }
    }
    
    // Normal booking flow
    if(parseInt(pcount.value) > 0) {
        console.log("[DEBUG] Normal booking - allowing form submission");
        return true;
    }
    alert("Please add atleast one passenger.")
    return false;
}

// Helper function to format INR currency
function formatINR(amount) {
    if (amount == null || isNaN(amount)) {
        return "₹0";
    }
    return "₹" + parseInt(amount).toLocaleString('en-IN');
}

// SAGA Demo Functions
function initSagaToggles() {
    console.log("[DEBUG] SAGA TOGGLE - Initializing SAGA demo toggles");
    
    const sagaSection = document.querySelector('.saga-demo-section');
    if (sagaSection) {
        console.log("[DEBUG] SAGA TOGGLE - SAGA demo section found!");
        
        // Add event listeners to toggle switches for mutual exclusivity
        const toggles = sagaSection.querySelectorAll('input[type="checkbox"]');
        toggles.forEach((toggle) => {
            toggle.addEventListener('change', function() {
                if (this.checked) {
                    // Uncheck other toggles
                    toggles.forEach(otherToggle => {
                        if (otherToggle !== this) {
                            otherToggle.checked = false;
                        }
                    });
                    console.log(`[DEBUG] SAGA TOGGLE - Selected: ${this.name}`);
                }
            });
        });
    } else {
        console.log("[DEBUG] SAGA TOGGLE - SAGA demo section NOT found!");
    }
}

function showSagaDemo(failureType) {
    console.log(`[SAGA DEMO] Starting SAGA demonstration with failure type: ${failureType}`);
    
    const failureDescriptions = {
        'simulate_reserveseat_fail': 'Seat Reservation Failure (Step 1)',
        'simulate_authorizepayment_fail': 'Payment Authorization Failure (Step 2)',
        'simulate_awardmiles_fail': 'Miles Award Failure (Step 3)',
        'simulate_confirmbooking_fail': 'Booking Confirmation Failure (Step 4)'
    };
    
    const description = failureDescriptions[failureType] || 'Unknown Failure Type';
    
    // Simple alert for now - can be enhanced later
    alert(`SAGA Demo: ${description}\n\nThis demonstrates the SAGA pattern where:\n1. Each step is executed\n2. If a step fails, compensation actions are triggered\n3. All completed steps are rolled back\n\nIn a real implementation, you would see step-by-step progression and compensation.`);
    
    console.log(`[SAGA DEMO] Demo completed for: ${description}`);
}