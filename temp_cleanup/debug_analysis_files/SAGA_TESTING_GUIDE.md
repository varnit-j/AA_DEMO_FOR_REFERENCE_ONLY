# SAGA Orchestrator - Quick Start & Testing Guide

## Quick Start

### 1. Access the SAGA Test Interface

```
http://localhost:8000/saga/test
```

### 2. Test Success Scenario

1. Go to `/saga/test`
2. Leave all failure checkboxes unchecked
3. Click **"✅ Test Success Scenario"**
4. View results showing all 4 steps completed

### 3. Test Failure Scenarios

#### Scenario A: Reserve Seat Fails (First Step)
1. Check "Fail at Reserve Seat"
2. Click **"❌ Test Selected Failure"**
3. View results showing:
   - Failed at: RESERVE_SEAT
   - Steps completed: 0
   - Compensations: 0 (no completed steps to compensate)

#### Scenario B: Deduct Points Fails (Second Step)
1. Uncheck all checkboxes
2. Check "Fail at Deduct Points"
3. Click **"❌ Test Selected Failure"**
4. View results showing:
   - Steps completed: 1 (RESERVE_SEAT)
   - Failed at: DEDUCT_LOYALTY_POINTS
   - Compensations executed: 1 (COMPENSATE_RESERVE_SEAT)

#### Scenario C: Payment Fails (Third Step)
1. Uncheck all checkboxes
2. Check "Fail at Process Payment"
3. Click **"❌ Test Selected Failure"**
4. View results showing:
   - Steps completed: 2
   - Failed at: PROCESS_PAYMENT
   - Compensations executed: 2 (in reverse order)

#### Scenario D: Confirm Booking Fails (Fourth Step)
1. Uncheck all checkboxes
2. Check "Fail at Confirm Booking"
3. Click **"❌ Test Selected Failure"**
4. View results showing:
   - Steps completed: 3
   - Failed at: CONFIRM_BOOKING
   - Compensations executed: 3 (all previous steps reversed)

## Expected Behaviors

### Success Scenario ✅

```
Status: SUCCESS

Booking Reference: ABC123DE

Steps Completed: 4 / 4

Results:
✅ RESERVE_SEAT - Seat reserved
✅ DEDUCT_LOYALTY_POINTS - 1000 points deducted
✅ PROCESS_PAYMENT - $500.00 charged
✅ CONFIRM_BOOKING - Booking confirmed

Duration: ~2-3 seconds
```

### Reserve Seat Failure ❌

```
Status: FAILED

Failed Step: RESERVE_SEAT

Error: Simulated failure for RESERVE_SEAT

Steps Completed: 0

Compensation:
  Total: 0 steps (nothing to compensate)

Reason: Step failed before any commits
```

### Deduct Points Failure ❌

```
Status: FAILED

Failed Step: DEDUCT_LOYALTY_POINTS

Error: Simulated failure for DEDUCT_LOYALTY_POINTS

Steps Completed: 1

Compensation Executed:
  ✅ COMPENSATE_RESERVE_SEAT - Seat reservation canceled

Reason: First step was successful, so it needs to be rolled back
```

### Payment Failure ❌

```
Status: FAILED

Failed Step: PROCESS_PAYMENT

Error: Simulated failure for PROCESS_PAYMENT

Steps Completed: 2

Compensation Executed:
  ✅ COMPENSATE_DEDUCT_LOYALTY_POINTS - Points refunded
  ✅ COMPENSATE_RESERVE_SEAT - Seat reservation canceled

Reason: Both previous steps succeeded, so they must be rolled back in reverse order
```

### Confirm Booking Failure ❌

```
Status: FAILED

Failed Step: CONFIRM_BOOKING

Error: Simulated failure for CONFIRM_BOOKING

Steps Completed: 3

Compensation Executed:
  ✅ COMPENSATE_PROCESS_PAYMENT - Payment refunded
  ✅ COMPENSATE_DEDUCT_LOYALTY_POINTS - Points refunded
  ✅ COMPENSATE_RESERVE_SEAT - Seat reservation canceled

Reason: All three steps succeeded, they must all be compensated in reverse order
```

## Key Testing Points

### 1. Sequential Execution
- Each test should show steps executing one after another
- Verify no parallel execution occurs
- Check timestamps in logs

### 2. Compensation Order
- Compensations always run in **reverse order** of execution
- Last executed step is compensated first
- All compensations should succeed

### 3. Memory Queue
- No external database calls during SAGA
- All state managed in memory
- Fast execution (< 5 seconds)

### 4. Logging
- Check `saga_orchestrator.log` for detailed logs
- Look for [SAGA QUEUE], [COMPENSATION], [SAGA STEP] markers
- Verify correlation IDs match

