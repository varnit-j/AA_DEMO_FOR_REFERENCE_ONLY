# Complete Booking Flow Analysis & Fixes

## Problem Identified: "DEBUG: No flight1 data - SAGA toggles may not work"

### Root Cause
When clicking "Proceed to Payment" or checking SAGA failure boxes, the UI showed:
```
DEBUG: No flight1 data - SAGA toggles may not work
```

This occurred because **the review() view was not properly handling backend service failures**.

---

## Complete Booking Flow

```
Search Results Page (search.html)
    ↓ User clicks "Book Flight" button
    ↓
search.html → GET params: flight1Id, flight1Date, seatClass
    ↓
review() view in ui/views.py
    ├─ Receives GET params with flight1Id
    ├─ Calls: call_backend_api(f'api/flights/{flight1_id}/')
    │   └─ If FAILS → flight1_data = None
    │       └─ Returns error page (AFTER FIX)
    │       └─ Previously: rendered book.html without flight1 in context
    └─ If SUCCESS → flight1_data added to context
    ↓
book.html template renders
    ├─ {% if flight1 %} → shows SAGA section + booking form
    │   └─ SAGA checkboxes are now visible
    │   └─ Hidden field flight1 ID is set
    └─ {% else %} → shows error message + hidden SAGA section
        └─ Cannot use SAGA checkboxes (no flight1 data)
    ↓
User adds passengers and checks SAGA failure box (optional)
    ↓
book_submit() JavaScript function
    ├─ Checks if any SAGA checkbox is checked
    ├─ If YES → sets saga_demo_mode='true'
    └─ If NO → saga_demo_mode='false' (normal booking)
    ↓
Submits form POST to book() view
    ↓
book() view in ui/views.py
    ├─ Extracts saga_demo_mode from POST
    ├─ Extracts booking_data + passengers
    ├─ Calls: call_backend_api('api/saga/start-booking/', 'POST', booking_data)
    ├─ If SAGA mode → redirect to /saga/results/?correlation_id=...
    └─ If normal mode → extracts flight data & renders payment.html
    ↓
Payment Processing
    ├─ User enters card details or selects payment method
    ├─ Form POST to payment() view
    └─ Process payment and confirm booking
```

---

## Key Files & Their Responsibilities

### 1. **microservices/ui-service/templates/flight/search.html**
**Role**: Flight search results UI

**Critical Part**:
```html
<form action="{% url 'review' %}" method="GET" style="display: flex;">
    <input type="hidden" name="flight1Id" value="{{flight.id}}">
    <input type="hidden" name="flight1Date", value="{{depart_date|date:'d-m-Y'}}">
    <input type="hidden" name="seatClass" value="{{seat}}">
    <button class="btn btn-primary o-b" type="submit">
        Book Flight
    </button>
</form>
```

**Data passed to review()**:
- `flight1Id`: Flight record ID from backend
- `flight1Date`: Departure date (format: dd-mm-yyyy)
- `seatClass`: Seat class (economy/business/first)

---

### 2. **microservices/ui-service/ui/views.py → review() function**
**Role**: Load flight data from backend and render booking form

**BEFORE FIX** (BROKEN):
```python
def review(request):
    flight1_id = request.GET.get('flight1Id')
    # ... code ...
    flight1_data = call_backend_api(f'api/flights/{flight1_id}/')
    if flight1_data:
        context['flight1'] = flight1_data
    # If flight1_data is None, flight1 is NOT in context
    # book.html renders without flight1 data → SAGA section hidden
    return render(request, "flight/book.html", context)
```

**AFTER FIX** (WORKS):
```python
def review(request):
    flight1_id = request.GET.get('flight1Id')
    if not flight1_id:
        # No flight ID provided → return error page
        return render(request, "flight/book.html", {
            'error': 'Missing flight ID. Please select a flight from search results.',
            'error_type': 'missing_flight_id'
        })
    
    flight1_data = call_backend_api(f'api/flights/{flight1_id}/')
    if not flight1_data:
        # Backend unavailable or flight not found → return error page
        return render(request, "flight/book.html", {
            'error': f'Failed to load flight details. Backend service is unreachable.',
            'error_type': 'backend_unavailable'
        })
    
    # Success → flight1 in context, SAGA section rendered
    context['flight1'] = flight1_data
    return render(request, "flight/book.html", context)
```

---

### 3. **microservices/ui-service/templates/flight/book.html**
**Role**: Booking form with SAGA demo controls

**Key Sections**:

#### A. Error Display (NEW)
```html
{% if error %}
    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb;">
        <h4>{{ error_type|title }} Error</h4>
        <p>{{ error }}</p>
    </div>
{% endif %}
```

