# SAGA Orchestrator Implementation Guide

## Overview

This document describes the complete implementation of the SAGA pattern for flight booking system. The SAGA pattern is a distributed transaction pattern used to maintain data consistency across microservices.

## What is SAGA?

SAGA is a distributed transaction pattern that manages data consistency across microservices. Instead of using traditional ACID transactions:

1. **Each service performs a local transaction** - Each booking step (reserve seat, deduct points, process payment, confirm booking) is a separate operation
2. **Sequential execution** - Steps execute one after another in a defined order
3. **Compensating transactions** - If any step fails, all previous steps are reversed (compensated)
4. **No distributed locks** - Transactions are loosely coupled and don't lock resources

## Architecture

### Components

#### 1. **BookingSAGAOrchestrator** (`flight/saga_orchestrator.py`)
Main orchestrator managing the complete booking flow:
- Maintains a memory queue of pending steps
- Executes steps sequentially
- Tracks completion and failures
- Triggers compensation on failure

#### 2. **SAGAMemoryQueue** (`flight/saga_orchestrator.py`)
In-memory queue for step management:
- Manages pending, executing, completed, and failed steps
- Maintains compensation queue for rollback
- Provides status tracking

#### 3. **SAGAStep** (`flight/saga_orchestrator.py`)
Represents a single SAGA step with:
- Step ID and name
- Status (PENDING, EXECUTING, COMPLETED, FAILED, COMPENSATING, COMPENSATED)
- Result and error information
- Timestamps for tracking

#### 4. **BookingSAGAService** (`flight/saga_service.py`)
Django integration service:
- Creates SAGA instances
- Provides high-level booking API
- Integrates with Django models

## Booking SAGA Flow

### The 4 Steps

```
Step 1: RESERVE_SEAT
├─ Description: Reserve seat for passenger
├─ Success: Returns seat ID
└─ Failure: Compensation cancels seat

Step 2: DEDUCT_LOYALTY_POINTS
├─ Description: Deduct loyalty points for discount
├─ Success: Returns points deducted and discount applied
└─ Failure: Compensation refunds points

Step 3: PROCESS_PAYMENT
├─ Description: Process payment
├─ Success: Returns transaction ID
└─ Failure: Compensation refunds payment

Step 4: CONFIRM_BOOKING
├─ Description: Confirm and issue booking
├─ Success: Returns booking confirmation
└─ Failure: Compensation cancels booking
```

### Success Flow

```
START
  ↓
RESERVE_SEAT (Success)
  ↓
DEDUCT_LOYALTY_POINTS (Success)
  ↓
PROCESS_PAYMENT (Success)
  ↓
CONFIRM_BOOKING (Success)
  ↓
END - Booking Confirmed ✅
```

### Failure Flow (Example: Payment Fails)

```
START
  ↓
RESERVE_SEAT (Success) ✅
  ↓
DEDUCT_LOYALTY_POINTS (Success) ✅
  ↓
PROCESS_PAYMENT (FAILED) ❌
  ↓
COMPENSATION TRIGGERED
  ↓
COMPENSATE_DEDUCT_LOYALTY_POINTS ✅
  ↓
COMPENSATE_RESERVE_SEAT ✅
  ↓
END - Booking Failed, All Changes Reversed ❌
```

## Usage

### 1. Django Web Interface

Access the SAGA test interface at: `/saga/test`

**Features:**
- Select which step to fail (or test success)
- Visual representation of SAGA steps
- Real-time status updates
- Comprehensive logging
- Compensation tracking

### 2. Programmatic Usage

```python
from flight.saga_orchestrator import BookingSAGAOrchestrator

# Create orchestrator
orchestrator = BookingSAGAOrchestrator()

# Prepare booking data
booking_data = {
    'flight_id': 123,
    'user_id': 1,
    'total_fare': 500.00,
    'loyalty_points_to_use': 1000,
    'payment_method': 'card',
    'passengers': [...]
}

# Test success scenario
result = orchestrator.start_booking_saga(booking_data, failure_scenarios={})

# Test failure at payment step
failure_scenarios = {
    'reserve_seat': False,
    'deduct_loyalty_points': False,
    'process_payment': True,  # This step will fail
    'confirm_booking': False
}
result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)

# Check result
if result.get('success'):
    print(f"Booking confirmed: {result.get('booking_reference')}")
else:
    print(f"Failed at: {result.get('failed_step')}")
    print(f"Compensations executed: {result.get('compensation_result')}")
```

