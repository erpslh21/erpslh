import sqlite3
import os

db_path = 'instance/farm.db'

def reset_db():
    print(f"Connecting to {db_path}...")
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Dropping table broiler_standard...")
    cursor.execute("DROP TABLE IF EXISTS broiler_standard;")

    print("Creating table broiler_standard...")
    create_table_sql = """
    CREATE TABLE broiler_standard (
        id INTEGER NOT NULL PRIMARY KEY,
        age_days INTEGER NOT NULL,
        water_to_feed_ratio FLOAT DEFAULT 0.0,
        live_weight FLOAT DEFAULT 0.0,
        daily_gain FLOAT DEFAULT 0.0,
        avg_daily_gain FLOAT DEFAULT 0.0,
        feed_consumption FLOAT DEFAULT 0.0,
        cum_feed_consumption FLOAT DEFAULT 0.0,
        fcr FLOAT DEFAULT 0.0,
        econ_fcr FLOAT DEFAULT 0.0,
        daily_depletion_rate FLOAT DEFAULT 0.0,
        cum_depletion_rate FLOAT DEFAULT 0.0,
        pef FLOAT DEFAULT 0.0
    );
    """
    cursor.execute(create_table_sql)

    conn.commit()
    print("broiler_standard table recreated successfully.")

    # Check table structure
    cursor.execute("PRAGMA table_info(broiler_standard);")
    columns = cursor.fetchall()
    print("Table columns:")
    for col in columns:
        print(col)

    conn.close()

if __name__ == "__main__":
    reset_db()