#### B. Flight Data & Hidden Fields
```html
{% if flight1 %}
    <input type="hidden" name="flight1" value="{{flight1.id}}">
    <!-- Flight details display -->
    <div>{{flight1.airline}} - {{flight1.flight_number}}</div>
{% else %}
    <div style="color: red;">❌ ERROR: No flight data available</div>
{% endif %}
```

#### C. SAGA Demo Section (Only rendered if flight1 exists)
```html
<div class="saga-demo-section">
    <h5>🔧 SAGA Demo Controls</h5>
    <div class="form-check">
        <input class="form-check-input" type="checkbox" 
               name="simulate_reserveseat_fail" 
               id="simulateReserveSeatFail">
        <label>Simulate Seat Reservation Failure</label>
    </div>
    <!-- Other failure options... -->
</div>
```

**CRITICAL**: This entire section depends on `{% if flight1 %}` being true.
- If `flight1` not in context → section is hidden
- If checkboxes are hidden → user cannot select failures
- If checkboxes hidden but "Proceed to Payment" clicked → normal booking happens

---

### 4. **microservices/ui-service/static/js/book.js**
**Role**: Form submission logic and SAGA toggle handling

**Functions**:

#### `initSagaToggles()`
```javascript
function initSagaToggles() {
    const sagaSection = document.querySelector('.saga-demo-section');
    if (sagaSection) {
        // Found → enable SAGA checkboxes with mutual exclusivity
        const toggles = sagaSection.querySelectorAll('input[type="checkbox"]');
        toggles.forEach(toggle => {
            toggle.addEventListener('change', function() {
                if (this.checked) {
                    // Uncheck others
                    toggles.forEach(other => {
                        if (other !== this) {
                            other.checked = false;
                        }
                    });
                }
            });
        });
    } else {
        // NOT found → SAGA section hidden in HTML
        console.log("[DEBUG] SAGA section NOT found - no flight data");
    }
}
```

#### `book_submit()`
```javascript
function book_submit() {
    const sagaCheckboxes = document.querySelectorAll(
        '.saga-demo-section input[type="checkbox"]:checked'
    );
    
    if (sagaCheckboxes.length > 0) {
        // SAGA checkbox selected → set saga_demo_mode='true'
        document.querySelector('input[name="saga_demo_mode"]').value = 'true';
        return true;
    }
    
    // Normal booking
    return true;
}
```

---

### 5. **microservices/ui-service/ui/views.py → book() function**
**Role**: Process booking form submission

**Flow**:
```python
def book(request):
    if request.method == 'POST':
        saga_demo_mode = request.POST.get('saga_demo_mode') == 'true'
        
        if saga_demo_mode:
            # User checked SAGA failure box
            # Call SAGA API with failure simulation
            booking_result = call_backend_api(
                'api/saga/start-booking/', 
                'POST', 
                booking_data
            )
            # Redirect to SAGA results page
            return HttpResponseRedirect(reverse("saga_results") + f"?correlation_id={...}")
        else:
            # Normal booking
            booking_result = call_backend_api(
                'api/saga/start-booking/', 
                'POST', 
                booking_data
            )
            if booking_result.get('success'):
                # Get flight data and render payment page
                flight_data = call_backend_api(f'api/flights/{flight_id}/')
                return render(request, "flight/payment.html", payment_context)
```

---

### 6. **Backend Service Endpoints** (Microservices)

#### Required Endpoints:

**A. Get Flight Details**
```
GET /api/flights/{flight_id}/
Response: {
    "id": 1,
    "airline": "American Airlines",
    "flight_number": "AA100",
    "plane": "Boeing 777",
    "origin": {"id": 1, "city": "New York", "airport": "JFK"},
    "destination": {"id": 2, "city": "Los Angeles", "airport": "LAX"},
    "depart_time": "08:00:00",
    "arrival_time": "11:30:00",
    "duration": "05:30:00",
    "economy_fare": 500,
    "business_fare": 1500,
    "first_fare": 3000,
    ...
}
```

**B. Start SAGA Booking**
```
POST /api/saga/start-booking/
Request: {
    "flight_id": 1,
    "user_id": 1,
    "passengers": [
        {"first_name": "John", "last_name": "Doe", "gender": "male"}
    ],
    "contact_info": {...},
    "simulate_reserveseat_fail": false,
    "simulate_authorizepayment_fail": true,  // if SAGA demo checked
    ...
}
Response: {
    "success": true,
    "correlation_id": "abc-123-def-456",
    "steps_completed": [...],
    ...
}
```

---

## Debugging Checklist

### When "DEBUG: No flight1 data" appears:

