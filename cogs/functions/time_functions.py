import datetime
from data.time_parameters import DAILY_CLOCK, tz

# 確認現在時間是否相同 
def check_times_up() -> bool :
    now = datetime.datetime.now().time().replace(tzinfo = tz)
    return True if (now.hour == DAILY_CLOCK.hour) and (now.minute == DAILY_CLOCK.minute) else False