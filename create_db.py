import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("health_dashboard.db")
cursor = conn.cursor()

# Create table to store user submissions
cursor.execute("""
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    symptoms TEXT,
    prediction TEXT,
    submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Save changes and close connection
conn.commit()
conn.close()

print("✅ Database 'health_dashboard.db' and table 'submissions' created successfully!")
