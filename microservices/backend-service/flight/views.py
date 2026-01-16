
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.db.models import Q
from datetime import datetime
import secrets

from .models import User, Place, Flight, Passenger, Ticket, Week
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PlaceSerializer, FlightSerializer, PassengerSerializer, TicketSerializer,
    FlightSearchSerializer, BookingSerializer
)


def generate_ref_no():
    """Generate a unique reference number for tickets"""
    return secrets.token_hex(3).upper()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Successfully logged out'})


class PlaceSearchView(generics.ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Place.objects.filter(
                Q(city__icontains=query) |
                Q(airport__icontains=query) |
                Q(code__icontains=query) |
                Q(country__icontains=query)
            )[:10]
        return Place.objects.all()


@api_view(['GET'])
@permission_classes([AllowAny])
def flight_search(request):
    # Get parameters directly from request
    origin_code = request.GET.get('origin', '').upper()
    destination_code = request.GET.get('destination', '').upper()
    depart_date_str = request.GET.get('depart_date', '')
    seat_class = request.GET.get('seat_class', 'economy')
    
    # Basic validation
    if not origin_code or not destination_code or not depart_date_str:
        return Response({'error': 'Missing required parameters: origin, destination, depart_date'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse date
        depart_date = datetime.strptime(depart_date_str, '%Y-%m-%d').date()
        
        origin = Place.objects.get(code=origin_code)
        destination = Place.objects.get(code=destination_code)
        flight_day = Week.objects.get(number=depart_date.weekday())
        
        flights = Flight.objects.filter(
            origin=origin,
            destination=destination,
            depart_day=flight_day,
            airline__icontains='American Airlines'
        )
        
        if seat_class == 'economy':
            flights = flights.exclude(economy_fare=0).order_by('economy_fare')
        elif seat_class == 'business':
            flights = flights.exclude(business_fare=0).order_by('business_fare')
        elif seat_class == 'first':
            flights = flights.exclude(first_fare=0).order_by('first_fare')
        
        flight_serializer = FlightSerializer(flights, many=True)
        return Response({
            'flights': flight_serializer.data,
            'origin': PlaceSerializer(origin).data,
            'destination': PlaceSerializer(destination).data,
            'depart_date': depart_date,
            'seat_class': seat_class
        })
        
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'},
                       status=status.HTTP_400_BAD_REQUEST)
    except Place.DoesNotExist:
        return Response({'error': 'Invalid origin or destination code'},
                       status=status.HTTP_400_BAD_REQUEST)
    except Week.DoesNotExist:
        return Response({'error': 'Invalid date'},
                       status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_flight_detail(request, flight_id):
    """Get detailed information about a specific flight"""
    try:
        flight = Flight.objects.get(id=flight_id)
        serializer = FlightSerializer(flight)
        return Response(serializer.data)
    except Flight.DoesNotExist:
        return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def book_flight(request):
    """Book a flight with passengers"""
    try:
        print(f"[DEBUG] Booking request data: {request.data}")
        
        # Extract booking data
        flight_id = request.data.get('flight_id')
        passengers_data = request.data.get('passengers', [])
        contact_info = request.data.get('contact_info', {})
        user_id = request.data.get('user_id')  # Get user_id from request
        
        if not flight_id or not passengers_data:
            return Response({'error': 'Missing flight_id or passengers'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get flight
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create passengers
        passengers = []
        for passenger_data in passengers_data:
            passenger = Passenger.objects.create(
                first_name=passenger_data.get('first_name', ''),
                last_name=passenger_data.get('last_name', ''),
                gender=passenger_data.get('gender', 'male')
            )
            passengers.append(passenger)
        
        # Get or create user based on provided user_id
        try:
            if user_id:
                user = User.objects.get(id=user_id)
                print(f"[DEBUG] Creating ticket for user ID: {user_id}")
            else:
                user = User.objects.get(id=1)  # Fallback to user ID 1
                print(f"[DEBUG] No user_id provided, using fallback user ID: 1")
        except User.DoesNotExist:
            user = None
            print(f"[DEBUG] ERROR: User ID {user_id or 1} not found in database")
            
        ref_no = generate_ref_no()
        ticket = Ticket.objects.create(
            user=user,
            ref_no=ref_no,
            flight=flight,
            flight_ddate=request.data.get('flight_date', '2024-01-15'),
            flight_adate=request.data.get('flight_date', '2024-01-15'),
            flight_fare=flight.economy_fare,
            other_charges=50.0,
            total_fare=flight.economy_fare + 50.0,
            seat_class='economy',
            mobile=contact_info.get('mobile', ''),
            email=contact_info.get('email', ''),
            status='PENDING'
        )
        
        # Add passengers to ticket
        ticket.passengers.set(passengers)
        
        print(f"[DEBUG] Created ticket: {ticket.ref_no}")
        
        return Response({
            'success': True,
            'booking_reference': ticket.ref_no,
            'ticket_id': ticket.id,
            'flight': FlightSerializer(flight).data,
            'message': 'Booking successful'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"[DEBUG] Booking error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ticket(request, ticket_id):
    """Get ticket details by ID"""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_tickets(request, user_id):
    """Get all tickets for a specific user"""
    try:
        tickets = Ticket.objects.filter(user_id=user_id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_ticket_payment(request, ticket_ref):
    """Confirm ticket payment and update status to CONFIRMED"""
    try:
        ticket = Ticket.objects.get(ref_no=ticket_ref)
        ticket.status = 'CONFIRMED'
        ticket.save()
        
        print(f"[DEBUG] Ticket {ticket_ref} status updated to CONFIRMED")
        
        return Response({
            'success': True,
            'ticket_ref': ticket_ref,
            'status': ticket.status,
            'message': 'Payment confirmed successfully'
        })
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"[DEBUG] Error confirming payment: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
