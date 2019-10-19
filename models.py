import datetime as dt
from typing import List
from icalendar import prop
import pytz

TIME_FORMAT = "%I:%M%p"
TZ = pytz.timezone("America/New_York")
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


class CalendarEvent:
    DATE_FORMAT = "%Y-%m-%d"
    summary: str
    start: dt.datetime
    end: dt.datetime
    options: dict

    def __init__(self, summary: str, dtstart: str, dtend: str, **options):
        self.summary = summary
        self.start = get_date(dtstart, self.DATE_FORMAT)
        if dtend is None:
            self.end = (self.start + dt.timedelta(days=1))
        else:
            self.end = get_date(dtend, self.DATE_FORMAT)
        self.options = options
    
    def to_ical(self):
        return dict(
            summary=self.summary,
            start=to_ical(self.start),
            end=to_ical(self.end),
            **self.options
        )


class Section(CalendarEvent):
    DATE_FORMAT = "%m/%d/%Y"
    location: str
    last_date: dt.datetime
    weekdays: List[str]

    def __init__(self, class_summary, section_type, weekdays: List[str], start_time, end_time, location, professors: List[str], dtstart: str, last_date, **options):
        self.options = options
        self.summary = f"{class_summary} ({section_type})"
        self.location = location
        self.weekdays = weekdays
        start_time, end_time = get_time(start_time), get_time(end_time)
        start, self.last_date = get_date(dtstart, self.DATE_FORMAT), get_date(last_date, self.DATE_FORMAT, UTC)
        weekday_ints = [WEEKDAYS[d] for d in self.weekdays]
        start = get_closest_weekday(start, weekday_ints)
        self.start = start.replace(hour=start_time.hour, minute=start_time.minute)
        self.end = start.replace(hour=end_time.hour, minute=end_time.minute)

    def to_ical(self) -> dict:
        return dict(
            location=self.location,
            rrule=self.get_rrule(),
            **super().to_ical()
        )

    def get_rrule(self):
        return "RRULE:" + to_str(prop.vRecur(FREQ="WEEKLY", BYDAY=self.weekdays, UNTIL=self.last_date))

    def get_exdate(self, exdate_template: str):
        return exdate_template.replace("000000", self.start.strftime("%H%M%S"))  # "000000" is an empty time on each exdate
    
    def get_year(self):
        return self.start.year
    
    def get_term(self):
        start_month = self.start.month
        if 8 <= start_month <= 10:
            return "Fall"
        elif 1 <= start_month <= 3:
            return "Spring"
        else:
            return "Summer"
        

def get_closest_weekday(starting_datetime, needed_days, past=False):
    # Past means that we're searching the closest weekday in the past instead of the future
    starting_day = starting_datetime.weekday()
    possibilities = []
    for needed_day in needed_days:
        days_difference = (starting_day - needed_day) if past else (needed_day - starting_day)
        if days_difference < 0:  # Target day has (not) already happened this week
            days_difference += 7
        possibilities.append(days_difference)
    time_difference = dt.timedelta(min(possibilities))
    if past:
        time_difference *= -1
    return starting_datetime + time_difference


def get_time(time_of_the_day: str) -> dt.time:   # 9:30AM
    return dt.datetime.strptime(time_of_the_day, TIME_FORMAT).time()


def get_date(date: str, format, timezone=TZ) -> dt.datetime:
    datetime = dt.datetime.strptime(date, format)
    return timezone.localize(datetime) if timezone else datetime


def to_ical(dt: dt.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
    # 1996-12-19T16:39:57-08:00


def to_str(ical_object):
    return ical_object.to_ical().decode("UTF-8")
