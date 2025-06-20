# app/orchestrator.py
import os
import time
import json
import random
import redis
import psycopg2
from psycopg2 import OperationalError

# --- Configuration from Environment Variables ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_QUEUE_NAME = 'data_queue'

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'myuser')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'mypassword')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'historical_data')

def get_redis_connection():
    """Establishes a connection to Redis."""
    print("Connecting to Redis...")
    while True:
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            r.ping()
            print("Successfully connected to Redis.")
            return r
        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def get_postgres_connection():
    """Establishes a connection to PostgreSQL."""
    print("Connecting to PostgreSQL...")
    while True:
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
            print("Successfully connected to PostgreSQL.")
            return conn
        except OperationalError as e:
            print(f"PostgreSQL connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def setup_postgres_table(conn):
    """Ensures the target table exists in PostgreSQL."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS event_logs (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(50) NOT NULL,
                value INTEGER NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()
    print("PostgreSQL table 'event_logs' is ready.")

def produce_data(redis_conn):
    """Simulates producing data and pushing it to the Redis queue."""
    event = {
        'event_id': f'evt-{random.randint(1000, 9999)}',
        'value': random.randint(1, 100)
    }
    # We use LPUSH to add the event to the left side of the list (queue)
    redis_conn.lpush(REDIS_QUEUE_NAME, json.dumps(event))
    print(f"Produced event and pushed to Redis queue: {event}")

def consume_and_store_data(redis_conn, pg_conn):
    """Waits for data in Redis, then moves it to PostgreSQL."""
    # BRPOP is a blocking command that waits for an item to appear in the list.
    # The '0' means it will wait indefinitely.
    print(f"\nWaiting for new data in Redis queue '{REDIS_QUEUE_NAME}'...")
    print(f"\npippdsadsadsadolpippola...")

    _, event_json = redis_conn.brpop(REDIS_QUEUE_NAME, 0)
    
    event_data = json.loads(event_json)
    print(f"Consumed event from Redis: {event_data}")

    # Insert data into PostgreSQL
    with pg_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO event_logs (event_id, value) VALUES (%s, %s)",
            (event_data['event_id'], event_data['value'])
        )
        pg_conn.commit()
    print(f"Successfully stored event {event_data['event_id']} in PostgreSQL.")

if __name__ == "__main__":
    redis_conn = get_redis_connection()
    pg_conn = get_postgres_connection()
    
    setup_postgres_table(pg_conn)
    
    # This loop will run forever
    while True:
        try:
            # In a real-world scenario, the producer might be a separate application.
            # Here, we produce one piece of data, then consume one.
            produce_data(redis_conn)
            consume_and_store_data(redis_conn, pg_conn)
            # Wait a bit before producing the next event
            time.sleep(2)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Reconnect if connections are lost
            if redis_conn:
                redis_conn.close()
            if pg_conn:
                pg_conn.close()
            
            print("Attempting to re-establish connections...")
            redis_conn = get_redis_connection()
            pg_conn = get_postgres_connection()
            time.sleep(5)