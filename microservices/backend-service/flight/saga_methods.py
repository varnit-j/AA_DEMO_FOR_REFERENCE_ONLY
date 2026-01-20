
"""
Additional methods for SAGA Orchestrator
"""

def execute_step_method(self, step, step_data):
    """Execute a single SAGA step"""
    try:
        logger.info(f"[SAGA] Calling {step.action_url} with data: {step_data}")
        
        response = requests.post(
            step.action_url,
            json=step_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"[SAGA] Request error for step {step.name}: {e}")
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"[SAGA] Unexpected error in step {step.name}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def execute_compensation_method(self, completed_steps, correlation_id, booking_data):
    """Execute compensation for completed steps in reverse order"""
    logger.info(f"[SAGA] Starting compensation for {len(completed_steps)} completed steps")
    
    compensation_results = []
    
    # Execute compensation in reverse order
    for step in reversed(completed_steps):
        logger.info(f"[SAGA] Executing compensation for step: {step.name}")
        
        compensation_data = {
            "correlation_id": correlation_id,
            "booking_data": booking_data,
            "step_name": step.name
        }
        
        try:
            response = requests.post(
                step.compensation_url,
                json=compensation_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                compensation_results.append({
                    "step": step.name,
                    "success": True,
                    "result": result
                })
                logger.info(f"[SAGA] Compensation for {step.name} completed successfully")
            else:
                compensation_results.append({
                    "step": step.name,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                logger.error(f"[SAGA] Compensation for {step.name} failed")
                
        except Exception as e:
            compensation_results.append({
                "step": step.name,
                "success": False,
                "error": str(e)
            })
            logger.error(f"[SAGA] Compensation error for {step.name}: {e}")
    
    return {
        "compensation_completed": True,
        "results": compensation_results
    }

def handle_step_failure_method(self, event):
    """Handle step failure events"""
    logger.info(f"[SAGA] Handling step failure event: {event.to_dict()}")

def handle_compensation_failure_method(self, event):
    """Handle compensation failure events"""
    logger.error(f"[SAGA] Compensation failure event: {event.to_dict()}")

def get_saga_status_method(self, correlation_id):
    """Get SAGA status by correlation ID"""
    events = event_dispatcher.get_event_history(correlation_id)
    
    if not events:
        return {"error": "SAGA not found"}
    
    # Determine current status
    