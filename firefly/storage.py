import sqlite3
import datetime
from typing import Dict, Any

def init_db(db_path: str):
    """
    Initializes the database and creates the metrics table if it doesn't exist.

    Args:
        db_path: The path to the SQLite database file.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                url TEXT NOT NULL,
                http_code INTEGER,
                time_namelookup REAL,
                time_connect REAL,
                time_appconnect REAL,
                time_pretransfer REAL,
                time_starttransfer REAL,
                time_total REAL,
                speed_download REAL,
                speed_upload REAL,
                size_download REAL,
                error TEXT
            )
        """)
        conn.commit()

def insert_metric(db_path: str, metrics: Dict[str, Any]):
    """
    Inserts a new metric record into the database.

    Args:
        db_path: The path to the SQLite database file.
        metrics: A dictionary containing the performance metrics.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Get current timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Prepare data for insertion
        data = {
            "timestamp": timestamp,
            "url": metrics.get("url"),
            "http_code": metrics.get("http_code"),
            "time_namelookup": metrics.get("time_namelookup"),
            "time_connect": metrics.get("time_connect"),
            "time_appconnect": metrics.get("time_appconnect"),
            "time_pretransfer": metrics.get("time_pretransfer"),
            "time_starttransfer": metrics.get("time_starttransfer"),
            "time_total": metrics.get("time_total"),
            "speed_download": metrics.get("speed_download"),
            "speed_upload": metrics.get("speed_upload"),
            "size_download": metrics.get("size_download"),
            "error": metrics.get("error"),
        }

        # Create the insert query
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f"INSERT INTO metrics ({columns}) VALUES ({placeholders})"

        cursor.execute(sql, tuple(data.values()))
        conn.commit()


if __name__ == '__main__':
    # Test the storage module
    TEST_DB_PATH = "test_metrics.db"
    print(f"Testing storage with database: {TEST_DB_PATH}")

    # 1. Initialize the database
    print("1. Initializing database...")
    init_db(TEST_DB_PATH)
    print("Database initialized.")

    # 2. Insert a sample success metric
    print("2. Inserting a sample success metric...")
    sample_metric_success = {
        'url': 'https://www.google.com',
        'http_code': 200,
        'time_namelookup': 0.05,
        'time_connect': 0.1,
        'time_total': 0.5
    }
    insert_metric(TEST_DB_PATH, sample_metric_success)
    print("Success metric inserted.")

    # 3. Insert a sample error metric
    print("3. Inserting a sample error metric...")
    sample_metric_error = {
        'url': 'https://nonexistent.url.xyz',
        'error': 'Could not resolve host'
    }
    insert_metric(TEST_DB_PATH, sample_metric_error)
    print("Error metric inserted.")

    # 4. Verify insertion by querying the data
    print("4. Verifying insertion...")
    with sqlite3.connect(TEST_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metrics")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} rows in the 'metrics' table.")
        for row in rows:
            print(dict(row))

    # Clean up the test database
    import os
    os.remove(TEST_DB_PATH)
    print(f"Cleaned up {TEST_DB_PATH}.")