### 3. Service Layer Usage

```python
from flight.saga_service import booking_saga_service
from django.contrib.auth.models import User

user = User.objects.get(id=1)

result = booking_saga_service.create_booking_saga(
    user=user,
    flight_ids=[123],
    flight_dates=['2024-01-20'],
    passenger_data=[{'first_name': 'John', 'last_name': 'Doe', 'gender': 'male'}],
    seat_class='Economy',
    total_fare=500.00,
    loyalty_points_to_use=1000,
    payment_method='card'
)
```

## Testing

### Run All Tests

```bash
python manage.py shell
>>> from flight.saga_tests import run_saga_tests
>>> results = run_saga_tests()
```

Or use the test runner script:

```bash
python run_saga_tests.py
```

### Test Scenarios

#### Test 1: Success Scenario
- All 4 steps complete successfully
- Booking confirmed
- Booking reference generated

#### Test 2: Reserve Seat Failure
- RESERVE_SEAT step fails
- No steps executed after
- No compensation needed (no completed steps to rollback)

#### Test 3: Deduct Points Failure
- RESERVE_SEAT succeeds
- DEDUCT_LOYALTY_POINTS fails
- Compensation executed for RESERVE_SEAT

#### Test 4: Payment Failure
- RESERVE_SEAT succeeds
- DEDUCT_LOYALTY_POINTS succeeds
- PROCESS_PAYMENT fails
- Compensation executed for both previous steps (in reverse order)

#### Test 5: Confirm Booking Failure
- All first 3 steps succeed
- CONFIRM_BOOKING fails
- Compensation executed for all 3 previous steps (in reverse order)

## Logging

### Log Files

- **saga_orchestrator.log** - Main orchestrator log with all events
- **saga_bookings.log** - Individual booking SAGA logs (JSON format)
- **saga_test_report.json** - Test execution report

### Log Levels

- `DEBUG` - Detailed queue operations
- `INFO` - Step execution and major events
- `WARNING` - Simulated failures
- `ERROR` - Actual failures and exceptions

### Log Format

```
2024-01-20 10:30:45,123 - [flight.saga_orchestrator] - INFO - [SAGA] Starting booking SAGA
2024-01-20 10:30:45,234 - [flight.saga_orchestrator] - INFO - [QUEUE] Executing step: RESERVE_SEAT
2024-01-20 10:30:45,789 - [flight.saga_orchestrator] - INFO - [SAGA] ✅ Step RESERVE_SEAT completed successfully
```

## Key Features

### 1. **Sequential Execution**
Steps are executed one after another, not in parallel. This ensures data consistency.

### 2. **Automatic Compensation**
When a step fails, all previously completed steps are automatically compensated (rolled back).

### 3. **Memory Queue**
All step management is done in memory with proper state tracking.

### 4. **Comprehensive Logging**
Every operation is logged with timestamps and details for debugging.

### 5. **Correlation ID**
Each SAGA execution has a unique correlation ID for tracking across logs.

### 6. **Status Tracking**
Real-time status updates for:
- Pending steps
- Currently executing step
- Completed steps
- Failed steps
- Pending compensations

### 7. **Failure Scenarios**
For testing, any step can be marked to fail artificially.

## Data Flow

### Request Data

```json
{
  "flight_id": 123,
  "user_id": 1,
  "total_fare": 500.00,
  "loyalty_points_to_use": 1000,
  "payment_method": "card",
  "passengers": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "gender": "male"
    }
  ]
}
```

### Success Response

