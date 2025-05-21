import sqlite3
from datetime import datetime

# Example database setup (SQLite)
def setup_db():
    conn = sqlite3.connect('premium_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_users (
            user_id INTEGER PRIMARY KEY,
            selected_plan TEXT,
            payment_proof TEXT,
            premium_expiry DATETIME
        );
    ''')
    conn.commit()
    conn.close()

# Function to add user to the database
def add_user(user_id, selected_plan, payment_proof, premium_expiry):
    conn = sqlite3.connect('premium_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO premium_users (user_id, selected_plan, payment_proof, premium_expiry)
        VALUES (?, ?, ?, ?);
    ''', (user_id, selected_plan, payment_proof, premium_expiry))
    conn.commit()
    conn.close()

# Check expiry and deactivate if necessary
def check_expiry():
    conn = sqlite3.connect('premium_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, premium_expiry FROM premium_users WHERE premium_expiry < ?;
    ''', (datetime.now(),))
    expired_users = cursor.fetchall()
    for user in expired_users:
        deactivate_premium(user[0])
    conn.close()

# Deactivate user from premium list
def deactivate_premium(user_id):
    conn = sqlite3.connect('premium_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM premium_users WHERE user_id = ?;
    ''', (user_id,))
    conn.commit()
    conn.close()
``