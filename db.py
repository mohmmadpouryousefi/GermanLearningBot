import sqlite3
import json
from datetime import datetime

# Initialize the database
def init_db():
    conn = sqlite3.connect('german_bot.db')
    cursor = conn.cursor()
    
    # Create messages table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        role TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Create user_data table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        level TEXT,
        state TEXT,
        last_active TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Save a message to the database
def save_message(user_id, message, role="user"):
    conn = sqlite3.connect('german_bot.db')
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO messages (user_id, message, role, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, message, role, timestamp)
    )
    
    conn.commit()
    conn.close()

# Get conversation history for a user
def get_conversation_history(user_id, limit=10):
    conn = sqlite3.connect('german_bot.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT message, role, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    
    # Reverse the results to get chronological order
    results = list(reversed(cursor.fetchall()))
    
    conn.close()
    
    # Format the results as a list of dictionaries
    history = [
        {"message": message, "role": role, "timestamp": timestamp}
        for message, role, timestamp in results
    ]
    
    return history

# Initialize the database when this module is imported
init_db()
