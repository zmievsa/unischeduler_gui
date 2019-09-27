import datetime
import pytz
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from icalendar import prop
from scrapper import scrap_no_school_events, scrap_term_dates
from text_parser import parse_schedule
TEST = True

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

TZ = pytz.timezone("America/New_York")
PATH_TO_SCHEDULE = "schedule.txt"

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main(year, term):
    start_date, end_date = get_term_interval(year, term)
    no_school_events = scrap_no_school_events(year, term)
    for event in no_school_events:
        set_real_no_school_datetimes(event)
    exdate = make_exdate_string_template(no_school_events)
    service = get_calendar_service()
    cal_id = create_calendar(service, year, term)
    sections = parse_schedule(PATH_TO_SCHEDULE)
    for section in sections:
        set_real_section_datetimes(section, start_date)
        make_rrule(section, end_date)
        make_exdate(section, exdate)
        create_event(service, cal_id, section)
    for event in no_school_events:
        create_event(service, cal_id, event)

    global TEST
    if TEST:
        answer = input("THIS WAS A TEST RUN. Do you want to do a real run now? (y/n): ")
        if answer.lower().startswith("y"):
            TEST = False
            main(year, term)


def get_term_interval(year, term):
    start_date_str, end_date_str = scrap_term_dates(year, term)
    return convert_to_date(start_date_str), convert_to_date(end_date_str)


def convert_to_date(string_date):
    return TZ.localize(datetime.datetime.strptime(string_date, "%Y-%m-%d"))


def set_real_no_school_datetimes(event):
    dtstart = convert_to_date(event.pop("raw_dtstart"))
    dtend = event.pop("raw_dtend")
    if dtend is None:
        dtend = (dtstart + datetime.timedelta(days=1))
    else:
        dtend = convert_to_date(dtend)
    if event["description"] is None:
        event.pop("description")
    event.update(dtstart=dtstart, dtend=dtend)


def make_exdate_string_template(no_school_events):
    dates = []
    for event in no_school_events:
        dtstart = event["dtstart"]
        dtend = event["dtend"]
        day_count = (dtend - dtstart).days
        if day_count > 1:
            dates += [dtstart + datetime.timedelta(i) for i in range(day_count + 1)]
        else:
            dates.append(dtstart)
    return "EXDATE;TZID=America/New_York:" + (",".join([datetime_to_ical(d) for d in dates]))


def create_calendar(service, year, term):
    summary = f"UCF {term} {year}"
    if not TEST:
        return service.calendars().insert(body={"summary": summary, "timeZone": "America/New_York"}).execute()['id']
    else:
        return 0


def set_real_section_datetimes(section, term_start_datetime):
    """ Before calling this method, the section only has times and weekdays but no real dates """
    weekday = get_closest_weekday(term_start_datetime, section.pop("weekday_ints"))
    start_time, end_time = section.pop("start_time"), section.pop("end_time")
    section["dtstart"] = weekday.replace(hour=start_time.hour, minute=start_time.minute)
    section["dtend"] = section["dtstart"].replace(hour=end_time.hour, minute=end_time.minute)


def make_rrule(section, final_date):
    weekdays = section.pop("weekday_strings")
    section["rrule"] = "RRULE:" + prop.vRecur(FREQ="WEEKLY", BYDAY=weekdays, UNTIL=final_date).to_ical().decode("UTF-8")


def make_exdate(section, exdate):
    section["exdate"] = exdate.replace("000000", section["dtstart"].strftime("%H%M%S"))


def datetime_to_ical(dt):
    return prop.vDatetime(dt).to_ical().decode("UTF-8")


def create_event(service, cal_id, event):
    rrule = event.pop("rrule", None)
    exdate = event.pop("exdate", None)
    event_body = {
        'start': {
            'dateTime': str(event.pop("dtstart")).replace(" ", "T"),
            'timeZone': "America/New_York"
        },
        'end': {
            'dateTime': str(event.pop("dtend")).replace(" ", "T"),
            'timeZone': "America/New_York"
        },
    }
    if rrule is not None:
        event_body['recurrence'] = [
            rrule.replace("0;", "0Z;"),
            exdate
        ]
    print(rrule, exdate, event_body)
    event_body.update(**event)
    if not TEST:
        service.events().insert(calendarId=cal_id, body=event_body).execute()
    print("Executed")


def get_closest_weekday(starting_datetime, needed_days, past=False):
    # Past means that we're searching the closest weekday in the past instead of the future
    starting_day = starting_datetime.weekday()
    possibilities = []
    for needed_day in needed_days:
        days_difference = (starting_day - needed_day) if past else (needed_day - starting_day)
        if days_difference < 0:  # Target day has (not) already happened this week
            days_difference += 7
        possibilities.append(days_difference)
    time_difference = datetime.timedelta(min(possibilities))
    if past:
        time_difference *= -1
    return starting_datetime + time_difference


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
    main(input("Year: "), input("Term (Fall, Spring): "))
