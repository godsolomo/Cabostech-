import sqlite3

conn = sqlite3.connect("cabos.db")
conn.execute("PRAGMA foreign_keys = ON")

conn.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    vin TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    plate_number TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS general_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_vin TEXT NOT NULL,
    service_date TEXT NOT NULL,
    odometer_reading INTEGER,
    work_performed TEXT NOT NULL,
    FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
)
""")

conn.commit()
conn.close()

print("CABOS TECH database ready.")
