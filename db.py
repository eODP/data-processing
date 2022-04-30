import psycopg2
import psycopg2.extras

import config

def connect():
    return psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_DATABASE,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

def fetch_all(sql):
    conn = connect()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute(sql)
    
    return cursor.fetchall()

def fetch_one(sql):
    conn = connect()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute(sql)
    
    return cursor.fetchone()

def execute(sql):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute(sql)
    conn.commit()
    
    conn.close()
    
    
    

