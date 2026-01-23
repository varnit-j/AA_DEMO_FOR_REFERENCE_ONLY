
# SAGA Pattern Implementation Plan

## Current State Analysis

### ✅ Working Components
- **Services Running**: Backend (8001), UI (8000), Loyalty (8002), Payment (8003)
- **Basic SAGA endpoints**: Loyalty and Payment services have working SAGA endpoints
- **Event Dispatcher**: Created for in-process event handling
- **Compensation Logic**: Basic compensation endpoints implemented

### ❌ Issues Identified
1. **Backend SAGA URLs not loading** - Import failure in saga_views_complete
2. **No seat reservation system** - Need 162 seats per flight tracking
3. **Missing database models** - No Seat or SeatReservation models
4. **Incomplete SAGA orchestrator** - Missing proper seat booking logic
5. **No UI integration** - SAGA not integrated with existing booking flow

## Implementation Plan

### Phase 1: Database & Seat Management
1. **Add Seat Models** to `flight/models.py`:
   - `Seat` model (flight, seat_number, seat_class, is_available)
   - `SeatReservation` model (correlation_id, flight, seats, user, status, expires_at)

2. **Create Database Migration**:
   - Generate seats for existing flights (162 seats each)
   - Economy: 1A-27F (162 seats), Business: 1A-3F (18 seats), First: 1A-2F (12 seats)

3. **Add Seat Management Utilities**:
   - `create_flight_seats()` function
   - `reserve_seats()` function
   - `release_seats()` function

### Phase 2: Fix Backend SAGA Integration
4. **Fix SAGA Views Import Issues**:
   - Complete `saga_views_complete.py` with proper imports
   - Add seat reservation logic to `reserve_seat()` endpoint
   - Fix URL routing in `urls.py`

5. **Implement Proper SAGA Steps**:
   - **ReserveSeat**: Reserve actual seats in database
   - **AuthorizePayment**: Already working
   - **AwardMiles**: Already working  
   - **ConfirmBooking**: Create actual ticket with reserved seats

6. **Add Compensation Logic**:
   - **CancelSeat**: Release reserved seats
   - **CancelPayment**: Already working
   - **ReverseMiles**: Already working
   - **CancelBooking**: Cancel ticket and release seats

### Phase 3: Complete SAGA Flow
7. **Integrate with Existing Booking Flow**:
   - Modify `book_flight()` in `simple_views.py` to use SAGA
   - Add SAGA option to UI booking process
   - Maintain backward compatibility

8. **Add UI Integration**:
   - Add SAGA booking option to booking form
   - Show seat selection interface
   - Display SAGA status and progress

9. **Testing & Validation**:
   - Test complete SAGA flow with success scenarios
   - Test compensation flow with failure scenarios
   - Verify seat availability and reservation logic

## SAGA Flow Design

### Success Flow
```
1. User initiates booking → UI calls backend SAGA endpoint
2. ReserveSeat → Reserve 162 seats for flight in database
3. AuthorizePayment → Mock payment authorization
4. AwardMiles → Add loyalty points to user account
5. ConfirmBooking → Create final ticket with reserved seats
```

### Failure Flow (Example: Payment fails)
```
1. ReserveSeat → ✅ Seats reserved
2. AuthorizePayment → ❌ Payment fails
3. Compensation starts:
   - CancelSeat → Release reserved seats
   - SAGA marked as failed
```

## Database Schema Changes

### New Models
```python
class Seat(models.Model):
    flight = ForeignKey(Flight)
    seat_number = CharField(max_length=4)  # "12A"
    seat