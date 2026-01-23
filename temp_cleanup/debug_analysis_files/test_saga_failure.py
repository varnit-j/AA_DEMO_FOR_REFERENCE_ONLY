#!/usr/bin/env python
"""
Test SAGA with failure scenario
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
sys.path.insert(0, 'd:\\varnit\\demo\\2101\\AA_Flight_booking')

django.setup()

from flight.saga_orchestrator import BookingSAGAOrchestrator

print("\n" + "="*80)
print("TESTING SAGA WITH FAILURE SCENARIO")
print("="*80 + "\n")

# Test with payment failure
booking_data = {
    'flight_id': 123,
    'user_id': 1,
    'total_fare': 500.00,
    'loyalty_points_to_use': 1000,
    'payment_method': 'card',
    'passengers': [{'first_name': 'John', 'last_name': 'Test', 'gender': 'male'}]
}

# Simulate payment failure
failure_scenarios = {
    'reserve_seat': False,
    'deduct_loyalty_points': False,
    'process_payment': True,  # Fail at payment step
    'confirm_booking': False
}

orchestrator = BookingSAGAOrchestrator()
result = orchestrator.start_booking_saga(booking_data, failure_scenarios=failure_scenarios)

print("\n" + "="*80)
print("RESULT SUMMARY")
print("="*80)
print(f"Success: {result.get('success')}")
print(f"Failed Step: {result.get('failed_step')}")
print(f"Steps Completed: {result.get('steps_completed')}")
print(f"Compensation Results: {result.get('compensation_result', {}).get('successful_compensations')} successful")
print(f"Detailed Operations: {len(orchestrator.detailed_operations)} operations")
print(f"Compensation History: {len(orchestrator.compensation_history)} reversal steps")
print("="*80 + "\n")

# Show detailed operations
print("DETAILED OPERATIONS:")
for op in orchestrator.detailed_operations:
    print(f"  - {op['operation']}: {op['status']} - {op['details']}")

# Show compensation history
print("\nCOMPENSATION HISTORY:")
for comp in orchestrator.compensation_history:
    print(f"  - {comp['action']} {comp['step']}: {comp['status']}")

print("\n" + "="*80)
print("SUCCESS TEST")
print("="*80 + "\n")

# Test success scenario
orchestrator2 = BookingSAGAOrchestrator()
result2 = orchestrator2.start_booking_saga(booking_data, failure_scenarios={})

print(f"Success: {result2.get('success')}")
print(f"Booking Reference: {result2.get('booking_reference')}")
print(f"Steps Completed: {result2.get('steps_completed')}")

print("\n" + "="*80)
print("✓ TESTS COMPLETE")
print("="*80 + "\n")
