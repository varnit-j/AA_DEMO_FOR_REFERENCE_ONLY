# 🎯 SAGA Pattern Demo Guide

## How to Demonstrate SAGA Implementation in Your Flight Booking System

This guide provides step-by-step instructions to showcase the SAGA pattern implementation across all microservices.

---

## 🚀 **Demo Setup (Prerequisites)**

### 1. Start All Microservices
```bash
# Terminal 1: Backend Service (Orchestrator)
cd AA_Flight_booking/microservices/backend-service
python3.12 manage.py runserver 8001

# Terminal 2: Payment Service  
cd AA_Flight_booking/microservices/payment-service
python3.12 manage.py runserver 8003

# Terminal 3: Loyalty Service
cd AA_Flight_booking/microservices/loyalty-service
python3.12 manage.py runserver 8002

# Terminal 4: UI Service
cd AA_Flight_booking/microservices/ui-service
python3.12 manage.py runserver 8000
```

### 2. Open Browser
Navigate to: `http://localhost:8000`

---

## 🎬 **Demo Scenario 1: Successful SAGA Transaction**

### **What to Show:** Complete booking flow with all SAGA steps succeeding

#### **Step 1: Login**
- Go to `http://localhost:8000`
- Click "Login" 
- Use credentials: `username: admin`, `password: admin` (or register new user)

#### **Step 2: Search Flights**
- Origin: `ORD` (Chicago)
- Destination: `DFW` (Dallas)
- Date: Tomorrow's date
- Click "Search Flights"

#### **Step 3: Book Flight**
- Select any flight
- Click "Book Now"
- Fill passenger details:
  - First Name: `John`
  - Last Name: `Doe`
  - Gender: `Male`
- Add contact info
- Click "Proceed to Payment"

#### **Step 4: Monitor SAGA Execution**
**Watch the terminal logs carefully - this is where SAGA magic happens!**

**Backend Service Terminal will show:**
```
[SAGA] Starting booking SAGA with correlation_id: [unique-id]
[SAGA] Executing step 1/4: ReserveSeat
[SAGA] Executing step 2/4: AuthorizePayment  
[SAGA] Executing step 3/4: AwardMiles
[SAGA] Executing step 4/4: ConfirmBooking
[SAGA] All steps completed successfully
```

**Payment Service Terminal will show:**
```
[SAGA] AuthorizePayment step for correlation_id: [unique-id]
[SAGA] Payment authorized successfully. Amount: $XXX
```

**Loyalty Service Terminal will show:**
```
[SAGA] AwardMiles step for correlation_id: [unique-id]
[SAGA] Awarding XXX miles to user X
[SAGA] Miles awarded successfully. User X: [old-balance] -> [new-balance]
```

#### **Step 5: Complete Payment**
- Choose payment method
- Optionally redeem some points
- Click "Pay Now"
- Verify booking appears in "My Bookings"

---

## 🎬 **Demo Scenario 2: SAGA Compensation (Rollback)**

### **What to Show:** SAGA rollback when a step fails

#### **Method 1: Simulate Payment Failure**
1. Follow steps 1-3 from Scenario 1
2. In the payment service code, temporarily modify the authorization to fail
3. Watch the compensation flow in terminal logs:

```
[SAGA] Step AuthorizePayment failed
[SAGA] Starting compensation for correlation_id: [unique-id]
[SAGA] Executing compensation: ReleaseSeat
[SAGA] Compensation completed successfully
```

#### **Method 2: Use Built-in Failure Simulation**
