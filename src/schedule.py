import datetime as dt

import icalendar as ical

from models import CalendarEvent, ClassSection, RegularEvent
from scrapper import scrap_no_school_events
from text_parser import parse_schedule

from util import SchedulerError

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main(schedule: str):
    if not schedule.strip():
        raise SchedulerError("You inputted an empty schedule.")
    sections = [ClassSection(*s) for s in parse_schedule(schedule)]
    if not sections:
        raise SchedulerError("Something's weird about your schedule. Contact my author")
    year, term = sections[0].get_year(), sections[0].get_term()
    no_school_events = [RegularEvent(**e)
                        for e in scrap_no_school_events(year, term)]
    exdates = make_timeless_exdates(no_school_events)
    cal = ical.Calendar(
        summary=f"UCF {'Spring'} {'2020'}", timezone="America/New_York")
    for section in sections:
        cal.add_component(create_event(section, exdates))
    for event in no_school_events:
        cal.add_component(create_event(event))
    return cal.to_ical()


def make_timeless_exdates(no_school_events):
    dates = []
    for event in no_school_events:
        day_count = (event['dtend'] - event['dtstart']).days
        if day_count > 1:
            dates += [event['dtstart'] +
                      dt.timedelta(i) for i in range(day_count + 1)]
        else:
            dates.append(event['dtstart'])
    return dates


def create_event(event: CalendarEvent, timeless_exdates=None):
    ical_event = ical.Event()
    for name, value in event.items():
        ical_event.add(name, value)
    if timeless_exdates:
        start_time = ical_event['dtstart'].dt.time()
        exdates = [dt.datetime.combine(e, start_time)
                   for e in timeless_exdates]
        ical_event.add("exdate", exdates)
    return ical_event


if __name__ == '__main__':
    from pathlib import Path
    folder = Path(__file__).parent.resolve()
    with open(folder / "schedule.txt") as f:
        icalendar = main(f.read())
    with open(folder / "schedule.ics", "wb") as f2:
        print(icalendar.decode("UTF-8"))
        f2.write(icalendar)
