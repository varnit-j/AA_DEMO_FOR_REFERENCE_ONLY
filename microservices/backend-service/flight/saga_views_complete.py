

"""
Complete SAGA Views for Backend Service
Integrates SAGA pattern with existing booking system
"""
import logging
import json
import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Flight, Place, Week, SagaTransaction, SagaPaymentAuthorization, SagaMilesAward, SeatReservation, Ticket, Passenger
from .simple_views import stored_tickets
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# SAGA-specific storage
saga_reservations = {}
saga_orchestrator = None

# Initialize orchestrator
def get_orchestrator():
    global saga_orchestrator
    if saga_orchestrator is None:
        try:
            from .saga_orchestrator_fixed import BookingOrchestrator
            saga_orchestrator = BookingOrchestrator()
            logger.info("[SAGA] Orchestrator initialized successfully")
        except ImportError as e:
            logger.error(f"[SAGA] Failed to import orchestrator: {e}")
            saga_orchestrator = None
    return saga_orchestrator

@csrf_exempt
@require_http_methods(["POST"])
def start_booking_saga(request):
    """Start the complete SAGA booking process"""
    try:
        data = json.loads(request.body)
        logger.info(f"[SAGA] Starting booking SAGA with data: {data}")
        
        # Validate required fields
        flight_id = data.get('flight_id')
        passengers = data.get('passengers', [])
        contact_info = data.get('contact_info', {})
        
        if not flight_id or not passengers or not contact_info:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: flight_id, passengers, contact_info'
            }, status=400)
        
        # Get flight details
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Flight {flight_id} not found'
            }, status=404)
        
        # Prepare booking data for SAGA
        booking_data = {
            'flight_id': flight_id,
            'user_id': data.get('user_id', 1),
            'passengers': passengers,
            'contact_info': contact_info,
            'flight_fare': float(flight.economy_fare),
            'flight': {
                'id': flight.id,
                'flight_number': flight.flight_number,
                'economy_fare': float(flight.economy_fare),
                'origin': str(flight.origin),
                'destination': str(flight.destination)
            },
            # Failure simulation flags
            'simulate_reserveseat_fail': data.get('simulate_reserveseat_fail', False),
            'simulate_authorizepayment_fail': data.get('simulate_authorizepayment_fail', False),
            'simulate_awardmiles_fail': data.get('simulate_awardmiles_fail', False),
            'simulate_confirmbooking_fail': data.get('simulate_confirmbooking_fail', False)
        }
        
        # Get orchestrator and start SAGA
        orchestrator = get_orchestrator()
        if not orchestrator:
            return JsonResponse({
                'success': False,
                'error': 'SAGA orchestrator not available'
            }, status=500)
        
        # Create SAGA transaction record in database
        try:
            flight = Flight.objects.get(id=flight_id)
            saga_transaction = SagaTransaction.objects.create(
                correlation_id=str(uuid.uuid4()),
                user_id=booking_data.get('user_id'),
                flight=flight,
                booking_data=booking_data,
                status='STARTED'
            )
            
            # Update booking data with correlation ID
            booking_data['correlation_id'] = saga_transaction.correlation_id
            
            # Start SAGA process
            result = orchestrator.start_booking_saga(booking_data)
            
            # Update SAGA transaction status based on result
            if result.get('success'):
                saga_transaction.status = 'COMPLETED'
                saga_transaction.steps_completed = result.get('steps_completed', 0)
            else:
                saga_transaction.status = 'FAILED'
                saga_transaction.failed_step = result.get('failed_step')
                saga_transaction.error_message = result.get('error')
                saga_transaction.compensation_executed = bool(result.get('compensation_result'))
            
            saga_transaction.save()
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"[SAGA] Error creating SAGA transaction: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to create SAGA transaction: {str(e)}'
            })
        
    except Exception as e:
        logger.error(f"[SAGA] Error starting booking SAGA: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def reserve_seat(request):
    """SAGA Step 1: Reserve seat for booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] ReserveSeat step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in ReserveSeat for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated seat reservation failure"
            })
        
        # Store reservation in memory for now
        saga_reservations[correlation_id] = {
            'flight_id': booking_data.get('flight_id'),
            'passengers': booking_data.get('passengers', []),
            'user_id': booking_data.get('user_id'),
            'status': 'reserved'
        }
        
        logger.info(f"[SAGA] Seat reservation successful for {correlation_id}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "reservation_id": correlation_id,
            "message": "Seat reserved successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ReserveSeat: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def confirm_booking(request):
    """SAGA Step 4: Confirm booking and create proper Ticket record"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        booking_data = data.get('booking_data', {})
        simulate_failure = data.get('simulate_failure', False)
        
        logger.info(f"[SAGA] ConfirmBooking step for correlation_id: {correlation_id}")
        
        # Simulate failure if requested
        if simulate_failure:
            logger.error(f"[SAGA] Simulated failure in ConfirmBooking for {correlation_id}")
            return JsonResponse({
                "success": False,
                "error": "Simulated booking confirmation failure"
            })
        
        # Get flight details
        flight_id = booking_data.get('flight_id')
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": f"Flight {flight_id} not found"
            })
        
        # Generate unique reference number
        import secrets
        ref_no = secrets.token_hex(3).upper()
        
        # Calculate proper flight dates based on actual flight schedule
        from datetime import datetime, timedelta, time
        booking_date = timezone.now()
        
        # Get actual flight departure date from flight schedule
        # Business Rule: Use flight's actual schedule, not arbitrary dates
        if hasattr(flight, 'depart_day') and flight.depart_day.exists():
            # Find next occurrence of flight's scheduled day
            today_weekday = booking_date.weekday()  # 0=Monday, 6=Sunday
            flight_days = [day.number for day in flight.depart_day.all()]
            
            # Find next available flight day (minimum 2 hours advance booking)
            days_ahead = 1
            for i in range(7):  # Check next 7 days
                check_date = booking_date + timedelta(days=i)
                check_weekday = check_date.weekday()
                
                # Check if flight operates on this day and booking is at least 2 hours in advance
                if check_weekday in flight_days:
                    flight_datetime = timezone.make_aware(datetime.combine(check_date.date(), flight.depart_time))
                    if flight_datetime > booking_date + timedelta(hours=2):
                        days_ahead = i
                        break
            
            flight_ddate = (booking_date + timedelta(days=days_ahead)).date()
        else:
            # Fallback: Next day if no schedule defined
            flight_ddate = (booking_date + timedelta(days=1)).date()
        
        # Calculate arrival date based on flight duration
        if flight.duration:
            departure_datetime = datetime.combine(flight_ddate, flight.depart_time)
            arrival_datetime = departure_datetime + flight.duration
            flight_adate = arrival_datetime.date()
        else:
            # Fallback: Same day arrival
            flight_adate = flight_ddate
        
        # Business Validation: Check advance booking requirements
        min_advance_hours = 2  # Business rule: minimum 2 hours advance booking
        
        # Fix timezone issue: make flight_datetime timezone-aware
        flight_datetime = timezone.make_aware(datetime.combine(flight_ddate, flight.depart_time))
        booking_deadline = booking_date + timedelta(hours=min_advance_hours)
        
        if flight_datetime <= booking_deadline:
            return JsonResponse({
                "success": False,
                "error": f"Booking must be made at least {min_advance_hours} hours in advance"
            })
        
        # Get or create user for proper business tracking
        user_id = booking_data.get('user_id')
        user = None
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found, creating ticket without user association")
        
        # Create Passenger records with business validation
        passengers_data = booking_data.get('passengers', [])
        if not passengers_data:
            return JsonResponse({
                "success": False,
                "error": "At least one passenger is required"
            })
        
        passenger_objects = []
        for i, passenger_data in enumerate(passengers_data):
            # Business validation for passenger data
            first_name = passenger_data.get('first_name', '').strip()
            last_name = passenger_data.get('last_name', '').strip()
            
            if not first_name or not last_name:
                return JsonResponse({
                    "success": False,
                    "error": f"Passenger {i+1}: First name and last name are required"
                })
            
            passenger = Passenger.objects.create(
                first_name=first_name,
                last_name=last_name,
                gender=passenger_data.get('gender', 'male')
            )
            passenger_objects.append(passenger)
        
        # Calculate business-appropriate pricing
        contact_info = booking_data.get('contact_info', {})
        seat_class = booking_data.get('seat_class', 'economy')
        
        # Get fare based on seat class (business rule)
        if seat_class == 'business' and flight.business_fare:
            base_fare = flight.business_fare
        elif seat_class == 'first' and flight.first_fare:
            base_fare = flight.first_fare
        else:
            base_fare = flight.economy_fare
            seat_class = 'economy'  # Default to economy if class not available
        
        # Calculate total fare with business charges
        passenger_count = len(passenger_objects)
        flight_fare = base_fare * passenger_count
        
        # Business charges (taxes, fees, etc.)
        tax_rate = 0.08  # 8% tax
        service_fee = 25.0  # Fixed service fee
        other_charges = (flight_fare * tax_rate) + service_fee
        total_fare = flight_fare + other_charges
        
        # Validate contact information (business requirement)
        email = contact_info.get('email', '').strip()
        mobile = contact_info.get('mobile', '').strip()
        
        if not email or '@' not in email:
            return JsonResponse({
                "success": False,
                "error": "Valid email address is required"
            })
        
        if not mobile or len(mobile) < 10:
            return JsonResponse({
                "success": False,
                "error": "Valid mobile number is required"
            })
        
        # Create proper Ticket record with business validation
        ticket = Ticket.objects.create(
            user=user,  # Proper user association
            ref_no=ref_no,
            flight=flight,
            flight_ddate=flight_ddate,
            flight_adate=flight_adate,
            flight_fare=flight_fare,
            other_charges=other_charges,
            total_fare=total_fare,
            seat_class=seat_class,
            booking_date=booking_date,
            mobile=mobile,
            email=email,
            status='CONFIRMED'
        )
        
        # Add passengers to ticket
        ticket.passengers.set(passenger_objects)
        
        # Calculate cancellation policy (business rule)
        cancellation_deadline = flight_datetime - timedelta(hours=24)  # 24 hours before flight
        refund_policy = "Full refund available until 24 hours before departure"
        
        if booking_date > cancellation_deadline:
            refund_policy = "No refund available - within 24 hours of departure"
        
        logger.info(f"[SAGA] Business-compliant booking confirmed: {ref_no} for {passenger_count} passengers")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "booking_reference": ref_no,
            "ticket_id": ticket.id,
            "flight_number": flight.flight_number,
            "flight_ddate": flight_ddate.strftime('%Y-%m-%d'),
            "flight_adate": flight_adate.strftime('%Y-%m-%d'),
            "departure_time": flight.depart_time.strftime('%H:%M'),
            "arrival_time": flight.arrival_time.strftime('%H:%M'),
            "seat_class": seat_class,
            "passenger_count": passenger_count,
            "total_fare": total_fare,
            "cancellation_deadline": cancellation_deadline.strftime('%Y-%m-%d %H:%M'),
            "refund_policy": refund_policy,
            "message": "Business-compliant booking confirmed successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in ConfirmBooking: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def cancel_seat(request):
    """SAGA Compensation: Cancel seat reservation"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] CancelSeat compensation for correlation_id: {correlation_id}")
        
        # Remove from memory storage
        if correlation_id in saga_reservations:
            del saga_reservations[correlation_id]
            logger.info(f"[SAGA] Seat reservation cancelled for {correlation_id}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "message": "Seat reservation cancelled successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in CancelSeat compensation: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def cancel_booking(request):
    """SAGA Compensation: Cancel booking"""
    try:
        data = json.loads(request.body)
        correlation_id = data.get('correlation_id')
        
        logger.info(f"[SAGA] CancelBooking compensation for correlation_id: {correlation_id}")
        
        # For now, just log the cancellation
        # In a real system, you would mark the ticket as cancelled
        logger.info(f"[SAGA] Booking cancelled for {correlation_id}")
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "message": "Booking cancelled successfully"
        })
        
    except Exception as e:
        logger.error(f"[SAGA] Error in CancelBooking compensation: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_saga_status(request, correlation_id):
    """Get SAGA transaction status"""
    try:
        saga_transaction = SagaTransaction.objects.get(correlation_id=correlation_id)
        
        return JsonResponse({
            "success": True,
            "correlation_id": correlation_id,
            "status": saga_transaction.status,
            "steps_completed": saga_transaction.steps_completed,
            "failed_step": saga_transaction.failed_step,
            "error_message": saga_transaction.error_message,
            "created_at": saga_transaction.created_at.isoformat(),
            "updated_at": saga_transaction.updated_at.isoformat()
        })
        
    except SagaTransaction.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": f"SAGA transaction {correlation_id} not found"
        }, status=404)
    except Exception as e:
        logger.error(f"[SAGA] Error getting SAGA status: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        })