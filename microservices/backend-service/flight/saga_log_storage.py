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
        """Add a log entry for a SAGA transaction - now persisted to database"""
        try:
            # Import here to avoid circular imports
            from .models import SagaLogEntry as SagaLogModel
            
            # Create database record
            log_entry = SagaLogModel.objects.create(
                correlation_id=correlation_id,
                step_name=step_name,
                service=service,
                log_level=log_level,
                message=message,
                is_compensation=is_compensation
            )
            
            # Enhanced logging with compensation indicator
            comp_indicator = " [COMPENSATION]" if is_compensation else ""
            logger.info(f"[SAGA LOG DB] {service} - {step_name}{comp_indicator}: {message}")
            logger.info(f"[SAGA LOG DB] ✅ Persisted log entry ID {log_entry.id} to database")
            
            # BACKWARD COMPATIBILITY: Also store in memory for immediate access
            if correlation_id not in self.logs:
                self.logs[correlation_id] = []
            
            # Create in-memory entry for backward compatibility
            memory_entry = SagaLogEntry(correlation_id, step_name, service, log_level, message, is_compensation)
            self.logs[correlation_id].append(memory_entry)
            
        except Exception as e:
            logger.error(f"[SAGA LOG DB] ❌ Failed to persist log to database: {e}")
            # Fallback to memory-only storage
            if correlation_id not in self.logs:
                self.logs[correlation_id] = []
            
            log_entry = SagaLogEntry(correlation_id, step_name, service, log_level, message, is_compensation)
            self.logs[correlation_id].append(log_entry)
            
            comp_indicator = " [COMPENSATION]" if is_compensation else ""
            logger.info(f"[SAGA LOG FALLBACK] {service} - {step_name}{comp_indicator}: {message}")
    
    def get_logs(self, correlation_id: str, include_compensation: bool = True) -> List[Dict[str, Any]]:
        """Get all logs for a SAGA transaction - now from database with fallback"""
        logger.info(f"[SAGA LOG DB] ===== GET_LOGS REQUEST =====")
        logger.info(f"[SAGA LOG DB] Requested correlation_id: {correlation_id}")
        
        try:
            # Try database first
            from .models import SagaLogEntry as SagaLogModel
            
            query = SagaLogModel.objects.filter(correlation_id=correlation_id)
            if not include_compensation:
                query = query.filter(is_compensation=False)
            
            db_logs = query.order_by('timestamp')
            logs = [log.to_dict() for log in db_logs]
            
            if logs:
                logger.info(f"[SAGA LOG DB] ✅ Found {len(logs)} logs in database")
                return logs
            else:
                logger.warning(f"[SAGA LOG DB] ❌ No logs in database for {correlation_id}")
                
        except Exception as e:
            logger.error(f"[SAGA LOG DB] Database query failed: {e}")
        
        # Fallback to memory storage
        logger.info(f"[SAGA LOG DB] Falling back to memory storage")
        if correlation_id not in self.logs:
            logger.warning(f"[SAGA LOG DB] ❌ Not found in memory either: {correlation_id}")
            return []
        
        logs = [
            log.to_dict() for log in self.logs[correlation_id]
            if include_compensation or not log.is_compensation
        ]
        logger.info(f"[SAGA LOG DB] ✅ Found {len(logs)} logs in memory")
        return logs
    
    def clear_logs(self, correlation_id: str):
        """Clear logs for a completed SAGA transaction"""
        if correlation_id in self.logs:
            del self.logs[correlation_id]

# Global instance
saga_log_storage = SagaLogStorage()
