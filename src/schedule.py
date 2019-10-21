import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools
from copy import deepcopy

import icalendar as ical
import datetime as dt
from scrapper import scrap_no_school_events
from text_parser import parse_schedule
from models import CalendarEvent, RegularEvent, ClassSection

from typing import List

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main(schedule: str):
    sections = [ClassSection(*s) for s in parse_schedule(schedule)]
    year, term = sections[0].get_year(), sections[0].get_term()
    no_school_events = [RegularEvent(**e) for e in scrap_no_school_events(year, term)]
    exdates = make_timeless_exdates(no_school_events)
    cal = ical.Calendar(summary=f"UCF {'Spring'} {'2020'}", timezone="America/New_York")
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
            dates += [event['dtstart'] + datetime.timedelta(i) for i in range(day_count + 1)]
        else:
            dates.append(event['dtstart'])
    return dates


def create_calendar(service, year, term):
    summary = f"UCF {term} {year}"
    if not TEST:
        return service.calendars().insert(body={"summary": summary, "timeZone": "America/New_York"}).execute()['id']
    else:
        return 0


def create_non_periodic_section(service, cal_id, section):
    dates: List[datetime.date] = section.pop("dates")
    dtstart: datetime.datetime = section.pop("dtstart")
    dtend: datetime.datetime = section.pop("dtend")

    for date in dates:
        event = dict(
            dtstart=dtstart.combine(date, dtstart.time(), dtstart.tzinfo),
            dtend=dtend.combine(date, dtend.time(), dtend.tzinfo),
        )
        event.update(**section)
        create_event(service, cal_id, event)


def create_event(event: CalendarEvent, timeless_exdates=None):
    ical_event = ical.Event()
    for name, value in event.items():
        ical_event.add(name, value)
    if timeless_exdates:
        start_time = ical_event['dtstart'].dt.time()
        exdates = [dt.datetime.combine(e, start_time) for e in timeless_exdates]
        ical_event.add("exdate", exdates)
    return ical_event


def get_calendar_service():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('calendar', 'v3', http=creds.authorize(Http()))


if __name__ == '__main__':
    with open("schedule (new).txt") as f:
        schedule = f.read()
    icalendar = main(schedule)
    with open("schedule.ics", "wb") as f2:
        print(icalendar.decode("UTF-8"))
        f2.write(icalendar)
