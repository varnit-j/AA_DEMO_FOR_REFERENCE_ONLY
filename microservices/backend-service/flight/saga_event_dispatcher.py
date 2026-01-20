"""
Simple Event Dispatcher for SAGA Pattern
Handles in-process event publishing and subscription
"""
import logging
import uuid
from typing import Dict, List, Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SagaEvent:
    """Represents a SAGA event"""
    def __init__(self, event_type: str, correlation_id: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.correlation_id = correlation_id
        self.data = data
        self.timestamp = datetime.now()
        self.event_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'correlation_id': self.correlation_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }

class EventDispatcher:
    """Simple in-process event dispatcher for SAGA orchestration"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[SagaEvent] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"[SAGA] Subscribed handler to event: {event_type}")
    
    def publish(self, event: SagaEvent):
        """Publish an event to all subscribers"""
        logger.info(f"[SAGA] Publishing event: {event.event_type} for correlation: {event.correlation_id}")
        
        # Store event in history
        self._event_history.append(event)
        
        # Notify subscribers
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"[SAGA] Error in event handler for {event.event_type}: {e}")
    
    def get_event_history(self, correlation_id: str = None) -> List[Dict]:
        """Get event history, optionally filtered by correlation ID"""
        if correlation_id:
            return [event.to_dict() for event in self._event_history 
                   if event.correlation_id == correlation_id]
        return [event.to_dict() for event in self._event_history]

# Global event dispatcher instance
event_dispatcher = EventDispatcher()