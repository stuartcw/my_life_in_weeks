#!/usr/bin/env python3
import sqlite_utils
import csv
from datetime import datetime
import yaml
import click

def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d').date()

@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.argument('settings_file', type=click.Path(exists=True))
@click.argument('db_file', type=click.Path())
def create_database(csv_file, settings_file, db_file):
    """Create a SQLite database from CSV events and YAML settings."""
    db = sqlite_utils.Database(db_file)
    
    # Create events table
    if "events" not in db.table_names():
        db["events"].create({
            "id": int,
            "date": str,
            "headline": str,
            "description": str,
            "based": str,
            "doing": str,
            "association": str
        }, pk="id")
        db["events"].create_index(["date"])

    # Create styles table for color schemes
    if "styles" not in db.table_names():
        db["styles"].create({
            "id": int,
            "type": str,  # 'location' or 'activity'
            "name": str,
            "class_name": str,
            "bg_color": str,
            "border_color": str,
            "start_date": str,
            "end_date": str
        }, pk="id")
        db["styles"].create_index(["type", "start_date"])

    # Import events from CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        events = []
        for row in reader:
            events.append({
                "date": row["date"],
                "headline": row["headline"],
                "description": row["description"],
                "based": row["based"],
                "doing": row["doing"],
                "association": row["association"]
            })
    
    if events:
        db["events"].insert_all(events)

    # Import styles from YAML
    with open(settings_file, 'r') as f:
        settings = yaml.safe_load(f)
        
        styles = []
        # Process location styles
        for loc in settings.get('locations', []):
            styles.append({
                "type": "location",
                "name": loc["name"],
                "class_name": loc["class_name"],
                "bg_color": loc["bg_color"],
                "border_color": loc["border_color"],
                "start_date": loc["start_date"],
                "end_date": loc["end_date"] or "9999-12-31"
            })
        
        # Process activity styles
        for act in settings.get('activities', []):
            styles.append({
                "type": "activity",
                "name": act["name"],
                "class_name": act["class_name"],
                "bg_color": act["bg_color"],
                "border_color": act["border_color"],
                "start_date": act["start_date"],
                "end_date": act["end_date"] or "9999-12-31"
            })

    if styles:
        db["styles"].insert_all(styles)

    # Create views for current styles
    db.execute("""
        CREATE VIEW IF NOT EXISTS current_styles AS
        SELECT type, name, class_name, bg_color, border_color
        FROM styles
        WHERE date('now') BETWEEN date(start_date) AND date(end_date)
    """)

    print(f"Created database at {db_file}")
    print(f"Imported {len(events)} events")
    print(f"Imported {len(styles)} styles")

if __name__ == "__main__":
    create_database()