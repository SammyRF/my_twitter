from datetime import datetime
import pytz

class time_helpers:

    @classmethod
    def utc_now(cls):
        return datetime.now().replace(tzinfo=pytz.utc)