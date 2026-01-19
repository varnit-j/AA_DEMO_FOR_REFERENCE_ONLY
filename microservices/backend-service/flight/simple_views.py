from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime
import json
import uuid

from .models import Place, Flight, Week

# Simple in-memory storage for demo purposes
# In production, this would be a database
stored_tickets = {}


@require_http_methods(["GET"])
def flight_search(request):
    """Simple flight search API without DRF"""
    try:
        # Get parameters
        origin_code = request.GET.get('origin', '').upper()
        destination_code = request.GET.get('destination', '').upper()
        depart_date_str = request.GET.get('depart_date', '')
        seat_class = request.GET.get('seat_class', 'economy')
        
        print(f"[DEBUG] Flight search params: origin={origin_code}, dest={destination_code}, date={depart_date_str}, class={seat_class}")
        
        # Basic validation
        if not origin_code or not destination_code or not depart_date_str:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Parse date
        depart_date = datetime.strptime(depart_date_str, '%Y-%m-%d').date()
        
        # Get places
        try:
            origin = Place.objects.get(code=origin_code)
            destination = Place.objects.get(code=destination_code)
        except Place.DoesNotExist:
            return JsonResponse({'error': 'Invalid origin or destination'}, status=400)
        
        # Get flight day
        try:
            flight_day = Week.objects.get(number=depart_date.weekday())
        except Week.DoesNotExist:
            return JsonResponse({'error': 'Invalid date'}, status=400)
        
        # Search flights - limit to American Airlines only
        flights = Flight.objects.filter(
            origin=origin,
            destination=destination,
            depart_day=flight_day,
            airline__icontains='American Airlines'
        )
        
        # Filter by seat class
        if seat_class == 'economy':
            flights = flights.exclude(economy_fare=0).order_by('economy_fare')
        elif seat_class == 'business':
            flights = flights.exclude(business_fare=0).order_by('business_fare')
        elif seat_class == 'first':
            flights = flights.exclude(first_fare=0).order_by('first_fare')
        
        # Convert to JSON
        flights_data = []
        for flight in flights:
            flights_data.append({
                'id': flight.id,
                'plane': flight.plane,
                'airline': flight.airline,
                'flight_number': flight.flight_number,  # Added flight number
                'origin': {
                    'code': flight.origin.code,
                    'city': flight.origin.city,
                    'airport': flight.origin.airport
                },
                'destination': {
                    'code': flight.destination.code,
                    'city': flight.destination.city,
                    'airport': flight.destination.airport
                },
                'depart_time': str(flight.depart_time),
                'arrival_time': str(flight.arrival_time),
                'economy_fare': float(flight.economy_fare),
                'business_fare': float(flight.business_fare),
                'first_fare': float(flight.first_fare),
                'duration': str(flight.duration)
            })
        
        return JsonResponse({
            'flights': flights_data,
            'origin': {
                'code': origin.code,
                'city': origin.city,
                'airport': origin.airport
            },
            'destination': {
                'code': destination.code,
                'city': destination.city,
                'airport': destination.airport
            },
            'depart_date': str(depart_date),
            'seat_class': seat_class
        })
        
    except Exception as e:
        print(f"[ERROR] Flight search exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def book_flight(request):
    """Book a flight - simplified booking endpoint"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(f"[DEBUG] Booking request data: {data}")
        
        # Extract required fields
        flight_id = data.get('flight_id')
        passengers = data.get('passengers', [])
        contact_info = data.get('contact_info', {})
        
        # Validate required fields
        if not flight_id:
            return JsonResponse({'error': 'Flight ID is required'}, status=400)
        
        if not passengers:
            return JsonResponse({'error': 'At least one passenger is required'}, status=400)
        
        # Validate contact info
        if not contact_info.get('email') or not contact_info.get('mobile'):
            return JsonResponse({'error': 'Contact email and mobile are required'}, status=400)
        
        # Get flight details
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({'error': 'Flight not found'}, status=404)
        
        # Validate passengers
        for i, passenger in enumerate(passengers):
            if not passenger.get('first_name') or not passenger.get('last_name'):
                return JsonResponse({'error': f'Passenger {i+1}: First name and last name are required'}, status=400)
            if not passenger.get('gender'):
                return JsonResponse({'error': f'Passenger {i+1}: Gender is required'}, status=400)
        
        # Generate booking reference
        booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
        
        # Prepare flight data for response
        flight_data = {
            'id': flight.id,
            'plane': flight.plane,
            'airline': flight.airline,
            'flight_number': flight.flight_number,  # Added flight number
            'origin': {
                'code': flight.origin.code,
                'city': flight.origin.city,
                'airport': flight.origin.airport
            },
            'destination': {
                'code': flight.destination.code,
                'city': flight.destination.city,
                'airport': flight.destination.airport
            },
            'depart_time': str(flight.depart_time),
            'arrival_time': str(flight.arrival_time),
            'economy_fare': float(flight.economy_fare),
            'business_fare': float(flight.business_fare),
            'first_fare': float(flight.first_fare),
            'duration': str(flight.duration)
        }
        
        print(f"[DEBUG] Booking successful - Reference: {booking_reference}")
        
        # Store the ticket for later retrieval
        user_id = str(data.get('user_id', '1'))  # Get user_id from request data
        print(f"[DEBUG] Using user_id: {user_id} for ticket storage")
        
        if user_id not in stored_tickets:
            stored_tickets[user_id] = []
        
        # Create ticket record
        ticket_record = {
            'booking_reference': booking_reference,
            'flight': flight_data,
            'passengers': passengers,
            'contact_info': contact_info,
            'booking_date': '2026-01-15',  # Simplified for demo
            'status': 'pending'  # Initial status is pending until payment is processed
        }
        
        stored_tickets[user_id].append(ticket_record)
        print(f"[DEBUG] Stored ticket for user {user_id}: {booking_reference}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'booking_reference': booking_reference,
            'flight': flight_data,
            'passengers': passengers,
            'contact_info': contact_info,
            'message': 'Flight booked successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"[ERROR] Booking exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_user_tickets(request, user_id):
    """Get tickets for a specific user"""
    try:
        # Get stored tickets for the user
        user_tickets = stored_tickets.get(str(user_id), [])
        print(f"[DEBUG] Getting tickets for user {user_id}: found {len(user_tickets)} tickets")
        return JsonResponse(user_tickets, safe=False)
        
    except Exception as e:
        print(f"[ERROR] Get user tickets exception: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def places_search(request):
    """Search places by query string"""
    try:
        query = request.GET.get('q', '').strip()
        print(f"[DEBUG] Places search query: '{query}'")
        
        if not query:
            # Return empty list if no query
            return JsonResponse([], safe=False)
        
        # Search places by city, airport, code, or country
        places = Place.objects.filter(
            Q(city__icontains=query) |
            Q(airport__icontains=query) |
            Q(code__icontains=query) |
            Q(country__icontains=query)
        )[:10]  # Limit to 10 results
        
        # Convert to JSON
        places_data = []
        for place in places:
            places_data.append({
                'id': place.id,
                'city': place.city,
                'airport': place.airport,
                'code': place.code,
                'country': place.country,
                'display_name': f"{place.city}, {place.country} ({place.code})"
            })
        
        print(f"[DEBUG] Found {len(places_data)} places for query '{query}'")
        return JsonResponse(places_data, safe=False)
        
    except Exception as e:
        print(f"[ERROR] Places search exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'backend-service'})


@require_http_methods(["GET"])
def get_flight_detail(request, flight_id):
    """Get detailed information about a specific flight"""
    try:
        flight = Flight.objects.get(id=flight_id)
        
        flight_data = {
            'id': flight.id,
            'plane': flight.plane,
            'airline': flight.airline,
            'flight_number': flight.flight_number,  # Added flight number
            'origin': {
                'code': flight.origin.code,
                'city': flight.origin.city,
                'airport': flight.origin.airport
            },
            'destination': {
                'code': flight.destination.code,
                'city': flight.destination.city,
                'airport': flight.destination.airport
            },
            'depart_time': str(flight.depart_time),
            'arrival_time': str(flight.arrival_time),
            'economy_fare': float(flight.economy_fare),
            'business_fare': float(flight.business_fare),
            'first_fare': float(flight.first_fare),
            'duration': str(flight.duration)
        }
        
        return JsonResponse(flight_data)
        
    except Flight.DoesNotExist:
        return JsonResponse({'error': 'Flight not found'}, status=404)
    except Exception as e:
        print(f"[ERROR] Flight detail exception: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_ticket_status(request, booking_ref):
    """Update ticket status by booking reference"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        new_status = data.get('status')
        
        print(f"[DEBUG] Updating ticket {booking_ref} status to: {new_status}")
        
        if not new_status:
            return JsonResponse({'error': 'Status is required'}, status=400)
        
        # Valid status values
        valid_statuses = ['pending', 'confirmed', 'on_hold', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=400)
        
        # Find and update the ticket in stored_tickets
        ticket_found = False
        for user_id, tickets in stored_tickets.items():
            for ticket in tickets:
                if ticket['booking_reference'] == booking_ref:
                    ticket['status'] = new_status
                    ticket_found = True
                    print(f"[DEBUG] Updated ticket {booking_ref} status to {new_status} for user {user_id}")
                    break
            if ticket_found:
                break
        
        if not ticket_found:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'booking_reference': booking_ref,
            'status': new_status,
            'message': f'Ticket status updated to {new_status}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"[ERROR] Update ticket status exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)