import datetime
from typing import List, Tuple


TIME_FORMAT = "%I:%M%p"
WEEKDAYS = {
    "Mo": 0,
    "Tu": 1,
    "We": 2,
    "Th": 3,
    "Fr": 4,
    "Sa": 5,
    "Su": 6
}


def parse_schedule(path: str):
    """ Parses a given file returning a list of section instances """
    with open(path) as f:
        lines = f.readlines()
    sections = []
    n = 0  # Line counter
    while (len(lines) > n):
        if not lines[n + 2].startswith("Online"):  # Skip online classes
            title_line, type_line, time_line, location_line = [line.strip() for line in lines[n:n + 4]]
            start_time, end_time, weekday_strings = extract_time_attributes(time_line)
            sections.append(dict(
                summary=extract_summary(title_line, type_line),
                start_time=extract_time_of_the_day(start_time),
                end_time=extract_time_of_the_day(end_time),
                weekday_strings=weekday_strings,
                weekday_ints=[WEEKDAYS[d] for d in weekday_strings],
                dates=[],
                location=location_line.replace("    ", " ").replace("  ", " ")))
            n += 4
        else:
            n += 3  # Online classes have only 3 lines
    return sections


def extract_summary(title_line: str, type_line: str):  # COP 3502 (LEC)
    return f"{title_line[0:8]} ({type_line[0:3]})"


def extract_time_attributes(time_line: str) -> Tuple[str, str, List[str]]:  # MoWeFr 9:30AM - 10:20AM
    weekdays_str, start_time, _, end_time = time_line.split(" ")
    weekdays = [weekdays_str[i:i + 2] for i in range(0, len(weekdays_str), 2)]
    return start_time, end_time, weekdays


def extract_time_of_the_day(time_of_the_day: str) -> datetime.time:  # 9:30AM
    return datetime.datetime.strptime(time_of_the_day, TIME_FORMAT).time()
