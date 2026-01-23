"""
Complete SAGA Orchestrator Implementation
Implements proper SAGA pattern with memory queue, sequential execution, 
compensation logic, and comprehensive logging
"""

import logging
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import deque
from enum import Enum

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('saga_orchestrator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SAGAStepStatus(Enum):
    """SAGA step status enumeration"""
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"


class SAGAStep:
    """Represents a single SAGA step"""
    
    def __init__(self, step_id: str, step_name: str, step_data: Dict[str, Any]):
        self.step_id = step_id
        self.step_name = step_name
        self.step_data = step_data
        self.status = SAGAStepStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.compensation_required = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            'step_id': self.step_id,
            'step_name': self.step_name,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'compensation_required': self.compensation_required
        }


class SAGAMemoryQueue:
    """Memory-based queue for SAGA step management with proper sequencing"""
    
    def __init__(self):
        self.pending_steps: deque = deque()
        self.executing_steps: dict = {}
        self.completed_steps: List[SAGAStep] = []
        self.failed_steps: List[SAGAStep] = []
        self.compensation_queue: deque = deque()
        self.step_counter = 0
        
    def add_step(self, step_name: str, step_data: Dict[str, Any]) -> str:
        """Add a step to the pending queue and return step ID"""
        step_id = f"step_{self.step_counter}_{int(time.time() * 1000)}"
        self.step_counter += 1
        
        step = SAGAStep(step_id, step_name, step_data)
        self.pending_steps.append(step)
        
        logger.debug(f"[QUEUE] Added step: {step_name} (ID: {step_id}) - Queue size: {len(self.pending_steps)}")
        return step_id
        
    def get_next_step(self) -> Optional[SAGAStep]:
        """Get the next pending step and mark as executing"""
        if self.pending_steps:
            step = self.pending_steps.popleft()
            step.status = SAGAStepStatus.EXECUTING
            step.started_at = datetime.now().isoformat()
            self.executing_steps[step.step_id] = step
            logger.info(f"[QUEUE] Executing step: {step.step_name} (ID: {step.step_id})")
            return step
        return None
        
    def mark_completed(self, step: SAGAStep, result: Dict[str, Any]) -> None:
        """Mark a step as completed"""
        step.status = SAGAStepStatus.COMPLETED
        step.result = result
        step.completed_at = datetime.now().isoformat()
        step.compensation_required = True
        
        if step.step_id in self.executing_steps:
            del self.executing_steps[step.step_id]
            
        self.completed_steps.append(step)
        
        duration = (
            datetime.fromisoformat(step.completed_at) - 
            datetime.fromisoformat(step.started_at)
        ).total_seconds()
        
        logger.info(f"[QUEUE] [OK] Completed: {step.step_name} - Duration: {duration:.2f}s")
        
    def mark_failed(self, step: SAGAStep, error: str) -> None:
        """Mark a step as failed and prepare compensation queue"""
        step.status = SAGAStepStatus.FAILED
        step.error = error
        step.completed_at = datetime.now().isoformat()
        
        if step.step_id in self.executing_steps:
            del self.executing_steps[step.step_id]
            
        self.failed_steps.append(step)
        
        logger.error(f"[QUEUE] ❌ Failed: {step.step_name} - Error: {error}")
        
        # Clear pending steps and add compensation for all completed steps (in reverse order)
        self.pending_steps.clear()
        
        for completed_step in reversed(self.completed_steps):
            if completed_step.compensation_required:
                compensation_step = {
                    'name': f"COMPENSATE_{completed_step.step_name}",
                    'original_step': completed_step,
                    'status': 'PENDING_COMPENSATION'
                }
                self.compensation_queue.append(compensation_step)
                logger.info(f"[COMPENSATION] Queued: {compensation_step['name']}")
        
        logger.info(f"[COMPENSATION] Total compensation steps: {len(self.compensation_queue)}")
        
    def get_pending_count(self) -> int:
        """Get count of pending steps"""
        return len(self.pending_steps)
        
    def get_completed_count(self) -> int:
        """Get count of completed steps"""
        return len(self.completed_steps)
        
    def get_compensation_count(self) -> int:
        """Get count of pending compensation steps"""
        return len(self.compensation_queue)
        
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of queue status"""
        return {
            'pending': len(self.pending_steps),
            'executing': len(self.executing_steps),
            'completed': len(self.completed_steps),
            'failed': len(self.failed_steps),
            'compensation_pending': len(self.compensation_queue)
        }


class BookingSAGAOrchestrator:
    """
    Main SAGA Orchestrator for flight booking
    Manages the complete booking flow with 4 steps:
    1. RESERVE_SEAT - Reserve seat for passenger
    2. DEDUCT_LOYALTY_POINTS - Use loyalty points for discount
    3. PROCESS_PAYMENT - Process payment
    4. CONFIRM_BOOKING - Confirm the booking
    """
    
    def __init__(self):
        self.queue = SAGAMemoryQueue()
        self.correlation_id = None
        self.booking_data = None
        self.saga_log = []
        self.failure_scenarios = {}  # Track which steps should fail
        self.detailed_operations = []  # Track detailed operation records
        self.compensation_history = []  # Track compensation steps with details
        
    def start_booking_saga(
        self, 
        booking_data: Dict[str, Any],
        failure_scenarios: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Start the complete SAGA booking process
        
        Args:
            booking_data: Flight booking data
            failure_scenarios: Dict with scenario flags like {'reserve_seat': True} to fail that step
            
        Returns:
            Dict with saga result
        """
        # CRITICAL: Reset queue and tracking for each SAGA execution
        self.queue = SAGAMemoryQueue()
        self.detailed_operations = []
        self.compensation_history = []
        self.saga_log = []
        
        self.correlation_id = str(uuid.uuid4())
        self.booking_data = booking_data
        self.failure_scenarios = failure_scenarios or {}
        
        logger.info("=" * 80)
        logger.info(f"[SAGA] 🚀 Starting booking SAGA")
        logger.info(f"[SAGA] Correlation ID: {self.correlation_id}")
        logger.info(f"[SAGA] Failure scenarios: {self.failure_scenarios}")
        logger.info("=" * 80)
        
        self._save_saga_log_entry("SAGA_START", {
            "correlation_id": self.correlation_id,
            "booking_data": booking_data,
            "failure_scenarios": self.failure_scenarios
        })
        
        # Define SAGA steps in sequence
        saga_steps = [
            ("RESERVE_SEAT", {
                "description": "Reserve seat for passenger",
                "endpoint": "/api/saga/reserve-seat/",
                "compensation_endpoint": "/api/saga/cancel-seat/"
            }),
            ("DEDUCT_LOYALTY_POINTS", {
                "description": "Deduct loyalty points for discount",
                "endpoint": "/api/saga/deduct-points/",
                "compensation_endpoint": "/api/saga/refund-points/"
            }),
            ("PROCESS_PAYMENT", {
                "description": "Process payment",
                "endpoint": "/api/saga/process-payment/",
                "compensation_endpoint": "/api/saga/refund-payment/"
            }),
            ("CONFIRM_BOOKING", {
                "description": "Confirm booking",
                "endpoint": "/api/saga/confirm-booking/",
                "compensation_endpoint": "/api/saga/cancel-booking/"
            })
        ]
        
        # Add all steps to the queue
        for step_name, step_config in saga_steps:
            step_data = {
                'correlation_id': self.correlation_id,
                'booking_data': booking_data,
                'step_config': step_config,
                'simulate_failure': self.failure_scenarios.get(step_name.lower(), False)
            }
            self.queue.add_step(step_name, step_data)
        
        logger.info(f"[SAGA] Queued {self.queue.get_pending_count()} steps for execution")
        
        # Execute steps sequentially
        return self._execute_saga_steps()
        
    def _execute_saga_steps(self) -> Dict[str, Any]:
        """Execute SAGA steps sequentially from the memory queue"""
        logger.info(f"[SAGA] Starting sequential execution of steps")
        
        while True:
            # Check queue status
            status = self.queue.get_status_summary()
            logger.debug(f"[SAGA] Queue status: {status}")
            
            step = self.queue.get_next_step()
            if not step:
                break
            
            logger.info(f"\n[SAGA STEP] Executing: {step.step_name}")
            
            # Execute the step
            result = self._execute_single_step(step)
            
            if result.get('success'):
                self.queue.mark_completed(step, result)
                self._save_saga_log_entry(f"{step.step_name}_SUCCESS", result)
                logger.info(f"[SAGA] ✅ Step {step.step_name} completed successfully\n")
            else:
                self.queue.mark_failed(step, result.get('error', 'Unknown error'))
                self._save_saga_log_entry(f"{step.step_name}_FAILED", result)
                logger.error(f"[SAGA] ❌ Step {step.step_name} failed\n")
                
                # Execute compensation
                compensation_result = self._execute_compensation()
                
                failure_summary = {
                    'success': False,
                    'correlation_id': self.correlation_id,
                    'failed_step': step.step_name,
                    'error': result.get('error', 'Unknown error'),
                    'steps_completed': self.queue.get_completed_count(),
                    'compensation_result': compensation_result,
                    'compensation_history': self.compensation_history,
                    'detailed_operations': self.detailed_operations,
                    'saga_log': self.saga_log
                }
                
                self._save_saga_log_entry("SAGA_FAILED", failure_summary)
                return failure_summary
        
        # All steps completed successfully
        success_summary = {
            'success': True,
            'correlation_id': self.correlation_id,
            'booking_reference': self.correlation_id[:8].upper(),
            'steps_completed': self.queue.get_completed_count(),
            'total_steps': len([s for s in self.saga_log if 'SUCCESS' in s.get('event_type', '')]),
            'detailed_operations': self.detailed_operations,
            'compensation_history': self.compensation_history,
            'saga_log': self.saga_log
        }
        
        logger.info("=" * 80)
        logger.info(f"[SAGA] ✅ ALL STEPS COMPLETED SUCCESSFULLY")
        logger.info(f"[SAGA] Booking Reference: {success_summary['booking_reference']}")
        logger.info(f"[SAGA] Steps Completed: {success_summary['steps_completed']}")
        logger.info("=" * 80)
        
        self._save_saga_log_entry("SAGA_SUCCESS", success_summary)
        return success_summary
        
    def _execute_single_step(self, step: SAGAStep) -> Dict[str, Any]:
        """Execute a single SAGA step"""
        step_name = step.step_name
        step_data = step.step_data
        
        # Check for simulated failure
        if step_data.get('simulate_failure'):
            logger.warning(f"[SAGA] ⚠️  Simulating failure for step: {step_name}")
            return {
                'success': False,
                'error': f'Simulated failure for {step_name} as per failure scenario'
            }
        
        try:
            # Simulate step execution
            logger.info(f"[SAGA STEP] Processing {step_name}...")
            
            # Simulate different processing times
            time.sleep(0.5)
            
            # Execute step logic based on step name
            result = self._execute_step_logic(step_name, step_data)
            
            return result
            
        except Exception as e:
            error_msg = f"Exception in {step_name}: {str(e)}"
            logger.error(f"[SAGA] {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _execute_step_logic(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific logic for each SAGA step"""
        booking_data = step_data['booking_data']
        
        if step_name == "RESERVE_SEAT":
            logger.info("[RESERVE_SEAT] Reserving seat...")
            result = {
                'success': True,
                'step': 'RESERVE_SEAT',
                'seat_id': f"SEAT_{booking_data.get('flight_id', 'UNKNOWN')}_{int(time.time())}",
                'message': 'Seat reserved successfully'
            }
            self.detailed_operations.append({
                'operation': 'RESERVE_SEAT',
                'action': 'Reserve',
                'details': 'Seat reserved on selected flight',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat()
            })
            return result
            
        elif step_name == "DEDUCT_LOYALTY_POINTS":
            logger.info("[DEDUCT_LOYALTY_POINTS] Deducting loyalty points...")
            points_to_deduct = booking_data.get('loyalty_points_to_use', 0)
            result = {
                'success': True,
                'step': 'DEDUCT_LOYALTY_POINTS',
                'points_deducted': points_to_deduct,
                'discount_applied': points_to_deduct * 0.01,  # $0.01 per point
                'message': f'Deducted {points_to_deduct} loyalty points'
            }
            self.detailed_operations.append({
                'operation': 'DEDUCT_LOYALTY_POINTS',
                'action': 'Deduct',
                'points': points_to_deduct,
                'discount': points_to_deduct * 0.01,
                'details': f'Deducted {points_to_deduct} loyalty points for discount',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat()
            })
            return result
            
        elif step_name == "PROCESS_PAYMENT":
            logger.info("[PROCESS_PAYMENT] Processing payment...")
            total_fare = booking_data.get('total_fare', 0)
            result = {
                'success': True,
                'step': 'PROCESS_PAYMENT',
                'transaction_id': f"TXN_{self.correlation_id[:8]}_{int(time.time())}",
                'amount_charged': total_fare,
                'payment_method': booking_data.get('payment_method', 'card'),
                'message': f'Payment of ${total_fare:.2f} processed successfully'
            }
            self.detailed_operations.append({
                'operation': 'PROCESS_PAYMENT',
                'action': 'Charge',
                'amount': total_fare,
                'method': booking_data.get('payment_method', 'card'),
                'details': f'Payment of ${total_fare:.2f} processed',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat()
            })
            return result
            
        elif step_name == "CONFIRM_BOOKING":
            logger.info("[CONFIRM_BOOKING] Confirming booking...")
            result = {
                'success': True,
                'step': 'CONFIRM_BOOKING',
                'booking_id': f"BK_{self.correlation_id[:8]}",
                'status': 'CONFIRMED',
                'message': 'Booking confirmed successfully'
            }
            self.detailed_operations.append({
                'operation': 'CONFIRM_BOOKING',
                'action': 'Confirm',
                'details': 'Booking confirmed and ticket issued',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat()
            })
            return result
        
        return {
            'success': False,
            'error': f'Unknown step: {step_name}'
        }
        
    def _execute_compensation(self) -> Dict[str, Any]:
        """Execute compensation steps for failed SAGA"""
        logger.info("=" * 80)
        logger.info(f"[SAGA COMPENSATION] 🔄 Starting compensation flow")
        logger.info(f"[SAGA COMPENSATION] Total compensation steps: {self.queue.get_compensation_count()}")
        logger.info("=" * 80)
        
        compensation_results = []
        successful = 0
        failed = 0
        
        while self.queue.compensation_queue:
            comp_step = self.queue.compensation_queue.popleft()
            original_step = comp_step['original_step']
            
            try:
                logger.info(f"[COMPENSATION] Executing: {comp_step['name']}")
                
                # Execute compensation logic
                comp_result = self._execute_compensation_step(
                    comp_step['name'],
                    original_step
                )
                
                if comp_result.get('success'):
                    logger.info(f"[COMPENSATION] ✅ {comp_step['name']} successful")
                    compensation_results.append({
                        'step': comp_step['name'],
                        'success': True,
                        'result': comp_result,
                        'original_step': original_step.step_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    successful += 1
                    
                    # Track in history
                    self.compensation_history.append({
                        'action': 'REVERSE',
                        'step': original_step.step_name,
                        'compensation_step': comp_step['name'],
                        'status': 'SUCCESS',
                        'details': comp_result,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    logger.error(f"[COMPENSATION] ❌ {comp_step['name']} failed")
                    compensation_results.append({
                        'step': comp_step['name'],
                        'success': False,
                        'error': comp_result.get('error', 'Unknown error'),
                        'original_step': original_step.step_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    failed += 1
                    
                    # Track in history
                    self.compensation_history.append({
                        'action': 'REVERSE',
                        'step': original_step.step_name,
                        'compensation_step': comp_step['name'],
                        'status': 'FAILED',
                        'error': comp_result.get('error', 'Unknown error'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"[COMPENSATION] Exception in {comp_step['name']}: {e}")
                compensation_results.append({
                    'step': comp_step['name'],
                    'success': False,
                    'error': str(e),
                    'original_step': original_step.step_name,
                    'timestamp': datetime.now().isoformat()
                })
                failed += 1
                
                # Track in history
                self.compensation_history.append({
                    'action': 'REVERSE',
                    'step': original_step.step_name,
                    'compensation_step': comp_step['name'],
                    'status': 'EXCEPTION',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        result = {
            'total_compensations': len(compensation_results),
            'successful_compensations': successful,
            'failed_compensations': failed,
            'results': compensation_results,
            'compensation_history': self.compensation_history
        }
        
        logger.info("=" * 80)
        logger.info(f"[COMPENSATION] Completed: {successful}/{len(compensation_results)} successful")
        logger.info("=" * 80)
        
        self._save_saga_log_entry("SAGA_COMPENSATION", result)
        return result
        
    def _execute_compensation_step(self, comp_name: str, original_step: SAGAStep) -> Dict[str, Any]:
        """Execute individual compensation step"""
        # Simulate compensation execution
        time.sleep(0.3)
        
        step_name = original_step.step_name
        
        if "RESERVE_SEAT" in step_name:
            logger.info("[COMPENSATE_RESERVE_SEAT] Canceling seat reservation...")
            return {
                'success': True,
                'step': comp_name,
                'message': 'Seat reservation canceled'
            }
            
        elif "DEDUCT_LOYALTY_POINTS" in step_name:
            logger.info("[COMPENSATE_DEDUCT_LOYALTY_POINTS] Refunding loyalty points...")
            return {
                'success': True,
                'step': comp_name,
                'message': 'Loyalty points refunded'
            }
            
        elif "PROCESS_PAYMENT" in step_name:
            logger.info("[COMPENSATE_PROCESS_PAYMENT] Refunding payment...")
            return {
                'success': True,
                'step': comp_name,
                'message': 'Payment refunded'
            }
            
        elif "CONFIRM_BOOKING" in step_name:
            logger.info("[COMPENSATE_CONFIRM_BOOKING] Canceling booking...")
            return {
                'success': True,
                'step': comp_name,
                'message': 'Booking canceled'
            }
        
        return {
            'success': False,
            'error': f'Unknown compensation step: {comp_name}'
        }
        
    def _save_saga_log_entry(self, event_type: str, data: Dict[str, Any]) -> None:
        """Save SAGA event to log"""
        try:
            log_entry = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'correlation_id': self.correlation_id,
                'data': data
            }
            
            self.saga_log.append(log_entry)
            
            # Also save to file
            with open('saga_bookings.log', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
            logger.debug(f"[LOG] Saved event: {event_type}")
            
        except Exception as e:
            logger.warning(f"[LOG] Failed to save log entry: {e}")
    
    def get_saga_status(self) -> Dict[str, Any]:
        """Get current SAGA status"""
        return {
            'correlation_id': self.correlation_id,
            'queue_status': self.queue.get_status_summary(),
            'log_entries': len(self.saga_log),
            'timestamp': datetime.now().isoformat()
        }
