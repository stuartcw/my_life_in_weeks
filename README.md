# my_life_in_weeks

#My Life in Weeks

A simple application for managing personal life events and generating a visual representation of those events using SQLite, CSV, YAML, and HTML. This project contains the functionality to create a SQLite database, extract tables from HTML files, and generates a web page to visualize these events.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Scripts Description](#scripts-description)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

To get a copy of this project running on your local machine for development and testing purposes, follow these instructions:

### Prerequisites

Make sure you have the following installed on your machine:

- Python 3.x
- SQLite
- pip (Python package manager)

You will also need to install the required Python packages:

```bash
pip install sqlite-utils pandas beautifulsoup4 jinja2 pyyaml click
```

## Project Structure

```
.
├── create_database.py       # Script to create the SQLite database from CSV and YAML
├── extract_tables.py        # Script to extract tables from HTML files and save as CSV
├── life_weeks_python.py     # Script to generate HTML based on the events data
├── create_db.sh             # Shell script to create the database
├── life_events.csv          # Sample CSV file for life events
├── settings.yaml            # YAML configurations for styles and locations
├── life_weeks_template.html  # HTML template for generating the life weeks visualization
└── README.md                # Documentation for the project
```

## Scripts Description

### `create_database.py`

This script creates a SQLite database from a provided CSV file of life events and a YAML file for configuration settings.

**Usage:**

```bash
python create_database.py <csv_file> <settings_file> <db_file>
```
- `csv_file`: Path to the CSV file containing event data.
- `settings_file`: Path to the YAML file containing styles and options.
- `db_file`: Path where the database file will be created.

### `extract_tables.py`

Extracts tables from a specified HTML file and saves each table as a separate CSV file.

**Usage:**

```python
python extract_tables.py <html_file> <output_directory>
```

### `life_weeks_python.py`

Generates an HTML file that visualizes the life events stored in the SQLite database. This script uses Jinja2 templating to create the output HTML based on the events and styles.

**Usage:**

Run this script directly:

```bash
python life_weeks_python.py
```

### `create_db.sh`

A shell script that runs `create_database.py` to create the SQLite database from the provided data files.

**Usage:**

```bash
bash create_db.sh
```

## Usage

1. Prepare your CSV file and YAML configuration as needed, ensuring they follow the expected format.
2. Run the `create_db.sh` script to create the database:
   ```bash
   bash create_db.sh
   ```
3. After running the above script, run the `life_weeks_python.py` script:
   ```bash
   python life_weeks_python.py
   ```
4. Open the generated `life_weeks.html` file in a web browser to view your life events visualized.

## Contributing

If you would like to contribute to this project, please fork the repository and create a pull request. For significant changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
