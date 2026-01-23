#!/usr/bin/env python3.12
"""
Debug the actual UI form submission flow
Traces what data gets sent from book.html to book view
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
sys.path.insert(0, '/d/varnit/demo/2101/AA_Flight_booking/microservices/ui-service')
django.setup()

print("\n" + "="*80)
print("FLOW ANALYSIS: Book Form Submission")
print("="*80)

print("""
STEP 1: User is on review page (flight selected)
  - Route: /flight/review/?flight1Id=X&flight1Date=Y&seatClass=economy
  - review() view sets context['flight1'] with flight data
  - Renders flight/book.html with flight1 in context

STEP 2: book.html template has:
  - Hidden input: <input type="hidden" name="flight1" value="{{flight1.id}}">
  - Hidden input: <input type="hidden" name="flight1Class" value="{{seat}}">
  - Hidden input: <input type="hidden" id="p-count" name="passengersCount" value="0">

STEP 3: JavaScript (book.js) - add_traveller() function:
  - Creates hidden inputs for each passenger:
    <input type="hidden" name="passenger1FName" value="John">
    <input type="hidden" name="passenger1LName" value="Doe">
    <input type="hidden" name="passenger1Gender" value="male">
  - Updates #p-count value to number of passengers
  - Updates display of traveller count

STEP 4: User adds at least 1 passenger and clicks "Proceed to payment"
  - book_submit() is called
  - Checks if passengers were added: parseInt(pcount.value) > 0
  - If NO SAGA checkboxes checked: returns true (normal flow)
  - Form posts to /flight/book/ with method=POST

STEP 5: book() view receives POST
  - Extracts passengersCount from POST
  - Loops through passengers using passenger{i}FName naming
  - Builds booking_data dict
  - Calls backend SAGA API

THE ISSUE: What happens if flight1 is NOT in POST data?
  - book_submit() doesn't validate flight1 is present
  - book() view checks: flight1_id = request.POST.get('flight1')
  - If missing: returns error page
""")

print("\n" + "="*80)
print("POSSIBLE ISSUES")
print("="*80)

issues = [
    {
        'num': 1,
        'title': 'Flight data not passed from review to book form',
        'cause': 'review() not setting flight1 in context',
        'fix': 'Verify review() sets context["flight1"] before rendering',
        'impact': 'book.html shows "DEBUG: No flight1 data - SAGA toggles may not work"'
    },
    {
        'num': 2,
        'title': 'Form submission fails to include hidden fields',
        'cause': 'JavaScript error preventing hidden field creation',
        'fix': 'Check browser console for JS errors',
        'impact': 'Flight data lost when form submitted'
    },
    {
        'num': 3,
        'title': 'Passenger data not being collected',
        'cause': 'passengersCount stays 0 or passenger fields not created',
        'fix': 'Ensure add_traveller() creates hidden passenger fields',
        'impact': 'Booking fails with "No passengers" error'
    },
    {
        'num': 4,
        'title': 'Backend SAGA API call fails silently',
        'cause': 'call_backend_api() returning None on connection error',
        'fix': 'Add proper error handling in call_backend_api()',
        'impact': 'User sees booking failed but no clear error message'
    }
]

for issue in issues:
    print(f"\n[Issue {issue['num']}] {issue['title']}")
    print(f"  Cause: {issue['cause']}")
    print(f"  Fix: {issue['fix']}")
    print(f"  Impact: {issue['impact']}")

print("\n" + "="*80)
print("TO FIX: Need to check these in order")
print("="*80)

print("""
1. Is call_backend_api() working?
   - Check if it handles connection errors properly
   - Add timeout and retry logic
   
2. Are error messages being shown?
   - Check if book view is returning proper error context
   
3. Is passenger form working?
   - Check if add_traveller() is creating hidden fields correctly
   - Check if passengersCount is being updated
   
4. Is flight data being passed?
   - Check if review() is setting flight1 context
   - Check if book.html is receiving it
   - Check if hidden field is being created
""")
