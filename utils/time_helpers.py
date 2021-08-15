from datetime import datetime
import pytz

class TimeHelpers:

    @classmethod
    def utc_now(cls):
        return datetime.now().replace(tzinfo=pytz.utc)


