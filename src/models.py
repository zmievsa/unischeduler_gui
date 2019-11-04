import datetime as dt
from typing import List, Union

import pytz
from icalendar import prop

from util import SchedulerError, TIMEZONE

TIME_FORMAT = "%I:%M%p"
ICAL_TIME_FORMAT = "%H%M%S"
# Created for cases when we have a date for something but not the time yet
ICAL_TIMELESS_DATETIME_FORMAT = "%Y%m%dT{time}"
ICAL_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
TZ = pytz.timezone(TIMEZONE)
UTC = pytz.timezone("UTC")
WEEKDAYS = {
    "Mo": 0,
    "Tu": 1,
    "We": 2,
    "Th": 3,
    "Fr": 4,
    "Sa": 5,
    "Su": 6
}


class CalendarEvent(dict):
    """
    Necessary keys:
    dtstart: datetime
    dtend: datetime
    summary: str

    """
    pass


class RegularEvent(CalendarEvent):
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, summary: str, raw_dtstart: str, raw_dtend: str, *args, **kwargs):
        start = get_date(raw_dtstart, self.DATE_FORMAT, UTC).date()
        if raw_dtend is None:
            end = (start + dt.timedelta(days=1))
        else:
            end = get_date(raw_dtend, self.DATE_FORMAT, UTC).date()
        super().__init__(dtstart=start, dtend=end, summary=summary)


class ClassSection(CalendarEvent):
    DATE_FORMATS = ["%m/%d/%Y", "%Y/%m/%d", "%d/%m/%Y"]  # Trust me with this

    def __init__(self, class_summary, section_type, weekdays: List[str], start_time, end_time, location, professors: List[str], dtstart, last_date, **kwargs):
        summary = f"{class_summary} ({section_type})"
        start_time, end_time = get_time(start_time), get_time(end_time)
        start, last_date = get_date(dtstart, self.DATE_FORMATS), get_date(
            last_date, self.DATE_FORMATS, UTC)
        start = get_closest_weekday(start, weekdays)
        dtstart = dt.datetime.combine(start, start_time)
        dtend = dt.datetime.combine(start, end_time)
        rrule = prop.vRecur(FREQ="WEEKLY", BYDAY=weekdays, UNTIL=last_date)
        super().__init__(dtstart=dtstart, dtend=dtend,
                         rrule=rrule, summary=summary, location=location)

    def get_year(self):
        return self['dtstart'].year

    def get_term(self):
        start_month = self['dtstart'].month
        if 8 <= start_month <= 10:
            return "Fall"
        elif 1 <= start_month <= 3:
            return "Spring"
        else:
            return "Summer"


def get_date(date: str, format: Union[List[str], str], timezone=TZ) -> dt.datetime:
    formats = [format] if type(format) is str else format
    for fmt in formats:
        try:
            datetime = dt.datetime.strptime(date, fmt)
        except ValueError as e:
            err = e
        else:
            return timezone.localize(datetime) if timezone else datetime
    else:
        raise SchedulerError("Something's weird about your schedule. Ask my author for help.") from err


def get_time(time_of_the_day: str) -> dt.time:   # 9:30AM
    return dt.datetime.strptime(time_of_the_day, TIME_FORMAT).time()


def get_closest_weekday(starting_datetime, needed_days, past=False):
    # Past means that we're searching the closest weekday in the past instead of the future
    needed_days = [WEEKDAYS[d] for d in needed_days]
    starting_day = starting_datetime.weekday()
    possibilities = []
    for needed_day in needed_days:
        days_difference = (
            starting_day - needed_day) if past else (needed_day - starting_day)
        # Target day has (not) already happened this week
        if days_difference < 0:
            days_difference += 7
        possibilities.append(days_difference)
    time_difference = dt.timedelta(min(possibilities))
    if past:
        time_difference *= -1
    return starting_datetime + time_difference


def to_str(ical_object):
    return ical_object.to_ical().decode("UTF-8")
