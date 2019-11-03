import re
from typing import List, Tuple, Union


def parse_schedule(schedule: str) -> List[Union[str, List[str]]]:
    schedule = "\n".join([l.strip()
                          for l in schedule.splitlines() if l.strip()])
    print(schedule)
    re_summary = re.compile(r"[A-Z]{3}[A-Z]* \d+[A-Z]? - .+")
    # Good luck figuring this out!
    re_details = re.compile(
        r"(?:[A-Z][a-z]+\n)?(?:[A-Z][a-z])+ \d\d?:\d\d(?:[A-Za-z:\-\s\d,])+.+")
    class_summaries = re_summary.findall(schedule)
    classes = re_summary.split(schedule)[1:]  # classes[0] == ''
    sections: List[Union[List[str], str]] = []
    for class_summary, class_info in zip(class_summaries, classes):
        if "Dropped" in class_info or "Online" in class_info or "Withdrawn" in class_info:
            continue
        current_sections = re_details.findall(class_info)
        for section in current_sections:
            lines = [l.strip() for l in section.splitlines() if l.strip()]
            if " - " not in lines[0]:  # If it's not a recurrence line
                section_type = last_type = lines.pop(0)
            else:
                section_type = last_type
            recurrence, location, *professors, dtstart_and_dtend = lines
            professors = [p.replace(",", "") for p in professors]
            start_time, end_time, weekdays = extract_time_attributes(
                recurrence)
            dtstart, _, dtend = dtstart_and_dtend.split(" ")
            sections.append([class_summary, section_type, weekdays,
                             start_time, end_time, location, professors, dtstart, dtend])
    return sections


# MoWeFr 9:30AM - 10:20AM
def extract_time_attributes(time_line: str) -> Tuple[str, str, List[str]]:
    weekdays_str, start_time, _, end_time = time_line.split(" ")
    weekdays = [weekdays_str[i:i + 2] for i in range(0, len(weekdays_str), 2)]
    return start_time, end_time, weekdays
