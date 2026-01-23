"""
Enhanced SAGA Orchestrator with Detailed Operation Tracking
Tracks all operations, compensation, and loyalty points adjustments
"""

import logging
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations tracked"""
    RESERVE_SEAT = "RESERVE_SEAT"
    DEDUCT_POINTS = "DEDUCT_POINTS"
    CHARGE_PAYMENT = "CHARGE_PAYMENT"
    CONFIRM_BOOKING = "CONFIRM_BOOKING"
    REVERSE_SEAT = "REVERSE_SEAT"
    REFUND_POINTS = "REFUND_POINTS"
    REFUND_PAYMENT = "REFUND_PAYMENT"
    REVERSE_BOOKING = "REVERSE_BOOKING"


class Operation:
    """Represents a single operation (forward or backward)"""
    
    def __init__(self, op_type: OperationType, description: str, details: Dict[str, Any]):
        self.op_id = f"op_{int(time.time() * 1000)}"
        self.op_type = op_type
        self.description = description
        self.details = details
        self.timestamp = datetime.now().isoformat()
        self.status = "PENDING"
        self.result = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'op_id': self.op_id,
            'type': self.op_type.value,
            'description': self.description,
            'details': self.details,
            'timestamp': self.timestamp,
            'status': self.status,
            'result': self.result
        }


class OperationHistory:
    """Tracks all operations and their reversals"""
    
    def __init__(self):
        self.operations: List[Operation] = []
        self.loyalty_adjustments: List[Dict[str, Any]] = []
        self.payment_transactions: List[Dict[str, Any]] = []
        
    def record_operation(self, op_type: OperationType, description: str, details: Dict[str, Any]) -> Operation:
        """Record a new operation"""
        operation = Operation(op_type, description, details)
        operation.status = "COMPLETED"
        self.operations.append(operation)
        
        logger.info(f"[OPERATION] {op_type.value}: {description}")
        
        return operation
    
    def record_loyalty_adjustment(self, adjustment_type: str, points: int, reason: str, timestamp: str = None):
        """Record loyalty points adjustment"""
        adjustment = {
            'type': adjustment_type,  # 'DEDUCT' or 'REFUND'
            'points': points,
            'reason': reason,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        self.loyalty_adjustments.append(adjustment)
        
        symbol = '-' if adjustment_type == 'DEDUCT' else '+'
        logger.info(f"[LOYALTY] {symbol}{points} points - {reason}")
        
    def record_payment_transaction(self, transaction_type: str, amount: float, reason: str, timestamp: str = None):
        """Record payment transaction"""
        transaction = {
            'type': transaction_type,  # 'CHARGE' or 'REFUND'
            'amount': amount,
            'reason': reason,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        self.payment_transactions.append(transaction)
        
        symbol = '-' if transaction_type == 'CHARGE' else '+'
        logger.info(f"[PAYMENT] {symbol}${amount:.2f} - {reason}")
    
    def get_loyalty_summary(self) -> Dict[str, Any]:
        """Get summary of loyalty points changes"""
        total_deducted = sum(adj['points'] for adj in self.loyalty_adjustments if adj['type'] == 'DEDUCT')
        total_refunded = sum(adj['points'] for adj in self.loyalty_adjustments if adj['type'] == 'REFUND')
        net_change = total_refunded - total_deducted
        
        return {
            'total_deducted': total_deducted,
            'total_refunded': total_refunded,
            'net_change': net_change,
            'adjustments': self.loyalty_adjustments
        }
    
    def get_payment_summary(self) -> Dict[str, Any]:
        """Get summary of payment transactions"""
        total_charged = sum(t['amount'] for t in self.payment_transactions if t['type'] == 'CHARGE')
        total_refunded = sum(t['amount'] for t in self.payment_transactions if t['type'] == 'REFUND')
        net_charge = total_charged - total_refunded
        
        return {
            'total_charged': total_charged,
            'total_refunded': total_refunded,
            'net_charge': net_charge,
            'transactions': self.payment_transactions
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operations': [op.to_dict() for op in self.operations],
            'loyalty_summary': self.get_loyalty_summary(),
            'payment_summary': self.get_payment_summary(),
            'all_operations_count': len(self.operations),
            'reversals_count': len([op for op in self.operations if op.op_type.value.startswith('REVERSE') or op.op_type.value.startswith('REFUND')])
        }


class EnhancedBookingSAGAOrchestrator:
    """
    Enhanced SAGA Orchestrator with detailed operation tracking
    """
    
    def __init__(self):
        self.correlation_id = None
        self.booking_data = None
        self.failure_scenarios = {}
        self.history = OperationHistory()
        self.saga_log = []
        self.steps_executed = []
        self.failed_step = None
        self.failure_reason = None
        
    def start_booking_saga(
        self, 
        booking_data: Dict[str, Any],
        failure_scenarios: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Start the SAGA with tracking"""
        
        self.correlation_id = str(uuid.uuid4())
        self.booking_data = booking_data
        self.failure_scenarios = failure_scenarios or {}
        
        logger.info("=" * 80)
        logger.info(f"[SAGA] 🚀 Starting booking SAGA: {self.correlation_id}")
        logger.info("=" * 80)
        
        # Define steps
        steps = [
            ("RESERVE_SEAT", self._execute_reserve_seat),
            ("DEDUCT_LOYALTY_POINTS", self._execute_deduct_points),
            ("PROCESS_PAYMENT", self._execute_process_payment),
            ("CONFIRM_BOOKING", self._execute_confirm_booking)
        ]
        
        # Execute steps
        for step_name, step_fn in steps:
            if self.failure_scenarios.get(step_name.lower(), False):
                # This step should fail
                self.failed_step = step_name
                self.failure_reason = f"Simulated failure at {step_name}"
                logger.error(f"[SAGA] ❌ {step_name} FAILED (simulated)")
                
                # Execute compensation
                self._execute_compensation()
                
                return self._build_failure_response()
            
            # Execute the step
            try:
                step_fn()
                self.steps_executed.append(step_name)
                logger.info(f"[SAGA] ✅ {step_name} COMPLETED")
            except Exception as e:
                self.failed_step = step_name
                self.failure_reason = str(e)
                logger.error(f"[SAGA] ❌ {step_name} FAILED: {e}")
                
                # Execute compensation
                self._execute_compensation()
                
                return self._build_failure_response()
        
        # All steps completed
        return self._build_success_response()
    
    def _execute_reserve_seat(self):
        """Execute seat reservation step"""
        logger.info("[STEP 1/4] Reserving seat...")
        
        flight_id = self.booking_data.get('flight_id', 'UNKNOWN')
        seat_id = f"SEAT_{flight_id}_{int(time.time())}"
        
        self.history.record_operation(
            OperationType.RESERVE_SEAT,
            f"Reserved seat on flight {flight_id}",
            {'flight_id': flight_id, 'seat_id': seat_id}
        )
        
        time.sleep(0.3)
    
    def _execute_deduct_points(self):
        """Execute loyalty points deduction"""
        logger.info("[STEP 2/4] Deducting loyalty points...")
        
        points = self.booking_data.get('loyalty_points_to_use', 0)
        discount = points * 0.01
        
        self.history.record_operation(
            OperationType.DEDUCT_POINTS,
            f"Deducted {points} loyalty points",
            {'points': points, 'discount': discount}
        )
        
        self.history.record_loyalty_adjustment(
            'DEDUCT',
            points,
            'Deducted for flight booking discount'
        )
        
        time.sleep(0.3)
    
    def _execute_process_payment(self):
        """Execute payment processing"""
        logger.info("[STEP 3/4] Processing payment...")
        
        total_fare = self.booking_data.get('total_fare', 0)
        txn_id = f"TXN_{self.correlation_id[:8]}_{int(time.time())}"
        
        self.history.record_operation(
            OperationType.CHARGE_PAYMENT,
            f"Charged ${total_fare:.2f} for flight booking",
            {'amount': total_fare, 'transaction_id': txn_id}
        )
        
        self.history.record_payment_transaction(
            'CHARGE',
            total_fare,
            'Payment for flight booking'
        )
        
        time.sleep(0.3)
    
    def _execute_confirm_booking(self):
        """Execute booking confirmation"""
        logger.info("[STEP 4/4] Confirming booking...")
        
        booking_id = f"BK_{self.correlation_id[:8]}"
        
        self.history.record_operation(
            OperationType.CONFIRM_BOOKING,
            f"Booking confirmed with ID {booking_id}",
            {'booking_id': booking_id, 'status': 'CONFIRMED'}
        )
        
        time.sleep(0.3)
    
    def _execute_compensation(self):
        """Execute compensation for failed SAGA"""
        logger.info("=" * 80)
        logger.info(f"[COMPENSATION] 🔄 Starting compensation flow")
        logger.info("=" * 80)
        
        # Reverse in opposite order
        reversals = [
            ("CONFIRM_BOOKING", OperationType.REVERSE_BOOKING, "Booking cancelled due to failure"),
            ("PROCESS_PAYMENT", OperationType.REFUND_PAYMENT, "Payment refunded due to failure"),
            ("DEDUCT_LOYALTY_POINTS", OperationType.REFUND_POINTS, "Loyalty points refunded due to failure"),
            ("RESERVE_SEAT", OperationType.REVERSE_SEAT, "Seat reservation cancelled due to failure"),
        ]
        
        for step_name, op_type, description in reversals:
            if step_name in self.steps_executed:
                logger.info(f"[COMPENSATION] Reversing: {step_name}")
                
                # Reverse operation
                if op_type == OperationType.REVERSE_SEAT:
                    self.history.record_operation(op_type, description, {})
                
                elif op_type == OperationType.REFUND_POINTS:
                    points = self.booking_data.get('loyalty_points_to_use', 0)
                    self.history.record_operation(op_type, description, {'points': points})
                    self.history.record_loyalty_adjustment('REFUND', points, description)
                
                elif op_type == OperationType.REFUND_PAYMENT:
                    total_fare = self.booking_data.get('total_fare', 0)
                    self.history.record_operation(op_type, description, {'amount': total_fare})
                    self.history.record_payment_transaction('REFUND', total_fare, description)
                
                elif op_type == OperationType.REVERSE_BOOKING:
                    self.history.record_operation(op_type, description, {})
                
                time.sleep(0.2)
                logger.info(f"[COMPENSATION] ✅ {step_name} reversed")
    
    def _build_success_response(self) -> Dict[str, Any]:
        """Build success response"""
        logger.info("=" * 80)
        logger.info(f"[SAGA] ✅ BOOKING SUCCESSFUL")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'correlation_id': self.correlation_id,
            'booking_reference': self.correlation_id[:8].upper(),
            'steps_completed': len(self.steps_executed),
            'total_steps': 4,
            'status': 'CONFIRMED',
            'history': self.history.to_dict(),
            'operations': self.history.operations,
            'loyalty_summary': self.history.get_loyalty_summary(),
            'payment_summary': self.history.get_payment_summary()
        }
    
    def _build_failure_response(self) -> Dict[str, Any]:
        """Build failure response with detailed tracking"""
        logger.info("=" * 80)
        logger.info(f"[SAGA] ❌ BOOKING FAILED")
        logger.info("=" * 80)
        
        # Calculate net changes
        loyalty_summary = self.history.get_loyalty_summary()
        payment_summary = self.history.get_payment_summary()
        
        return {
            'success': False,
            'correlation_id': self.correlation_id,
            'failed_step': self.failed_step,
            'failure_reason': self.failure_reason,
            'steps_completed': len(self.steps_executed),
            'total_steps': 4,
            'status': 'CANCELLED',
            'history': self.history.to_dict(),
            'operations': self.history.operations,
            'loyalty_summary': loyalty_summary,
            'payment_summary': payment_summary,
            'compensation_executed': True,
            'reversals_count': len([op for op in self.history.operations 
                                   if op.op_type.value.startswith('REVERSE') or 
                                      op.op_type.value.startswith('REFUND')])
        }
