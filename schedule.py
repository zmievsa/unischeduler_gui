import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from scrapper import scrap_no_school_events
from text_parser import parse_schedule
from models import CalendarEvent, Section, to_ical, ICAL_TIMELESS_DATETIME_FORMAT

from typing import List

TEST = False

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main(schedule: str):
    sections = [Section(*s) for s in parse_schedule(schedule)]
    year, term = sections[0].get_year(), sections[0].get_term()
    no_school_events = [CalendarEvent(**e) for e in scrap_no_school_events(year, term)]
    exdate = make_exdate_string_template(no_school_events)
    service = get_calendar_service()
    cal_id = create_calendar(service, year, term)
    for section in sections:
        create_event(service, cal_id, section.to_ical(exdate))
    for event in no_school_events:
        create_event(service, cal_id, event.to_ical())

    global TEST
    if TEST and __name__ == "__main__":
        answer = input("\nTHIS WAS A TEST RUN. Do you want to do a real run now? (y/n): ")
        if answer.strip().lower().startswith("y"):
            TEST = False
            main(schedule)


def make_exdate_string_template(no_school_events):
    dates = []
    for event in no_school_events:
        day_count = (event.end - event.start).days
        if day_count > 1:
            dates += [event.start + datetime.timedelta(i) for i in range(day_count + 1)]
        else:
            dates.append(event.start)
    return "EXDATE;TZID=America/New_York:" + (",".join([to_ical(d, ICAL_TIMELESS_DATETIME_FORMAT) for d in dates]))


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


def create_event(service, cal_id, event):
    print(event)
    rrule = event.pop("rrule", None)
    exdate = event.pop("exdate", None)
    start, end = event.pop('start'), event.pop('end')
    event_body = {
        'start': {
            'dateTime': start,
            'timeZone': 'America/New_York'
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/New_York'
        },
    }
    if rrule is not None:
        event_body['recurrence'] = [
            rrule,
            exdate
        ]
    event_body.update(**event)
    if not TEST:
        service.events().insert(calendarId=cal_id, body=event_body).execute()
    print("Executed")


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
    TEST = True
    with open("schedule (new).txt") as f:
        schedule = f.read()
    main(schedule)