### 5. Error Messages
- Clear error descriptions for failed steps
- Specific failure reasons
- Compensation status clearly shown

## Log Analysis

### Log File Location
```
AA_Flight_booking/saga_orchestrator.log
```

### Key Log Entries to Look For

**SAGA Start:**
```
[SAGA] 🚀 Starting booking SAGA
[SAGA] Correlation ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
[SAGA] Failure scenarios: {various flags}
```

**Step Execution:**
```
[SAGA STEP] Executing: RESERVE_SEAT
[QUEUE] Executing step: RESERVE_SEAT (ID: step_0_1234567890)
[SAGA STEP] Processing RESERVE_SEAT...
[SAGA] ✅ Step RESERVE_SEAT completed successfully
```

**Failure:**
```
[SAGA] ❌ Step PROCESS_PAYMENT failed
Error: Simulated failure for PROCESS_PAYMENT
[QUEUE] Failed step: PROCESS_PAYMENT - Error: Simulated failure...
```

**Compensation:**
```
[SAGA COMPENSATION] 🔄 Starting compensation flow
[SAGA COMPENSATION] Total compensation steps: 2
[COMPENSATION] Executing: COMPENSATE_DEDUCT_LOYALTY_POINTS
[COMPENSATION] ✅ COMPENSATE_DEDUCT_LOYALTY_POINTS successful
```

## Debugging Tips

### 1. Missing Logs
- Check if logging is enabled in settings
- Verify log file path exists
- Check file permissions

### 2. Unexpected Step Order
- Review SAGA initialization in orchestrator
- Check queue add_step() calls in order
- Verify no step skipping

### 3. Compensation Not Executing
- Check queue.compensation_queue has items
- Verify compensation logic is implemented
- Review compensation response codes

### 4. Slow Execution
- Check individual step sleep times (0.5s, 0.3s)
- Review any external API calls
- Check database query performance

## Test Matrix

| Scenario | First Step | Second Step | Third Step | Fourth Step | Expected Compensations |
|----------|-----------|-----------|----------|-----------|----------------------|
| Success | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | None |
| Fail 1 | ❌ Fail | ⏭️ Skip | ⏭️ Skip | ⏭️ Skip | 0 |
| Fail 2 | ✅ Pass | ❌ Fail | ⏭️ Skip | ⏭️ Skip | 1 |
| Fail 3 | ✅ Pass | ✅ Pass | ❌ Fail | ⏭️ Skip | 2 |
| Fail 4 | ✅ Pass | ✅ Pass | ✅ Pass | ❌ Fail | 3 |

## Performance Benchmarks

Expected execution times:
- Success flow: 2-3 seconds
- Any failure scenario: 1-3 seconds
- Compensation per step: ~0.3 seconds

## Troubleshooting Test Issues

### Test Doesn't Start
1. Check Django is running: `python manage.py runserver`
2. Verify URL is correct: `http://localhost:8000/saga/test`
3. Check for URL routing errors in console

### No Results Displayed
1. Check browser console for JavaScript errors
2. Verify form submission is working
3. Check Django logs for view errors

### Steps Not Showing as Completed
1. Check if orchestrator is initialized
2. Verify queue is populated with steps
3. Look for exceptions in logs

### Compensation Not Working
1. Check compensation queue has items
2. Verify compensation step logic
3. Review error messages in compensation section

## Automation Testing

### Command Line Test
```bash
python manage.py shell
>>> from flight.saga_tests import run_saga_tests
>>> results = run_saga_tests()
>>> print(f"Passed: {results['passed']}/{results['total_tests']}")
```

### With Test Runner Script
```bash
python run_saga_tests.py
```

This will:
1. Run all 5 test scenarios
2. Generate test report
3. Save to `saga_test_report.json`
4. Print summary to console

## Continuous Testing

### In Your CI/CD Pipeline

Add to your test script:
```bash
python manage.py shell < run_saga_tests.py
```

### Expected CI Output
```
Total Tests: 5
Passed: 5 ✅
Failed: 0 ❌
Success Rate: 100.0%
```

## Next Steps

1. **Test all scenarios** - Use the quick start above
2. **Review logs** - Check saga_orchestrator.log for details
3. **Check compensation** - Verify rollback works correctly
4. **Integrate booking** - Connect SAGA to actual booking flow
5. **Monitor production** - Set up alerts for SAGA failures

## Support & Documentation

- **Full Guide**: `SAGA_ORCHESTRATOR_GUIDE.md`
- **Logs**: Check `saga_orchestrator.log` and `saga_bookings.log`
- **Test Report**: View `saga_test_report.json` after running tests
- **Source Code**: Review `flight/saga_orchestrator.py`
