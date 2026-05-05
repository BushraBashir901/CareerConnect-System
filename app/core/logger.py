import logging
import sys
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger("careerconnect")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _log_structured(self, level: str, event: str, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "name": "careerconnect",
            "event": event,
            **kwargs
        }
        self.logger.info(json.dumps(log_data))
    
    def info(self, event: str, **kwargs):
        self._log_structured("INFO", event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        self._log_structured("WARNING", event, **kwargs)
    
    def error(self, event: str, **kwargs):
        self._log_structured("ERROR", event, **kwargs)

# Global logger instance
logger = StructuredLogger()