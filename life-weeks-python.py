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

    def get_events(self) -> List[Event]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        events = []

        # Get regular events
        for row in c.execute(
            "SELECT date, headline, description, based, doing, association FROM events ORDER BY date"
        ):
            events.append(
                Event(
                    date=datetime.strptime(row[0], "%Y-%m-%d").date(),
                    headline=row[1],
                    description=row[2],
                    based=row[3],
                    doing=row[4],
                    association=row[5],
                )
            )

        conn.close()

        # Add birthday events
        settings = self.get_settings()
        start_date = settings["start_date"]
        for year in range(start_date.year, settings["end_year"] + 1):
            birthday = date(year, start_date.month, start_date.day)
            age = year - start_date.year
            if age >= 0:  # Only add birthdays from birth year onwards
                events.append(
                    Event(
                        date=birthday,
                        headline=f"🎂 {age} in {year}",
                        description=f"Turned {age} year{'s' if age != 1 else ''} old",
                        based=(
                            events[0].based if events else "Unknown"
                        ),  # Use the location from first event
                        doing=(
                            events[0].doing if events else "Unknown"
                        ),  # Use the activity from first event
                    )
                )

        # Sort all events by date
        events.sort(key=lambda x: x.date)
        return events

    def get_week_events(self, week_start: date, events: List[Event]) -> List[Event]:
        week_end = week_start + timedelta(days=6)
        return [event for event in events if week_start <= event.date <= week_end]

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

        c.execute("SELECT MIN(date) FROM events")
        start_date = c.fetchone()[0]
        if start_date:
            settings["start_date"] = datetime.strptime(start_date, "%Y-%m-%d").date()

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

        start_date = settings["start_date"]
        weeks_data = []

        # Calculate all weeks
        current_date = start_date
        while current_date.year <= settings["end_year"]:
            week_events = self.get_week_events(current_date, events)

            # Sort birthday events first
            week_events.sort(key=lambda x: (not x.headline.startswith("🎂"), x.date))

            weeks_data.append(
                {
                    "start_date": current_date,
                    "events": week_events,
                    "age": (current_date.year - start_date.year),
                }
            )
            current_date += timedelta(days=7)

        # Get initial based/doing values
        initial_based = "Unknown"
        initial_doing = "Unknown"
        if events:
            initial_based = events[0].based
            initial_doing = events[0].doing

        return template.render(
            weeks=weeks_data,
            colors=styles,
            based=initial_based,
            doing=initial_doing,
            based_class=initial_based.lower().replace(" ", "-"),
            doing_class=initial_doing.lower().replace(" ", "-"),
            association="",
        )


def main():
    generator = LifeWeeksGenerator("life_events.db")
    html = generator.generate_html()

    with open("life_weeks.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
