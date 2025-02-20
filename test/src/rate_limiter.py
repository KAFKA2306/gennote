from datetime import datetime
from config import RATE_LIMIT_CONFIG

class RateLimiter:
    def __init__(self):
        self.rate_limit = RATE_LIMIT_CONFIG['rate_limit']
        self.time_window = RATE_LIMIT_CONFIG['time_window']
        self.tokens = self.rate_limit
        self.last_update = datetime.now()

    def can_process(self) -> bool:
        now = datetime.now()
        time_passed = (now - self.last_update).total_seconds()
        self.tokens += time_passed * (self.rate_limit / self.time_window)
        self.tokens = min(self.tokens, self.rate_limit)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
