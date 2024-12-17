import sqlite3

def setup_database():
    connection = sqlite3.connect("database/leaderboard.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE NOT NULL,
            score INTEGER NOT NULL
        )
""")
    
#     placeholder_leaders = [
#         ("jwt011", 5),
#         ("wesvane1", 4),
#         ("CartWheeel", 3),
#         ("FyreSchool", 2),
#         ("bkill16", 1)
#     ]

#     cursor.executemany("""
#         INSERT INTO leaderboard (player_name, score)
#         VALUES (?, ?)
# """, placeholder_leaders)
    
    connection.commit()
    connection.close()

def get_leaderboard():
    connection = sqlite3.connect('database/leaderboard.db')
    cursor = connection.cursor()

    cursor.execute('SELECT player_name, score FROM leaderboard ORDER BY score DESC LIMIT 5')
    top_leaders = cursor.fetchall()

    connection.close()
    return top_leaders
