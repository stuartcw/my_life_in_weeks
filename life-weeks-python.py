#!python3

from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlite3
from jinja2 import Environment, FileSystemLoader, select_autoescape


@dataclass
class Event:
    date: date
    headline: str
    description: str
    based: str
    doing: str
    association: Optional[str] = None


@dataclass
class Style:
    type: str
    name: str
    class_name: str
    bg_color: str
    border_color: str
    text_color: str = "#000000"


class LifeWeeksGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.env = Environment(
            loader=FileSystemLoader("."),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_datetime(value):
            if isinstance(value, str):
                return datetime.strptime(value, "%Y-%m-%d")
            return value

        def safe_strftime(value, fmt):
            if isinstance(value, str):
                value = datetime.strptime(value, "%Y-%m-%d")
            return value.strftime(fmt)

        self.env.filters["to_datetime"] = to_datetime
        self.env.filters["strftime"] = safe_strftime

    def get_events(self) -> Dict[str, List[Event]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        events = {}
        for row in c.execute(
            "SELECT date, headline, description, based, doing, association FROM events ORDER BY date"
        ):
            event = Event(
                date=datetime.strptime(row[0], "%Y-%m-%d").date(),
                headline=row[1],
                description=row[2],
                based=row[3],
                doing=row[4],
                association=row[5],
            )
            date_str = event.date.strftime("%Y-%m-%d")
            if date_str not in events:
                events[date_str] = []
            events[date_str].append(event)
        conn.close()
        return events

    def get_styles(self) -> List[Style]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        styles = []
        for row in c.execute(
            "SELECT type, name, class_name, bg_color, border_color FROM current_styles"
        ):
            styles.append(
                Style(
                    type=row[0],
                    name=row[1],
                    class_name=row[2],
                    bg_color=row[3],
                    border_color=row[4],
                )
            )
        conn.close()
        return styles

    def get_settings(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        settings = {}

        # Get earliest event date as start_date if not specified
        c.execute("SELECT MIN(date) FROM events")
        start_date = c.fetchone()[0]
        if start_date:
            settings["start_date"] = datetime.strptime(start_date, "%Y-%m-%d").date()

        # Get latest style end_date as end_year
        c.execute("SELECT MAX(end_date) FROM styles")
        end_date = c.fetchone()[0]
        if end_date and end_date != "9999-12-31":
            settings["end_year"] = datetime.strptime(end_date, "%Y-%m-%d").date().year
        else:
            settings["end_year"] = date.today().year + 1

        conn.close()
        return settings

    def generate_html(self) -> str:
        template = self.env.get_template("life_weeks_template.html")
        events = self.get_events()
        styles = self.get_styles()
        settings = self.get_settings()

        # Get initial based/doing values from first event
        initial_based = "Unknown"
        initial_doing = "Unknown"
        if events:
            first_event = next(iter(events.values()))[0]
            initial_based = first_event.based
            initial_doing = first_event.doing

        return template.render(
            start_year=settings["start_date"].year,
            start_month=settings["start_date"].month,
            start_day=settings["start_date"].day,
            end_year=settings["end_year"],
            events=events,
            colors=styles,
            based=initial_based,
            doing=initial_doing,
            based_class=initial_based.lower().replace(" ", "-"),
            doing_class=initial_doing.lower().replace(" ", "-"),
            association="",
            timedelta=timedelta,
        )


def main():
    generator = LifeWeeksGenerator("life_events.db")
    html = generator.generate_html()

    with open("life_weeks.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
