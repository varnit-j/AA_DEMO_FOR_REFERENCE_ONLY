"""
SAGA Log Storage System
Centralized logging for SAGA execution steps and compensation
"""
import logging
from typing import Dict, Any, List
from django.utils import timezone
import pytz

logger = logging.getLogger(__name__)

class SagaLogEntry:
    def __init__(self, correlation_id: str, step_name: str, service: str,
                 log_level: str, message: str, is_compensation: bool = False, timestamp=None):
        self.correlation_id = correlation_id
        self.step_name = step_name
        self.service = service
        self.log_level = log_level
        self.message = message
        self.is_compensation = is_compensation
        self.timestamp = timestamp or timezone.now()
    
    def to_dict(self):
        return {
            'correlation_id': self.correlation_id,
            'step_name': self.step_name,
            'service': self.service,
            'log_level': self.log_level,
            'message': self.message,
            'timestamp': self.timestamp.astimezone(pytz.timezone('Asia/Calcutta')).strftime('%H:%M:%S IST'),
            'timestamp_utc': self.timestamp.strftime('%H:%M:%S UTC'),
            'timestamp_full': self.timestamp.astimezone(pytz.timezone('Asia/Calcutta')).strftime('%Y-%m-%d %H:%M:%S IST'),
            'is_compensation': self.is_compensation
        }

class SagaLogStorage:
    """Centralized storage for SAGA execution logs"""
    
    def __init__(self):
        self.logs = {}  # correlation_id -> list of log entries
    
    def add_log(self, correlation_id: str, step_name: str, service: str,
                log_level: str, message: str, is_compensation: bool = False):
        """Add a log entry for a SAGA transaction"""
        if correlation_id not in self.logs:
            self.logs[correlation_id] = []
        
        log_entry = SagaLogEntry(correlation_id, step_name, service, log_level, message, is_compensation)
        self.logs[correlation_id].append(log_entry)
        
        logger.info(f"[SAGA LOG] {service} - {step_name}: {message}")
        logger.debug(f"[SAGA DEBUG] Log added for correlation_id={correlation_id}, total_logs={len(self.logs[correlation_id])}")
        logger.debug(f"[SAGA DEBUG] Log added for correlation_id={correlation_id}, total_logs={len(self.logs[correlation_id])}")
    
    def get_logs(self, correlation_id: str, include_compensation: bool = True) -> List[Dict[str, Any]]:
        """Get all logs for a SAGA transaction"""
        if correlation_id not in self.logs:
            logger.debug(f"[SAGA DEBUG] No logs found for correlation_id={correlation_id}")
            logger.debug(f"[SAGA DEBUG] No logs found for correlation_id={correlation_id}")
            return []
        
        logs = [
            log.to_dict() for log in self.logs[correlation_id]
            if include_compensation or not log.is_compensation
        ]
        logger.debug(f"[SAGA DEBUG] Retrieved {len(logs)} logs for correlation_id={correlation_id}")
        return logs
    
    def clear_logs(self, correlation_id: str):
        """Clear logs for a completed SAGA transaction"""
        if correlation_id in self.logs:
            del self.logs[correlation_id]

# Global instance
saga_log_storage = SagaLogStorage()
