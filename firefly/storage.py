import sqlite3
import datetime
from typing import Dict, Any

def upgrade_schema(conn: sqlite3.Connection):
    """
    Upgrades the database schema by adding new columns if they don't exist.
    """
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(metrics)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add 'hostname' column if it doesn't exist
    if 'hostname' not in columns:
        print("Upgrading schema: adding 'hostname' column.")
        cursor.execute("ALTER TABLE metrics ADD COLUMN hostname TEXT")

    # Add 'network_interface' column if it doesn't exist
    if 'network_interface' not in columns:
        print("Upgrading schema: adding 'network_interface' column.")
        cursor.execute("ALTER TABLE metrics ADD COLUMN network_interface TEXT")

    conn.commit()


def init_db(db_path: str):
    """
    Initializes the database and creates/upgrades the metrics table.

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
                error TEXT,
                hostname TEXT,
                network_interface TEXT
            )
        """)

        # After ensuring the table exists, check if it needs an upgrade
        upgrade_schema(conn)

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

        timestamp = datetime.datetime.now().isoformat()

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
            "hostname": metrics.get("hostname"),
            "network_interface": metrics.get("network_interface"),
            "error": metrics.get("error"),
        }

        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f"INSERT INTO metrics ({columns}) VALUES ({placeholders})"

        cursor.execute(sql, tuple(data.values()))
        conn.commit()


if __name__ == '__main__':
    # Test the storage module with schema upgrade
    TEST_DB_PATH = "test_metrics_v2.db"
    print(f"Testing storage with database: {TEST_DB_PATH}")

    # 1. Initialize the database (first time)
    print("1. Initializing database...")
    init_db(TEST_DB_PATH)
    print("Database initialized.")

    # 2. Insert a record without new fields (simulating old version)
    print("2. Inserting a sample old-style metric...")
    sample_metric_old = {'url': 'https://www.google.com', 'http_code': 200, 'time_total': 0.5}
    insert_metric(TEST_DB_PATH, sample_metric_old)
    print("Old metric inserted.")

    # 3. Re-initialize to trigger schema upgrade
    print("3. Re-initializing to test schema upgrade...")
    init_db(TEST_DB_PATH)
    print("Schema upgrade check complete.")

    # 4. Insert a new record with all fields
    print("4. Inserting a sample new-style metric...")
    sample_metric_new = {
        'url': 'https://www.github.com',
        'http_code': 200, 'time_total': 0.8,
        'hostname': 'test-host',
        'network_interface': 'eth0'
    }
    insert_metric(TEST_DB_PATH, sample_metric_new)
    print("New metric inserted.")

    # 5. Verify the data
    print("5. Verifying data...")
    with sqlite3.connect(TEST_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metrics ORDER BY id")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} rows:")
        for row in rows:
            print(dict(row))

    # Clean up
    import os
    os.remove(TEST_DB_PATH)
    print(f"Cleaned up {TEST_DB_PATH}.")
