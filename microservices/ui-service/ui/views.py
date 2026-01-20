
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
import json
import requests
from django.conf import settings
from datetime import datetime
import math
import re
from decimal import Decimal
from . import loyalty_tracker

# Fee and Surcharge variable
FEE = 50.0

# Helper function to make API calls to backend service
def call_backend_api(endpoint, method='GET', data=None):
    """Make API calls to the backend service"""
    try:
        backend_url = settings.BACKEND_SERVICE_URL
        url = f"{backend_url}/{endpoint}"
        
        print(f"[DEBUG] Making {method} request to: {url}")
        if data:
            print(f"[DEBUG] Request data: {data}")
        
        if method == 'GET':
            response = requests.get(url, params=data)
        elif method == 'POST':
            response = requests.post(url, json=data)
        
        print(f"[DEBUG] Response status: {response.status_code}")
        if response.status_code in [200, 201]:  # Handle both 200 OK and 201 Created
            result = response.json()
            print(f"[DEBUG] Success response: {result}")
            return result
        else:
            print(f"[DEBUG] Error response: {response.text}")
            return None
    except Exception as e:
        print(f"[DEBUG] API call error: {e}")
        return None

def index(request):
    """Home page with flight search functionality"""
    min_date = f"{datetime.now().date().year}-{datetime.now().date().month}-{datetime.now().date().day}"
    max_date = f"{datetime.now().date().year if (datetime.now().date().month+3)<=12 else datetime.now().date().year+1}-{(datetime.now().date().month + 3) if (datetime.now().date().month+3)<=12 else (datetime.now().date().month+3-12)}-{datetime.now().date().day}"
    
    if request.method == 'POST':
        origin = request.POST.get('Origin')
        destination = request.POST.get('Destination')
        depart_date = request.POST.get('DepartDate')
        seat = request.POST.get('SeatClass')
        trip_type = request.POST.get('TripType')
        
        if trip_type == '1':
            return render(request, 'flight/index.html', {
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type
            })
        elif trip_type == '2':
            return_date = request.POST.get('ReturnDate')
            return render(request, 'flight/index.html', {
                'min_date': min_date,
                'max_date': max_date,
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type,
                'return_date': return_date
            })
    else:
        return render(request, 'flight/index.html', {
            'min_date': min_date,
            'max_date': max_date
        })

def login_view(request):
    """Login page"""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "flight/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "flight/login.html")

def register_view(request):
    """Registration page"""
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        if password != confirmation:
            return render(request, "flight/register.html", {
                "message": "Passwords must match."
            })
        
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        except:
            return render(request, "flight/register.html", {
                "message": "Username already taken."
            })
    else:
        return render(request, "flight/register.html")

