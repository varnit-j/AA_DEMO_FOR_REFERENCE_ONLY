
# Flight Data Misalignment Analysis - "Proceed to Payment" Flow

## Executive Summary

After comprehensive analysis of the payment flow when clicking "proceed to payment", I've identified several potential sources of flight data misalignment and added targeted logging to validate assumptions. The analysis reveals critical points where flight data could become inconsistent between booking initiation and payment processing.

## Code Flow Analysis

### 1. **Payment Flow Entry Points**

When user clicks "proceed to payment", the following code path is executed:

1. **UI Service** (`ui/views.py:payment()` - Line 506)
   - URL: `/flight/ticket/payment` 
   - Method: POST
   - Parameters required: `ticket`, `final_fare`, payment details

2. **Backend SAGA Orchestrator** (`saga_orchestrator_fixed.py`)
   - Coordinates 4 steps: ReserveSeat → AuthorizePayment → AwardMiles → ConfirmBooking
   - Each step receives `booking_data` with flight information

3. **Payment Service** (`payment/saga_views.py:authorize_payment()`)
   - Processes payment authorization with flight fare data
   - URL: `http://localhost:8003/api/saga/authorize-payment/`

## Identified Sources of Flight Data Misalignment

### **PRIMARY ISSUES (Most Likely)**

#### 1. **Flight Data Retrieval Inconsistency** 🔴 CRITICAL
**Location**: `ui/views.py:436-443`
```python
# Get flight data from the original booking data since SAGA doesn't return flight details
flight_id = booking_data.get('flight_id')
flight_data = call_backend_api(f'api/flights/{flight_id}/')
```

**Problem**: The UI service fetches flight data separately for payment context, but this might not match the original booking data if:
- Flight prices have changed between booking and payment
- Database has been updated
- Different seat class is retrieved than originally selected

#### 2. **Seat Class Parameter Loss** 🔴 CRITICAL
**Location**: `ui/views.py:447-456`
```python
seat_class = request.POST.get('flight1Class', 'economy')  # Defaults to economy!

# Calculate fare based on seat class
if seat_class == 'first':
    fare = flight_data.get('first_fare', 0)
elif seat_class == 'business':
    fare = flight_data.get('business_fare', 0)
else:
    fare = flight_data.get('economy_fare', 0)  # Default fallback
```

**Problem**: The seat class selection from booking form might not be properly preserved, causing wrong fare calculation.

### **SECONDARY ISSUES (Possible)**

#### 3. **SAGA Data Transformation** 🟡 MEDIUM
**Location**: `saga_views_complete.py:121-139`
```python
booking_data = {
    'flight_id': flight_id,
    'flight_fare': float(flight.economy_fare),  # Always uses economy_fare!
    'flight': {
        'economy_fare': float(flight.economy_fare),
        # Missing business_fare and first_fare
    }
}
```

**Problem**: SAGA booking data preparation hardcodes `economy_fare`, ignoring user's seat class selection.

#### 4. **Payment Service Fallback Logic** 🟡 MEDIUM
**Location**: `payment/saga_views.py:38-43`
```python
flight_fare = booking_data.get('flight_fare', 0)
if not flight_fare:
    flight_data = booking_data.get('flight', {})
    flight_fare = flight_data.get('economy_fare', 500)  # Default fare
```

**Problem**: Payment service falls back to economy fare or arbitrary $500 if flight_fare is missing.

#### 5. **Session/Context Loss** 🟡 MEDIUM
**Location**: Multiple locations
**Problem**: User session data