1. **Check Review View Logs**:
   ```
   [DEBUG] SAGA TOGGLE - review() called with GET params: {'flight1Id': '1', ...}
   [DEBUG] SAGA TOGGLE - Fetching flight data for ID: 1
   [DEBUG] SAGA TOGGLE - ✓ Flight1 data loaded successfully: American Airlines
   ```
   - If you see `✗ ERROR: Failed to load flight data` → backend is down
   - If you see `✗ ERROR: No flight1_id provided` → search page didn't pass flight ID

2. **Check Backend Service**:
   ```bash
   curl http://localhost:8001/api/flights/1/
   ```
   - Should return flight JSON
   - If connection refused → backend not running
   - If 404 → flight doesn't exist in DB

3. **Check Network Tab** (Browser F12):
   - Click "Book Flight" in search results
   - Should see GET request to `/review/?flight1Id=1&...`
   - Should receive HTML response with flight data filled in

---

## Testing the Complete Flow

### Test Case 1: Normal Booking (No SAGA Demo)

```
1. Search for flights
2. Click "Book Flight"
   ✓ review() called
   ✓ flight1 data loaded
   ✓ book.html rendered WITH flight data
   
3. Add passenger
4. Click "Proceed to Payment" (NO SAGA checkbox selected)
   ✓ book() called with saga_demo_mode='false'
   ✓ SAGA booking API called
   ✓ Redirect to payment.html
   
5. Enter payment details
   ✓ Payment processed
   ✓ Booking confirmed
```

### Test Case 2: SAGA Demo (With Failure)

```
1. Search for flights
2. Click "Book Flight"
   ✓ review() called
   ✓ flight1 data loaded
   ✓ book.html rendered WITH flight data
   ✓ SAGA demo section VISIBLE
   
3. Add passenger
4. Check "Simulate Seat Reservation Failure"
5. Click "Proceed to Payment"
   ✓ book() called with saga_demo_mode='true'
   ✓ SAGA booking API called with failure simulation
   ✓ Redirect to /saga/results/?correlation_id=...
   
6. View SAGA result page
   ✓ Shows failed step
   ✓ Shows compensation timeline
   ✓ Shows rollback status
```

### Test Case 3: Backend Unavailable

```
1. Stop backend service
2. Search for flights (cached)
3. Click "Book Flight"
4. review() called with flight1Id
   ✗ call_backend_api() fails → returns None
   ✓ Error page rendered with message:
      "Failed to load flight details. Backend service is unreachable."
   
5. Check Terminal for:
   [DEBUG] Connection error: Connection refused
   [DEBUG] Failed after 3 attempts
```

---

## What Changed (Fixes Applied)

### File: `microservices/ui-service/ui/views.py`

**Function: `review()`** (Lines ~278-330)

**Changes**:
1. Added explicit check for `flight1_id` before API call
   - If missing → return error page immediately
   
2. Added error handling when `flight1_data` is None
   - Returns error page instead of silently rendering without data
   
3. Added detailed logging to distinguish between:
   - Missing flight ID (search page issue)
   - Backend unreachable (service issue)
   - Flight not found (data issue)

### File: `microservices/ui-service/templates/flight/book.html`

**Changes**:
1. Added error display section at top of form
   - Shows error message with context-specific help
   - Different messages for different error types
   
2. Enhanced "No flight1 data" message
   - Now shows as prominent error box (not just debug text)
   - Explains consequences (SAGA section won't work)

---

## Expected Behavior After Fix

### Scenario 1: Backend Running, Flight Selected
```
✓ Click "Book Flight" → review() → flight1 data loads
✓ book.html renders with flight details
✓ SAGA section VISIBLE
✓ Can check SAGA failure boxes
✓ Click "Proceed to Payment" → booking flow continues
```

### Scenario 2: Backend Down, Flight Selected
```
✓ Click "Book Flight" → review() → backend unavailable
✗ Error page shows: "Backend service is unreachable"
✗ No flight details shown
✗ SAGA section NOT visible
✗ Cannot proceed with booking
```

### Scenario 3: No Flight Selected
```
✓ Click "Book Flight" without flight param → review() called
✗ Error page shows: "Missing flight ID"
✗ No flight details shown
✗ SAGA section NOT visible
✗ Cannot proceed with booking
```

---

## Recommendations

1. **Always check backend logs** when booking fails
2. **Verify backend URL** in settings.py: `BACKEND_SERVICE_URL`
3. **Test API endpoints** directly with curl/Postman
4. **Monitor browser F12 Network tab** to see actual requests/responses
5. **Check correlation_id** in SAGA logs to track transaction flow

