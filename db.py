import psycopg2

import config

conn = psycopg2.connect(
    host=config.DB_HOST,
    database=config.DB_DATABASE,
    user=config.DB_USER,
    password=config.DB_PASSWORD
)
