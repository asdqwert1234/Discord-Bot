import datetime

# 時區設置 'Asia/Taipei'
tz = datetime.timezone(datetime.timedelta(hours = 8))
# 每日凌晨12點
DAILY_CLOCK = datetime.time(hour = 0, minute = 17, second = 0, tzinfo= tz)