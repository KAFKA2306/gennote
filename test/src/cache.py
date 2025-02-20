from datetime import datetime
from typing import Dict, Optional
from config import CACHE_CONFIG

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.cache_duration = CACHE_CONFIG['duration']

    def get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_duration:
                return data
            del self.cache[key]
        return None

    def set(self, key: str, value: Dict):
        self.cache[key] = (value, datetime.now())
