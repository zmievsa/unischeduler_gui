import requests
from bs4 import BeautifulSoup


def scrap_term_dates(year, term):
    url = f"https://calendar.ucf.edu/{year}/{term}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = soup.find_all("h2", {"class": "mt-3 mb-2"})
    for title in titles:
        if title.get_text().startswith("Academic Dates and Deadlines"):
            deadline_table = title.find_next_sibling("table")
    for elem in deadline_table.find_all("tr"):
        summary = elem.find("span", {"class": "summary"})
        if summary is not None:
            if summary.get_text().startswith("Classes Begin"):
                start_date = elem.find("abbr", {"class": "dtstart"})['title']
            elif summary.get_text().startswith("Classes End"):
                end_date = elem.find("abbr", {"class": "dtstart"})['title']
    return start_date, end_date


def scrap_no_school_events(year, term):
    url = f"https://calendar.ucf.edu/{year}/{term}/no-classes/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    raw_events = soup.find_all("tr", {"class": "vevent"})
    scrapped_events = []
    for event in raw_events:
        dtstart = dtend = description = None
        for elem in event.find_all("abbr"):
            class_ = elem['class'] if isinstance(elem['class'], str) else elem['class'][0]
            if class_ == "dtstart":
                dtstart = elem['title']
            elif class_ == "dtend":
                dtend = elem['title']
        raw_description = event.find("div", {"class": "more-details"})
        if raw_description is not None:
            description = raw_description.get_text().strip()
        if dtstart is None:
            # Sometimes it has an event with no dtstart and no dtend.
            # I would check back on it later (UCF Cal -> no-school tag -> Study day)
            continue
        scrapped_events.append(dict(
            summary=event.find("span", {"class": "summary"}).get_text(),
            dtstart=dtstart,
            dtend=dtend
        ))
        if description:
            scrapped_events[-1]['description'] = description
    return scrapped_events
