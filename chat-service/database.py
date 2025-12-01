import sqlite3

conn = sqlite3.connect('chat.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    timestamp INTEGER
)
''')
conn.commit()
