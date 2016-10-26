from datetime import datetime
from datetime import timedelta

import constants

def currentTime():
    return datetime.now() - timedelta(hours=constants.TZ_OFFSET)
