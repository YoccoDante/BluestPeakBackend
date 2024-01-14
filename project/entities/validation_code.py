from datetime import datetime

class ValidationCode:
    def __init__(self, _id, code, email, duration=None, timestamp=None, attempts=None):
        self._id = _id
        self.code = code
        self.email = email
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.attempts = attempts if attempts is not None else 0