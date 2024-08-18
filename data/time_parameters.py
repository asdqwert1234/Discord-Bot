import datetime

# 時區設置 'Asia/Taipei'
tz = datetime.timezone(datetime.timedelta(hours = 8))
# 每日凌晨12點
DAILY_CLOCK = datetime.time(hour = 1, minute = 49, second = 0, tzinfo= tz)