```json
{
  "success": true,
  "correlation_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "booking_reference": "A1B2C3D4",
  "steps_completed": 4,
  "total_steps": 4,
  "saga_log": [...]
}
```

### Failure Response

```json
{
  "success": false,
  "correlation_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "failed_step": "PROCESS_PAYMENT",
  "error": "Payment authorization failed",
  "steps_completed": 2,
  "compensation_result": {
    "total_compensations": 2,
    "successful_compensations": 2,
    "results": [
      {
        "step": "COMPENSATE_DEDUCT_LOYALTY_POINTS",
        "success": true
      },
      {
        "step": "COMPENSATE_RESERVE_SEAT",
        "success": true
      }
    ]
  },
  "saga_log": [...]
}
```

## Performance

- **Sequential execution** ensures data consistency but may take longer
- **In-memory queue** provides fast state management
- **No external dependencies** for basic SAGA flow
- **Typical execution time**: ~2-3 seconds for full flow

## Error Handling

### At Step Level
- Each step catches exceptions
- Returns error message
- Triggers compensation immediately

### At Queue Level
- Validates step data
- Manages pending/executing/completed states
- Ensures compensation order (reverse of execution)

### At Orchestrator Level
- Wraps everything in try-catch
- Logs all errors
- Provides correlation ID for tracking
- Returns detailed error response

## Extension Points

### Adding New Steps

1. Define step in `start_booking_saga()`:
```python
("NEW_STEP", {
    "description": "...",
    "endpoint": "/api/saga/new-step/",
    "compensation_endpoint": "/api/saga/undo-new-step/"
})
```

2. Implement logic in `_execute_step_logic()`:
```python
elif step_name == "NEW_STEP":
    return {
        'success': True,
        'step': 'NEW_STEP',
        'data': {...}
    }
```

3. Implement compensation in `_execute_compensation_step()`:
```python
elif "NEW_STEP" in step_name:
    return {
        'success': True,
        'step': comp_name,
        'message': 'New step compensation done'
    }
```

### Customizing Compensation Logic

Override `_execute_compensation_step()` to customize compensation behavior.

## UI Components

### SAGA Test Page (`/saga/test`)

Features:
- **4 Checkboxes** for selecting which step to fail
- **Success/Failure Buttons** for running tests
- **Real-time Status** showing current execution
- **Results Section** with detailed logs
- **Compensation Tracking** showing rollback steps
- **Correlation ID** for tracking

## Best Practices

1. **Use correlation IDs** for debugging
2. **Log all operations** for audit trails
3. **Test failure scenarios** regularly
4. **Monitor compensation execution** for issues
5. **Use appropriate timeout values** for external calls
6. **Implement idempotency** for compensation steps
7. **Track compensation success rate** in monitoring

## Troubleshooting

### Issue: Steps not executing
- Check saga_orchestrator.log for errors
- Verify booking_data is properly formatted
- Check for exceptions in step logic

### Issue: Compensation not executing
- Verify compensation_queue has steps
- Check compensation endpoint is available
- Review compensation_result in response

### Issue: Slow execution
- Check network/database latency
- Review step implementation for bottlenecks
- Consider async compensation in future versions

### Issue: Lost data
- Always check saga_log for audit trail
- Verify compensation completed successfully
- Check database transaction logs

## Future Enhancements

1. **Async compensation** - Non-blocking compensation
2. **Retry logic** - Automatic retry for failed steps
3. **Timeout handling** - Configurable timeouts per step
4. **Dead letter queue** - For permanently failed compensations
5. **Metrics/monitoring** - Integration with monitoring systems
6. **Database persistence** - Store SAGA state in database
7. **Distributed execution** - Execute steps across multiple services
8. **Event sourcing** - Complete event audit trail

## References

- https://microservices.io/patterns/data/saga.html
- SAGA Pattern (Choreography vs Orchestration)
- Distributed Transactions
- Compensation Pattern

## Support

For issues or questions, check:
1. saga_orchestrator.log for detailed logs
2. SAGA Test page at `/saga/test` for testing
3. This documentation for usage patterns
