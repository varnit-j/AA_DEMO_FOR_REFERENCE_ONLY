
# Flight Data Misalignment - Recommendations & Fixes

## Summary of Critical Issues

Based on comprehensive analysis of the "proceed to payment" flow, I've identified **2 critical issues** that are most likely causing flight data misalignment:

### 🔴 **CRITICAL ISSUE #1: Seat Class Parameter Loss**
**Location**: `ui/views.py:447`
**Problem**: Seat class selection is not properly preserved from booking form to payment processing.

### 🔴 **CRITICAL ISSUE #2: SAGA Data Hardcodes Economy Fare**
**Location**: `saga_views_complete.py:130`
**Problem**: SAGA booking data preparation always uses `economy_fare`, ignoring user's actual seat class selection.

## Immediate Fixes Required

### **Fix #1: Preserve Seat Class in Payment Flow**

**File**: `AA_Flight_booking/microservices/ui-service/ui/views.py`
**Line**: 447

```python
# CURRENT (PROBLEMATIC)
seat_class = request.POST.get('flight1Class', 'economy')

# RECOMMENDED FIX
seat_class = request.POST.get('flight1Class') or request.POST.get('seat_class')
if not seat_class:
    # Try to get from SAGA correlation data or default to economy
    seat_class = 'economy'
    print(f"[FLIGHT_DATA_DEBUG] ⚠️ WARNING: No seat class found, defaulting to economy")
else:
    print(f"[FLIGHT_DATA_DEBUG] ✓ Seat class preserved: {seat_class}")
```

### **Fix #2: Include Seat Class in SAGA Booking Data**

**File**: `AA_Flight_booking/microservices/backend-service/flight/saga_views_complete.py`
**Line**: 130-139

```python
# CURRENT (PROBLEMATIC)
booking_data = {
    'flight_id': flight_id,
    'user_id': data.get('user_id', 1),
    'passengers': passengers,
    'contact_info': contact_info,
    'flight_fare': float(flight.economy_fare),  # ❌ Always economy!
    'flight': {
        'id': flight.id,
        'flight_number': flight.flight_number,
        'economy_fare': float(flight.economy_fare),
        'origin': str(flight.origin),
        'destination': str(flight.destination)
    },
}

# RECOMMENDED FIX
seat_class = data.get('seat_class', 'economy')
if seat_class == 'business' and flight.business_fare:
    selected_fare = float(flight.business_fare)
elif seat_class == 'first' and flight.first_fare:
    selected_fare = float(flight.first_fare)
else:
    selected_fare = float(flight.economy_fare)
    seat_class = 'economy'  # Fallback if class not available

booking_data = {
    'flight_id': flight_id,
    'user_id': data.get('user_id', 1),
    'passengers': passengers,
    'contact_info': contact_info,
    'seat_class': seat_class,  # ✅ Add seat class
    'flight_fare': selected_fare,  # ✅ Use correct fare
    'flight': {
        'id': flight.id,
        'flight_number': flight.flight_number,
        'economy_fare': float(flight.economy_fare),
        'business_fare': float(flight.business_fare) if flight.business_fare else 0,
        'first_fare': float(flight.first_fare) if flight.first_fare else 0,
        'selected_fare': selected_fare,  # ✅ Add selected fare
        'seat_class': seat_class,  # ✅ Add seat class
        