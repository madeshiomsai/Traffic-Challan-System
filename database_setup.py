"""
Run this once to (re)create Chalan.db with the violations table
(fine amounts) and the challans table (issued-challan history).

    python database_setup.py
"""

import sqlite3
from config import CHALAN_DB


def setup_database():
    conn = sqlite3.connect(CHALAN_DB)
    cursor = conn.cursor()

    # ---- Violation fine amounts ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_name TEXT NOT NULL UNIQUE,
            fine INTEGER NOT NULL
        )
    """)

    violations = [
        ("Triple Ride", 1000),
        ("No Parking", 100),
        ("No Helmet", 200),
        ("Overspeed", 1000),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO violations (violation_name, fine)
        VALUES (?, ?)
    """, violations)

    # ---- Issued challan history (no driver photo) ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT,
            vehicle_reg TEXT NOT NULL,
            vehicle_type TEXT,
            violation TEXT NOT NULL,
            fine INTEGER NOT NULL,
            mobile TEXT,
            challan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            notified INTEGER DEFAULT 0
        )
    """)

    # Migrate an older challans table (e.g. one that had a driver_photo
    # column, or was missing vehicle_type / notified) without losing data.
    cursor.execute("PRAGMA table_info(challans)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "vehicle_type" not in existing_columns:
        cursor.execute("ALTER TABLE challans ADD COLUMN vehicle_type TEXT")

    if "notified" not in existing_columns:
        cursor.execute("ALTER TABLE challans ADD COLUMN notified INTEGER DEFAULT 0")

    conn.commit()

    print("--------------------------------")
    print("VIOLATIONS TABLE")
    print("--------------------------------")
    cursor.execute("SELECT id, violation_name, fine FROM violations")
    for row in cursor.fetchall():
        print(row)

    print("--------------------------------")
    print("Chalan.db is ready (violations + challans tables).")
    print("--------------------------------")

    conn.close()


if __name__ == "__main__":
    setup_database()
