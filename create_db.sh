#!/usr/local/bin/bash
rm life_events.db
python create_database.py life_events.csv settings.yaml life_events.db
