import requests
import json
import sqlite3

def get_groups_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
        return data
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def create_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id TEXT PRIMARY KEY,
        name TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id TEXT PRIMARY KEY,
        name TEXT,
        coach TEXT,
        group_id TEXT,
        points INTEGER,
        matchesPlayed INTEGER,
        wins INTEGER,
        draws INTEGER,
        losses INTEGER,
        goalsScored INTEGER,
        goalsConceded INTEGER,
        goalDifference INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        number INTEGER,
        stage TEXT,
        date TEXT,
        minutesCompleted INTEGER,
        description TEXT,
        teamA_score INTEGER,
        teamB_score INTEGER,
        winningTeam TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT,
        minute INTEGER,
        type TEXT,
        team TEXT,
        scoringPlayer TEXT,
        assistingPlayer TEXT,
        cardColor TEXT,
        bookedPlayer TEXT,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    )
    ''')

def insert_group_data(cursor, group):
    group_id = group['_id']
    group_name = group['name']
    cursor.execute('INSERT OR IGNORE INTO groups (id, name) VALUES (?, ?)', (group_id, group_name))
    
    for team_info in group['teams']:
        team = team_info['team']
        team_id = team['_id']
        cursor.execute('''
        INSERT OR IGNORE INTO teams 
        (id, name, coach, group_id, points, matchesPlayed, wins, draws, losses, goalsScored, goalsConceded, goalDifference) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            team_id, 
            team['name'], 
            team['coach'], 
            team['group'], 
            team_info['points'], 
            team_info['matchesPlayed'], 
            team_info['wins'], 
            team_info['draws'], 
            team_info['losses'], 
            team_info['goalsScored'], 
            team_info['goalsConceded'], 
            team_info['goalDifference']
        ))
        
    for match in group['matches']:
        match_id = match['_id']
        cursor.execute('''
        INSERT OR IGNORE INTO matches 
        (id, number, stage, date, minutesCompleted, description, teamA_score, teamB_score, winningTeam) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            match_id, 
            match['number'], 
            match['stage'], 
            match['date'], 
            match['minutesCompleted'], 
            match['description'], 
            match['teamA']['score'], 
            match['teamB']['score'], 
            match['winningTeam']
        ))
        
        for event in match['matchEvents']:
            cursor.execute('''
            INSERT OR IGNORE INTO match_events 
            (match_id, minute, type, team, scoringPlayer, assistingPlayer, cardColor, bookedPlayer) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                match_id,
                event['minute'],
                event['type'],
                event.get('team'),
                event.get('scoringPlayer'),
                event.get('assistingPlayer'),
                event.get('cardColor'),
                event.get('bookedPlayer')
            ))

def main():
    groups_url = "https://euro-20242.p.rapidapi.com/groups"
    headers = {
        "x-rapidapi-key": "bba200fd56mshe960f0b2d77da71p110687jsnd7a81dfd6206",
        "x-rapidapi-host": "euro-20242.p.rapidapi.com"
    }

    data = get_groups_data(groups_url, headers)
    
    if data:
        conn = sqlite3.connect('euro2024.db')
        cursor = conn.cursor()
        create_tables(cursor)
        
        for group in data:
            insert_group_data(cursor, group)
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    main()

# import requests
# import json
# import pandas as pd
# import sqlite3


# #Get groups
# groups_url = "https://euro-20242.p.rapidapi.com/groups"


# headers = {
# 	"x-rapidapi-key": "bba200fd56mshe960f0b2d77da71p110687jsnd7a81dfd6206",
# 	"x-rapidapi-host": "euro-20242.p.rapidapi.com"
# }

# response = requests.get(groups_url, headers=headers)

# if response.status_code == 200:
#     data = response.json()
#     print(json.dumps(data, indent=4))

#     # Connect to SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect('euro2024.db')
#     cursor = conn.cursor()

#     # Create tables
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS groups (
#         id TEXT PRIMARY KEY,
#         name TEXT
#     )
#     ''')
    
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS teams (
#         id TEXT PRIMARY KEY,
#         name TEXT,
#         coach TEXT,
#         group_id TEXT,
#         points INTEGER,
#         matchesPlayed INTEGER,
#         wins INTEGER,
#         draws INTEGER,
#         losses INTEGER,
#         goalsScored INTEGER,
#         goalsConceded INTEGER,
#         goalDifference INTEGER,
#         FOREIGN KEY (group_id) REFERENCES groups (id)
#     )
#     ''')

#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS matches (
#         id TEXT PRIMARY KEY,
#         number INTEGER,
#         stage TEXT,
#         date TEXT,
#         minutesCompleted INTEGER,
#         description TEXT,
#         teamA_score INTEGER,
#         teamB_score INTEGER,
#         winningTeam TEXT
#     )
#     ''')
    
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS match_events (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         match_id TEXT,
#         minute INTEGER,
#         type TEXT,
#         team TEXT,
#         scoringPlayer TEXT,
#         assistingPlayer TEXT,
#         cardColor TEXT,
#         bookedPlayer TEXT,
#         FOREIGN KEY (match_id) REFERENCES matches (id)
#     )
#     ''')
    
#     # Insert data into tables
#     for group in data:
#         group_id = group['_id']
#         group_name = group['name']
        
#         cursor.execute('INSERT OR IGNORE INTO groups (id, name) VALUES (?, ?)', (group_id, group_name))
        
#         for team_info in group['teams']:
#             team = team_info['team']
#             team_id = team['_id']
#             cursor.execute('''
#             INSERT OR IGNORE INTO teams 
#             (id, name, coach, group_id, points, matchesPlayed, wins, draws, losses, goalsScored, goalsConceded, goalDifference) 
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
#                 team_id, 
#                 team['name'], 
#                 team['coach'], 
#                 team['group'], 
#                 team_info['points'], 
#                 team_info['matchesPlayed'], 
#                 team_info['wins'], 
#                 team_info['draws'], 
#                 team_info['losses'], 
#                 team_info['goalsScored'], 
#                 team_info['goalsConceded'], 
#                 team_info['goalDifference']
#             ))
            
#         for match in group['matches']:
#             match_id = match['_id']
#             cursor.execute('''
#             INSERT OR IGNORE INTO matches 
#             (id, number, stage, date, minutesCompleted, description, teamA_score, teamB_score, winningTeam) 
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
#                 match_id, 
#                 match['number'], 
#                 match['stage'], 
#                 match['date'], 
#                 match['minutesCompleted'], 
#                 match['description'], 
#                 match['teamA']['score'], 
#                 match['teamB']['score'], 
#                 match['winningTeam']
#             ))
            
#             for event in match['matchEvents']:
#                 cursor.execute('''
#                 INSERT OR IGNORE INTO match_events 
#                 (match_id, minute, type, team, scoringPlayer, assistingPlayer, cardColor, bookedPlayer) 
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
#                     match_id,
#                     event['minute'],
#                     event['type'],
#                     event.get('team'),
#                     event.get('scoringPlayer'),
#                     event.get('assistingPlayer'),
#                     event.get('cardColor'),
#                     event.get('bookedPlayer')
#                 ))

#     # Commit and close connection
#     conn.commit()
#     conn.close()

# else:
#     print(f"Failed to retrieve data: {response.status_code}")