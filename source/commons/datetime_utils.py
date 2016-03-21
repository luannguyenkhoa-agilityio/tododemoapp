from django.conf import settings
import pytz
from datetime import datetime, date


def get_current_weekday(timezone=None):
    """
    Get current weekday with timezone.
    @timezone: Timezone is string
    """
    nytz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    u = datetime.utcnow().replace(tzinfo=pytz.utc)
    currenttime = nytz.normalize(u)
    return currenttime.strftime("%a")


def get_current_time(timezone=None):
    """
    Get current time with timezone.
    @timezone: Timezone is string
    """
    nytz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    u = datetime.utcnow().replace(tzinfo=pytz.utc)
    currenttime = nytz.normalize(u)
    return currenttime.strftime("%H:%M:%S")


def get_current_date(timezone=None):
    """
    Get current date with timezone.
    @timezone: Timezone is string
    """
    nytz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    u = datetime.utcnow().replace(tzinfo=pytz.utc)
    return nytz.normalize(u)


def get_second_offset(time):
    """
    Get second offset from time
    @time: Python time object in 24 hour format
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def get_client_timezone(request=None):
    """
    Get client timezone by parsing parameter.
    Currently this function always return New York timezone
    """
    return settings.DEFAULT_TIMEZONE


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def convert_to_date(date):
    return datetime.strptime(date, '%B %d, %Y')


def current_date_with_format():
    return "%B %d, %Y".format(date.today())


def convert_to_string(date):
    return date.strftime('%B %d, %Y')


def compare_two_dates_string(date, range):
    date1 = datetime.strptime(date, '%B %d %Y')
    date2 = datetime.now().strptime('%B %d %Y')
    if date1 == date2 and compare_two_times_string(range=range) is False:
        return False
    return True


def compare_two_times_string(range):
    current_time = get_current_time()
    components = range.strip().split(" - ")
    if components.count < 2:
        return False
    convert_first = datetime.strptime(components[0], "%I:%M %p")
    convert_sec = datetime.strptime(components[-1], "%I:%M %p")
    return time_in_range(convert_first, convert_sec, current_time)
