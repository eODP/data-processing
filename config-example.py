from pathlib import Path

DB_HOST='localhost'
DB_DATABASE=''
DB_USER=''
DB_PASSWORD=''

PROJECT_DIR = Path(__file__).parent.resolve()
RAW_DATA_DIR=(PROJECT_DIR / 'raw_data')
OUTPUT_DIR=(PROJECT_DIR / 'output')