def logout_view(request):
    """Logout view"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def query(request, q):
    """Query places via backend API"""
    places_data = call_backend_api('api/places/search/', 'GET', {'q': q})
    if places_data:
        return JsonResponse(places_data, safe=False)
    else:
        return JsonResponse([], safe=False)

@csrf_exempt
def flight(request):
    """Search flights via backend API"""
    search_params = {
        'origin': request.GET.get('Origin'),
        'destination': request.GET.get('Destination'),
        'trip_type': request.GET.get('TripType'),
        'depart_date': request.GET.get('DepartDate'),
        'seat_class': request.GET.get('SeatClass')
    }
    
    if search_params['trip_type'] == '2':
        search_params['return_date'] = request.GET.get('ReturnDate')
    
    # Call backend API for flight search
    flight_data = call_backend_api('api/flights/search/', 'GET', search_params)
    
    if flight_data:
        print(f"[DEBUG] Raw flight_data from API: {flight_data}")
        
        # Extract flights list from API response
        flights = flight_data.get('flights', [])
        print(f"[DEBUG] Number of flights: {len(flights)}")
        
        # Convert time strings to proper format for template display
        for flight in flights:
            # Convert time strings like "08:09:00" to "08:09" for display
            if 'depart_time' in flight and flight['depart_time']:
                flight['depart_time_display'] = flight['depart_time'][:5]  # "08:09:00" -> "08:09"
            if 'arrival_time' in flight and flight['arrival_time']:
                flight['arrival_time_display'] = flight['arrival_time'][:5]  # "10:42:00" -> "10:42"
        
        if flights:
            print(f"[DEBUG] First flight data: {flights[0]}")
            print(f"[DEBUG] First flight fare fields: economy_fare={flights[0].get('economy_fare')}, business_fare={flights[0].get('business_fare')}, first_fare={flights[0].get('first_fare')}")
            print(f"[DEBUG] First flight time fields: depart_time_display={flights[0].get('depart_time_display')}, arrival_time_display={flights[0].get('arrival_time_display')}")
        
        # Prepare context for template
        context = {
            'flights': flights,
            'origin': flight_data.get('origin'),
            'destination': flight_data.get('destination'),
            'depart_date': search_params.get('depart_date'),
            'seat': search_params.get('seat_class'),  # Map seat_class to seat
            'trip_type': search_params.get('trip_type'),
        }
        
        # Calculate min/max prices for filters
        if flights:
            seat_class = search_params.get('seat_class', 'economy')
            fare_field = f"{seat_class}_fare"
            fares = [flight.get(fare_field, 0) for flight in flights if flight.get(fare_field)]
            if fares:
                context['min_price'] = min(fares)
                context['max_price'] = max(fares)
                print(f"[DEBUG] Price range for {seat_class}: {context['min_price']} - {context['max_price']}")
        
        print(f"[DEBUG] Final context keys: {list(context.keys())}")
        return render(request, "flight/search.html", context)
    else:
        return render(request, "flight/search.html", {
            'flights': [],
            'error': 'No flights found or service unavailable'
        })

def review(request):
    """Flight review page with actual flight data"""
    if request.user.is_authenticated:
        # Get flight data from request parameters
        flight1_id = request.GET.get('flight1Id')
        flight1_date = request.GET.get('flight1Date')
        flight2_id = request.GET.get('flight2Id')
        flight2_date = request.GET.get('flight2Date')
        seat_class = request.GET.get('seatClass', 'economy')
        
        context = {
            'fee': FEE,
            'seat': seat_class,
        }
        
        # Get flight1 data from backend
        if flight1_id:
            flight1_data = call_backend_api(f'api/flights/{flight1_id}/')
            if flight1_data:
                context['flight1'] = flight1_data
                context['flight1ddate'] = flight1_date
                context['flight1adate'] = flight1_date  # Simplified for now
        
        # Get flight2 data from backend if round trip
        if flight2_id:
            flight2_data = call_backend_api(f'api/flights/{flight2_id}/')
            if flight2_data:
                context['flight2'] = flight2_data
                context['flight2ddate'] = flight2_date
                context['flight2adate'] = flight2_date  # Simplified for now
        
        return render(request, "flight/book.html", context)
    else:
        return HttpResponseRedirect(reverse("login"))

def book(request):
    """Flight booking with backend integration"""
    print(f"[DEBUG] book() view called - Method: {request.method}, User: {request.user}")
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
            print(f"[DEBUG] Full POST data: {dict(request.POST)}")
            
            # Check if required flight data is present
            flight1_id = request.POST.get('flight1')
            if not flight1_id:
                print(f"[DEBUG] ERROR: Missing flight1 ID in POST data")
                return render(request, "flight/book.html", {
                    'error': 'Missing flight information. Please select a flight again.',
                })
            
            # Extract booking data from form
            booking_data = {
                'flight_id': request.POST.get('flight1'),
                'user_id': request.user.id,  # Add user_id to booking data
                'passengers': [],
                'contact_info': {
                    'mobile': request.POST.get('mobile'),
                    'email': request.POST.get('email'),
                    'country_code': request.POST.get('countryCode')
                }
            }
            
            # Extract passenger data using the correct JavaScript naming convention
            passengers_count = int(request.POST.get('passengersCount', 0))
            print(f"[DEBUG] Passengers count: {passengers_count}")
            
            for i in range(passengers_count):
                # Use the JavaScript naming convention: passenger1FName, passenger2FName, etc.
                passenger = {
                    'first_name': request.POST.get(f'passenger{i+1}FName'),
                    'last_name': request.POST.get(f'passenger{i+1}LName'),
                    'gender': request.POST.get(f'passenger{i+1}Gender')
                }
                
                print(f"[DEBUG] Passenger {i+1}: {passenger}")
                booking_data['passengers'].append(passenger)
            
            print(f"[DEBUG] Final booking data: {booking_data}")
            
            # Validate booking data before API call
            if not booking_data['passengers']:
                print(f"[DEBUG] ERROR: No passengers in booking data")
                return render(request, "flight/book.html", {
                    'error': 'No passengers added. Please add at least one passenger.',
                })
            
            # Call SAGA booking API instead of traditional booking
            print(f"[DEBUG] Calling SAGA booking API...")
            booking_result = call_backend_api('api/saga/start-booking/', 'POST', booking_data)
            print(f"[DEBUG] SAGA Booking API result: {booking_result}")
            
            if booking_result and booking_result.get('success'):
                print(f"[DEBUG] SAGA Booking successful, proceeding to payment")
                print(f"[DEBUG] SAGA Correlation ID: {booking_result.get('correlation_id')}")
                print(f"[DEBUG] SAGA Steps completed: {booking_result.get('steps_completed')}")
                
                # Get flight data from the original booking data since SAGA doesn't return flight details
                flight_id = booking_data.get('flight_id')
                flight_data = call_backend_api(f'api/flights/{flight_id}/')
                
                if not flight_data:
                    print(f"[DEBUG] ERROR: Could not retrieve flight data for flight {flight_id}")
                    return render(request, "flight/book.html", {
                        'error': 'Could not retrieve flight information. Please try again.',
                        'booking_data': booking_data
                    })
                seat_class = request.POST.get('flight1Class', 'economy')
                
                # Calculate fare based on seat class
                if seat_class == 'first':
                    fare = flight_data.get('first_fare', 0)
                elif seat_class == 'business':
                    fare = flight_data.get('business_fare', 0)
                else:
                    fare = flight_data.get('economy_fare', 0)
                
                # Add fee
                total_fare = fare + FEE
                
                # Get user's loyalty points from local tracker
                user_loyalty = loyalty_tracker.get_user_points(request.user.id)
                user_points = user_loyalty.get('points_balance', 0)
                points_value = user_points * 0.01  # 1 point = $0.01
                print(f"[DEBUG] Retrieved {user_points} points (${points_value:.2f} value) from local tracker")
                
                # Prepare payment context with SAGA correlation ID
                correlation_id = booking_result.get('correlation_id')
                payment_context = {
                    'booking_reference': correlation_id,
                    'flight': flight_data,
                    'fare': total_fare,
                    'ticket': correlation_id,  # Use SAGA correlation ID as ticket ID
                    'fee': FEE,
                    'seat': seat_class,
                    'user_points': user_points,
                    'points_value': points_value,
                    'message': 'SAGA Booking successful! All services coordinated. Proceed to payment.',
                    'saga_correlation_id': correlation_id
                }
                
                print(f"[DEBUG] Payment context: {payment_context}")
                print(f"[DEBUG] Points debugging - user_points: {user_points}, points_value: {points_value}")
                print(f"[DEBUG] Currency debugging - total_fare: {total_fare}, flight_data: {flight_data}")
                return render(request, "flight/payment.html", payment_context)
            else:
                print(f"[DEBUG] SAGA Booking failed - API returned: {booking_result}")
                error_msg = 'SAGA Booking failed. Please try again.'
                if booking_result and 'error' in booking_result:
                    error_msg = f"SAGA Booking failed: {booking_result['error']}"
                    if 'failed_step' in booking_result:
                        error_msg += f" (Failed at: {booking_result['failed_step']})"
                    if 'compensation_result' in booking_result:
                        comp_result = booking_result['compensation_result']
                        error_msg += f" (Compensations executed: {comp_result.get('total_compensations', 0)})"
                return render(request, "flight/book.html", {
                    'error': error_msg,
                    'booking_data': booking_data,
                    'saga_error': True
                })
        else:
            # GET request - show booking form
            return render(request, "flight/book.html")
    else:
        return HttpResponseRedirect(reverse("login"))

def payment(request):
    """Payment processing with proper POST handling"""
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(f"[DEBUG] Payment POST data: {dict(request.POST)}")
            
            # Extract payment data
            payment_data = {
                'ticket': request.POST.get('ticket'),
                'fare': request.POST.get('final_fare'),
                'card_number': request.POST.get('cardNumber'),
                'card_holder_name': request.POST.get('cardHolderName'),
                'expiry_month': request.POST.get('expMonth'),
                'expiry_year': request.POST.get('expYear'),
                'cvv': request.POST.get('cvv'),
                'payment_method': request.POST.get('payment_method', 'card'),
                'points_to_use': request.POST.get('points_to_use', 0)
            }
            
            print(f"[DEBUG] Payment data extracted: {payment_data}")
            print(f"[DEBUG] Raw points_to_use value: '{payment_data.get('points_to_use')}' (type: {type(payment_data.get('points_to_use'))})")
            
            # Determine ticket status based on payment method
            ticket_ref = payment_data.get('ticket')
            payment_method = payment_data.get('payment_method', 'card')
            
            # Handle points redemption with local tracker
            points_to_use_raw = payment_data.get('points_to_use', 0)
            if points_to_use_raw == '' or points_to_use_raw is None:
                points_to_use = 0
            else:
                try:
                    points_to_use = int(points_to_use_raw)
                except (ValueError, TypeError):
                    print(f"[DEBUG] Invalid points_to_use value: '{points_to_use_raw}', defaulting to 0")
                    points_to_use = 0
            
            if points_to_use > 0:
                points_value = points_to_use * 0.01
                print(f"[DEBUG] POINTS REDEMPTION - User wants to redeem {points_to_use} points (${points_value:.2f} value)")
                
                # Call loyalty service to redeem points
                try:
                    loyalty_url = settings.LOYALTY_SERVICE_URL
                    redeem_url = f"{loyalty_url}/api/loyalty/points/redeem/"
                    
                    redeem_data = {
                        'user_id': request.user.id,
                        'points_to_redeem': points_to_use,
                        'transaction_id': f"PAYMENT_{ticket_ref}"
                    }
                    
                    print(f"[DEBUG] POINTS REDEMPTION - Calling loyalty service URL: {redeem_url}")
                    print(f"[DEBUG] POINTS REDEMPTION - Redemption data: {redeem_data}")
                    redeem_response = requests.post(redeem_url, json=redeem_data)
                    
                    print(f"[DEBUG] POINTS REDEMPTION - Response status: {redeem_response.status_code}")
                    print(f"[DEBUG] POINTS REDEMPTION - Response text: {redeem_response.text}")
                    
                    if redeem_response.status_code == 200:
                        redeem_result = redeem_response.json()
                        print(f"[DEBUG] POINTS REDEMPTION - SUCCESS: {redeem_result}")
                        print(f"[DEBUG] POINTS REDEMPTION - Transaction should now appear in history")
                    else:
                        print(f"[ERROR] POINTS REDEMPTION - FAILED: {redeem_response.status_code} - {redeem_response.text}")
                        
                except Exception as e:
                    print(f"[ERROR] POINTS REDEMPTION - Exception occurred: {e}")
            else:
                print(f"[DEBUG] No points redemption requested")
            
            # For now, simulate successful payment processing
            # In a real implementation, this would call a payment service
            
            # Note: Loyalty points are now handled by the SAGA orchestration in the backend service
            # The SAGA pattern ensures proper transaction consistency across all services
            print(f"[DEBUG] Loyalty points will be awarded via SAGA orchestration")
            
            # Update ticket status based on payment method
            try:
                if payment_method == 'counter':
                    # For counter payments, set status to 'on_hold'
                    print(f"[DEBUG] BOOKING DISPLAY FIX - Setting ticket {ticket_ref} status to 'on_hold' for counter payment")
                    status_update_result = call_backend_api(f'api/tickets/{ticket_ref}/update_status/', 'POST', {
                        'status': 'on_hold'
                    })
                    if status_update_result and status_update_result.get('success'):
                        print(f"[DEBUG] BOOKING DISPLAY FIX - Successfully updated ticket status to 'on_hold'")
                    else:
                        print(f"[DEBUG] BOOKING DISPLAY FIX - Failed to update ticket status: {status_update_result}")
                else:
                    # For card payments, set status to 'confirmed'
                    print(f"[DEBUG] BOOKING DISPLAY FIX - Setting ticket {ticket_ref} status to 'confirmed' for card payment")
                    status_update_result = call_backend_api(f'api/tickets/{ticket_ref}/update_status/', 'POST', {
                        'status': 'confirmed'
                    })
                    if status_update_result and status_update_result.get('success'):
                        print(f"[DEBUG] BOOKING DISPLAY FIX - Successfully updated ticket status to 'confirmed'")
                    else:
                        print(f"[DEBUG] BOOKING DISPLAY FIX - Failed to update ticket status: {status_update_result}")
            except Exception as e:
                print(f"[DEBUG] Error updating ticket status: {e}")
            
            # Redirect to bookings page with success message
            return HttpResponseRedirect(reverse("bookings") + "?payment=success")
            
        else:
            # GET request - show payment form (this shouldn't happen normally)
            return render(request, "flight/payment.html", {
                'message': 'Payment form accessed directly'
            })
    else:
        return HttpResponseRedirect(reverse("login"))

def ticket_data(request, ref):
    """Ticket data API - simplified for UI service"""
    return JsonResponse({
        'ref': ref,
        'status': 'Service unavailable',
        'message': 'Backend service not connected'
    })

@csrf_exempt
def get_ticket(request):
    """Get ticket PDF - simplified for UI service"""
    return HttpResponse("PDF generation will be available when backend service is connected", content_type='text/plain')

def bookings(request):
    """User bookings page with backend integration"""
    if request.user.is_authenticated:
        context = {
            'page': 'bookings',
            'tickets': [],
        }
        
        # Check if redirected from successful payment
        if request.GET.get('payment') == 'success':
            context['success_message'] = 'Payment successful! Your booking has been confirmed.'
        
        # Get user bookings from backend API (including SAGA bookings)
        print(f"[DEBUG] Fetching tickets for logged-in user ID: {request.user.id}")
        print(f"[DEBUG] BOOKING DISPLAY FIX - Calling new endpoint: api/tickets/user/{request.user.id}/with-saga/")
        user_tickets_data = call_backend_api(f'api/tickets/user/{request.user.id}/with-saga/')
        if user_tickets_data:
            context['tickets'] = user_tickets_data
            print(f"[DEBUG] BOOKING DISPLAY FIX - Retrieved {len(user_tickets_data)} tickets for user {request.user.id}")
            print(f"[DEBUG] BOOKING DISPLAY FIX - Tickets found: {user_tickets_data}")
        else:
            print(f"[DEBUG] BOOKING DISPLAY FIX - No tickets found for user {request.user.id}")
            context['message'] = 'No bookings found or unable to retrieve booking history.'
            
        return render(request, 'flight/bookings.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def cancel_ticket(request):
    """Cancel ticket with points reversal"""
    if request.method == 'POST':
        booking_ref = request.POST.get('ref')
        if not booking_ref:
            return JsonResponse({'success': False, 'error': 'Booking reference is required'})
        
        try:
            print(f"[DEBUG] Cancelling ticket: {booking_ref}")
            
            # Get booking details first to calculate points reversal
            user_tickets_data = call_backend_api(f'api/tickets/user/{request.user.id}/')
            if not user_tickets_data:
                return JsonResponse({'success': False, 'error': 'Unable to retrieve booking details'})
            
            # Find the specific booking
            booking_to_cancel = None
            for ticket in user_tickets_data:
                if ticket.get('booking_reference') == booking_ref:
                    booking_to_cancel = ticket
                    break
            
            if not booking_to_cancel:
                return JsonResponse({'success': False, 'error': 'Booking not found'})
            
            # Calculate points to reverse (points earned from this booking)
            flight_fare = booking_to_cancel.get('flight', {}).get('economy_fare', 0)
            total_fare = flight_fare + FEE
            points_to_reverse = int(total_fare)  # 1 dollar = 1 point
            
            print(f"[DEBUG] Reversing {points_to_reverse} points for cancelled booking {booking_ref}")
            
            # Reverse loyalty points
            try:
                loyalty_url = settings.LOYALTY_SERVICE_URL
                reverse_url = f"{loyalty_url}/api/loyalty/points/redeem/"
                
                reverse_data = {
                    'user_id': request.user.id,
                    'points_to_redeem': points_to_reverse,
                    'transaction_id': f"CANCEL_{booking_ref}"
                }
                
                reverse_response = requests.post(reverse_url, json=reverse_data)
                if reverse_response.status_code == 200:
                    print(f"[DEBUG] Points reversed successfully for cancellation")
                else:
                    print(f"[DEBUG] Failed to reverse points: {reverse_response.status_code}")
            except Exception as e:
                print(f"[DEBUG] Error reversing points: {e}")
            
            # For now, simulate successful cancellation
            # In a real implementation, this would call the backend cancellation API
            
            return JsonResponse({
                'success': True,
                'message': f'Ticket {booking_ref} cancelled successfully.'
            })
            
        except Exception as e:
            print(f"[DEBUG] Cancellation error: {e}")
            return JsonResponse({'success': False, 'error': 'Cancellation failed. Please try again.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def resume_booking(request):
    """Resume booking - simplified for UI service"""
    if request.user.is_authenticated:
        return render(request, "flight/payment.html", {
            'message': 'Resume booking functionality will be available when backend service is connected'
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def contact(request):
    """Contact page"""
    return render(request, 'flight/contact.html')

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'flight/privacy-policy.html')

def terms_and_conditions(request):
    """Terms and conditions page"""
    return render(request, 'flight/terms.html')

def about_us(request):
    """About us page"""
    return render(request, 'flight/about.html')

def aadvantage_dashboard(request):
    """AAdvantage loyalty dashboard"""
    if request.user.is_authenticated:
        # Use local loyalty tracker instead of external service
        try:
            user_loyalty = loyalty_tracker.get_user_points(request.user.id)
            loyalty_data = {
                'status': 'active',
                'user_tier': 'Member',
                'points_balance': user_loyalty.get('points_balance', 0),
                'miles_to_next_tier': 0,
                'benefits': [
                    'Earn 1 point per $1 spent',
                    'Redeem points for discounts (1 point = $0.01)'
                ]
            }
            print(f"[DEBUG] Using local loyalty tracker with {loyalty_data['points_balance']} points")
        except Exception as e:
            print(f"[DEBUG] Local loyalty tracker error: {e}")
            loyalty_data = None
            
        # Get transaction history from local tracker
        try:
            print(f"[DEBUG] AADVANTAGE DASHBOARD - Requesting transaction history for user {request.user.id}")
            transaction_history = loyalty_tracker.get_user_transactions(request.user.id)
            print(f"[DEBUG] AADVANTAGE DASHBOARD - Retrieved {len(transaction_history)} transactions")
            print(f"[DEBUG] AADVANTAGE DASHBOARD - Transaction history data: {transaction_history}")
            
            # Check if we have any redemption transactions
            redemption_count = sum(1 for t in transaction_history if t.get('type') == 'miles_redemption')
            print(f"[DEBUG] AADVANTAGE DASHBOARD - Found {redemption_count} redemption transactions")
            
        except Exception as e:
            print(f"[ERROR] AADVANTAGE DASHBOARD - Transaction history error: {e}")
            transaction_history = []
            
        if not loyalty_data:
            # Fallback if local tracker fails
            loyalty_data = {
                'status': 'active',
                'user_tier': 'Member',
                'points_balance': 0,
                'miles_to_next_tier': 0,
                'benefits': [
                    'Earn 1 point per $1 spent',
                    'Redeem points for discounts (1 point = $0.01)'
                ]
            }
        
        context = {
            'page': 'aadvantage',
            'loyalty_data': loyalty_data,
            'transaction_history': transaction_history
        }
        return render(request, 'flight/aadvantage_dashboard.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))
