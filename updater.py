import psycopg2
import time
import random

DB_NAME = "dataviz"
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

def get_random_user_id():
    cursor.execute("SELECT Id FROM users ORDER BY RANDOM() LIMIT 1;")
    return cursor.fetchone()[0]

def get_random_event_id():
    cursor.execute("SELECT Id FROM events ORDER BY RANDOM() LIMIT 1;")
    return cursor.fetchone()[0]

while True:
    user_id = get_random_user_id()
    event_id = get_random_event_id()
    rate = random.randint(0, 5)
    has_attended = random.randint(0, 1)
    is_interested = random.randint(0, 1)
    
    insert_query = """
        INSERT INTO eventhistory (Id, UserId, EventId, Rate, HasAttended, IsInterested)
        VALUES ((SELECT COALESCE(MAX(Id), 0) + 1 FROM eventhistory), %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (user_id, event_id, rate, has_attended, is_interested))
    conn.commit()
    print(f"Inserted: UserId={user_id}, EventId={event_id}, Rate={rate}, HasAttended={has_attended}, IsInterested={is_interested}")
    
    time.sleep(5)
    
cursor.close()
conn.close()
