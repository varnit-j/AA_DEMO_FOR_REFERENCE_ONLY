#!/usr/bin/env python3
"""
Complete SAGA Implementation with Memory Queue and Sequential Steps
Implements the complete booking flow with proper logging and error handling
"""

import logging
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List
from collections import deque

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('saga_complete.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SAGAMemoryQueue:
    """Memory-based queue for SAGA step management"""
    
    def __init__(self):
        self.pending_steps = deque()
        self.completed_steps = []
        self.failed_steps = []
        self.compensation_queue = deque()
        
    def add_step(self, step_name: str, step_data: Dict[str, Any]):
        """Add a step to the pending queue"""
        step = {
            'name': step_name,
            'data': step_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'PENDING'
        }
        self.pending_steps.append(step)
        logger.info(f"[SAGA QUEUE] Added step: {step_name}")
        
    def get_next_step(self):
        """Get the next pending step"""
        if self.pending_steps:
            return self.pending_steps.popleft()
        return None
        
    def mark_completed(self, step: Dict[str, Any], result: Dict[str, Any]):
        """Mark a step as completed"""
        step['status'] = 'COMPLETED'
        step['result'] = result
        step['completed_at'] = datetime.now().isoformat()
        self.completed_steps.append(step)
        logger.info(f"[SAGA QUEUE] Completed step: {step['name']}")
        
    def mark_failed(self, step: Dict[str, Any], error: str):
        """Mark a step as failed and prepare compensation"""
        step['status'] = 'FAILED'
        step['error'] = error
        step['failed_at'] = datetime.now().isoformat()
        self.failed_steps.append(step)
        
        # Add compensation steps for all completed steps (in reverse order)
        for completed_step in reversed(self.completed_steps):
            compensation_step = {
                'name': f"COMPENSATE_{completed_step['name']}",
                'original_step': completed_step,
                'timestamp': datetime.now().isoformat(),
                'status': 'PENDING_COMPENSATION'
            }
            self.compensation_queue.append(compensation_step)
            
        logger.error(f"[SAGA QUEUE] Failed step: {step['name']} - {error}")
        logger.info(f"[SAGA QUEUE] Queued {len(self.compensation_queue)} compensation steps")

class CompleteSAGAOrchestrator:
    """Complete SAGA Orchestrator with sequential step execution"""
    
    def __init__(self):
        self.queue = SAGAMemoryQueue()
        self.correlation_id = None
        
    def start_booking_saga(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the complete SAGA booking process"""
        self.correlation_id = str(uuid.uuid4())
        logger.info(f"[SAGA] Starting booking SAGA with correlation_id: {self.correlation_id}")
        
        # Save booking data to file for debugging
        self._save_booking_log(booking_data)
        
        # Define SAGA steps in sequence
        saga_steps = [
            ("RESERVE_SEAT", {
                "url": "http://localhost:8001/api/saga/reserve-seat/",
                "compensation_url": "http://localhost:8001/api/saga/cancel-seat/"
            }),
            ("AUTHORIZE_PAYMENT", {
                "url": "http://localhost:8003/api/saga/authorize-payment/",
                "compensation_url": "http://localhost:8003/api/saga/cancel-payment/"
            }),
            ("AWARD_MILES", {
                "url": "http://localhost:8002/api/saga/award-miles/",
                "compensation_url": "http://localhost:8002/api/saga/reverse-miles/"
            }),
            ("CONFIRM_BOOKING", {
                "url": "http://localhost:8001/api/saga/confirm-booking/",
                "compensation_url": "http://localhost:8001/api/saga/cancel-booking/"
            })
        ]
        
        # Add all steps to the queue
        for step_name, step_config in saga_steps:
            step_data = {
                'correlation_id': self.correlation_id,
                'booking_data': booking_data,
                'step_config': step_config,
                'simulate_failure': booking_data.get(f'simulate_{step_name.lower()}_fail', False)
            }
            self.queue.add_step(step_name, step_data)
        
        # Execute steps sequentially
        return self._execute_saga_steps()
    
    def _execute_saga_steps(self) -> Dict[str, Any]:
        """Execute SAGA steps sequentially from the memory queue"""
        logger.info(f"[SAGA] Starting sequential execution of {len(self.queue.pending_steps)} steps")
        
        while True:
            step = self.queue.get_next_step()
            if not step:
                break
                
            logger.info(f"[SAGA] Executing step: {step['name']}")
            
            # Execute the step
            result = self._execute_single_step(step)
            
            if result.get('success'):
                self.queue.mark_completed(step, result)
                logger.info(f"[SAGA] ✅ Step {step['name']} completed successfully")
            else:
                self.queue.mark_failed(step, result.get('error', 'Unknown error'))
                logger.error(f"[SAGA] ❌ Step {step['name']} failed")
                
                # Execute compensation
                compensation_result = self._execute_compensation()
                
                return {
                    'success': False,
                    'correlation_id': self.correlation_id,
                    'failed_step': step['name'],
                    'error': result.get('error', 'Unknown error'),
                    'compensation_result': compensation_result,
                    'steps_completed': len(self.queue.completed_steps)
                }
            
            def _execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
                """Execute a single SAGA step with proper error handling"""
                import requests
                
                step_name = step['name']
                step_data = step['data']
                step_config = step_data['step_config']
                
                # Check for simulated failure
                if step_data.get('simulate_failure'):
                    logger.warning(f"[SAGA] Simulating failure for step: {step_name}")
                    return {
                        'success': False,
                        'error': f'Simulated failure for {step_name}'
                    }
                
                try:
                    # Prepare request data
                    request_data = {
                        'correlation_id': step_data['correlation_id'],
                        'booking_data': step_data['booking_data'],
                        'simulate_failure': step_data['simulate_failure']
                    }
                    
                    # Make HTTP request to the step endpoint
                    url = step_config['url']
                    logger.info(f"[SAGA] Calling {step_name} at {url}")
                    
                    response = requests.post(url, json=request_data, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"[SAGA] {step_name} response: {result}")
                        return result
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logger.error(f"[SAGA] {step_name} failed: {error_msg}")
                        return {
                            'success': False,
                            'error': error_msg
                        }
                
                def _execute_compensation(self) -> Dict[str, Any]:
                    """Execute compensation steps for failed SAGA"""
                    import requests
                    
                    logger.info(f"[SAGA COMPENSATION] Starting compensation for {len(self.queue.compensation_queue)} steps")
                    
                    compensation_results = []
                    
                    while self.queue.compensation_queue:
                        comp_step = self.queue.compensation_queue.popleft()
                        original_step = comp_step['original_step']
                        
                        try:
                            # Get compensation URL from original step config
                            step_config = original_step['data']['step_config']
                            compensation_url = step_config['compensation_url']
                            
                            logger.info(f"[SAGA COMPENSATION] Executing: {comp_step['name']}")
                            
                            # Prepare compensation request
                            comp_data = {
                                'correlation_id': self.correlation_id,
                                'compensation_reason': f"SAGA failure - rolling back {original_step['name']}"
                            }
                            
                            response = requests.post(compensation_url, json=comp_data, timeout=30)
                            
                            if response.status_code == 200:
                                result = response.json()
                                logger.info(f"[SAGA COMPENSATION] ✅ {comp_step['name']} successful")
                                compensation_results.append({
                                    'step': comp_step['name'],
                                    'success': True,
                                    'result': result
                                })
                            else:
                                logger.error(f"[SAGA COMPENSATION] ❌ {comp_step['name']} failed: HTTP {response.status_code}")
                                compensation_results.append({
                                    'step': comp_step['name'],
                                    'success': False,
                                    'error': f"HTTP {response.status_code}"
                                })
                                
                        except Exception as e:
                            logger.error(f"[SAGA COMPENSATION] Exception in {comp_step['name']}: {e}")
                            compensation_results.append({
                                'step': comp_step['name'],
                                'success': False,
                                'error': str(e)
                            })
                    
                    successful_compensations = len([r for r in compensation_results if r.get('success')])
                    logger.info(f"[SAGA COMPENSATION] Completed: {successful_compensations}/{len(compensation_results)} successful")
                    
                    return {
                        'total_compensations': len(compensation_results),
                        'successful_compensations': successful_compensations,
                        'results': compensation_results
                    }
                
                def _save_booking_log(self, booking_data: Dict[str, Any]):
                    """Save booking data to file for debugging"""
                    try:
                        log_entry = {
                            'correlation_id': self.correlation_id,
                            'timestamp': datetime.now().isoformat(),
                            'booking_data': booking_data
                        }
                        
                        with open('saga_bookings.log', 'a') as f:
                            f.write(json.dumps(log_entry) + '\n')
                            
                        logger.info(f"[SAGA] Saved booking log for {self.correlation_id}")
                        
                    except Exception as e:
                        logger.warning(f"[SAGA] Failed to save booking log: {e}")
            
            def test_complete_saga_flow():
                """Test the complete SAGA flow with a working flight"""
                logger.info("=" * 60)
                logger.info("STARTING COMPLETE SAGA FLOW TEST")
                logger.info("=" * 60)
                
                # Test data with working American Airlines flight
                booking_data = {
                    'flight_id': 37966,  # ORD to DFW American Airlines flight
                    'user_id': 1,
                    'passengers': [
                        {
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'gender': 'male'
                        }
                    ],
                    'contact_info': {
                        'email': 'john.doe@example.com',
                        'mobile': '+1234567890'
                    },
                    # Success scenario - no failure simulation
                    'simulate_reserve_seat_fail': False,
                    'simulate_authorize_payment_fail': False,
                    'simulate_award_miles_fail': False,
                    'simulate_confirm_booking_fail': False
                }
                
                # Create orchestrator and run SAGA
                orchestrator = CompleteSAGAOrchestrator()
                result = orchestrator.start_booking_saga(booking_data)
                
                # Log results
                logger.info("=" * 60)
                logger.info("SAGA FLOW TEST RESULTS")
                logger.info("=" * 60)
                logger.info(f"Success: {result.get('success')}")
                logger.info(f"Correlation ID: {result.get('correlation_id')}")
                logger.info(f"Steps Completed: {result.get('steps_completed')}")
                
                if result.get('success'):
                    logger.info(f"✅ SAGA COMPLETED SUCCESSFULLY!")
                    logger.info(f"Booking Reference: {result.get('booking_reference')}")
                else:
                    logger.error(f"❌ SAGA FAILED!")
                    logger.error(f"Failed Step: {result.get('failed_step')}")
                    logger.error(f"Error: {result.get('error')}")
                    logger.info(f"Compensation Result: {result.get('compensation_result')}")
                
                return result
            
            if __name__ == "__main__":
                test_complete_saga_flow()
                        
                except Exception as e:
                    error_msg = f"Exception in {step_name}: {str(e)}"
                    logger.error(f"[SAGA] {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg
                    }
        
        # All steps completed successfully
        logger.info(f"[SAGA] ✅ All {len(self.queue.completed_steps)} steps completed successfully")
        
        return {
            'success': True,
            'correlation_id': self.correlation_id,
            'message': 'SAGA booking completed successfully',
            'steps_completed': len(self.queue.completed_steps),
            'booking_reference': self.correlation_id[:8].upper()
        }