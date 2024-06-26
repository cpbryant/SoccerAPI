import requests
import json
import pandas as pd
import sqlite3


#Get matches
matches_url = "https://euro-20242.p.rapidapi.com/matches"

#Get groups
groups_url = "https://euro-20242.p.rapidapi.com/groups"


headers = {
	"x-rapidapi-key": "bba200fd56mshe960f0b2d77da71p110687jsnd7a81dfd6206",
	"x-rapidapi-host": "euro-20242.p.rapidapi.com"
}

response = requests.get(groups_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=4))

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('euro2024.db')
    cursor = conn.cursor()

    # Create tables
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
        captain TEXT,
        championships INTEGER,
        runnersUp INTEGER,
        group_id TEXT,
        imageUrl TEXT,
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
    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY,
        name TEXT,
        team_id TEXT,
        FOREIGN KEY (team_id) REFERENCES teams (id)
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
        winningTeam TEXT,
        stadium TEXT,
        city TEXT
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
        joiningPlayer TEXT,
        leavingPlayer TEXT,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    )
    ''')
    
    # Insert data into tables
    for group in data:
        group_id = group['_id']
        group_name = group['name']
        
        cursor.execute('INSERT OR IGNORE INTO groups (id, name) VALUES (?, ?)', (group_id, group_name))
        
        for team_info in group['teams']:
            team = team_info['team']
            team_id = team['_id']
            cursor.execute('''
            INSERT OR IGNORE INTO teams 
            (id, name, coach, captain, championships, runnersUp, group_id, imageUrl, points, matchesPlayed, wins, draws, losses, goalsScored, goalsConceded, goalDifference) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                team_id, 
                team['name'], 
                team['coach'], 
                team['captain'], 
                team['championships'], 
                team['runnersUp'], 
                team['group'], 
                team['imageUrl'],
                team_info['points'], 
                team_info['matchesPlayed'], 
                team_info['wins'], 
                team_info['draws'], 
                team_info['losses'], 
                team_info['goalsScored'], 
                team_info['goalsConceded'], 
                team_info['goalDifference']
            ))
            
            for player_id in team['players']:
                cursor.execute('INSERT OR IGNORE INTO players (id, team_id) VALUES (?, ?)', (player_id, team_id))
        
        for match in group['matches']:
            match_id = match['_id']
            cursor.execute('''
            INSERT OR IGNORE INTO matches 
            (id, number, stage, date, minutesCompleted, description, teamA_score, teamB_score, winningTeam, stadium, city) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                match_id, 
                match['number'], 
                match['stage'], 
                match['date'], 
                match['minutesCompleted'], 
                match['description'], 
                match['teamA']['score'], 
                match['teamB']['score'], 
                match['winningTeam'], 
                match['stadium'], 
                match['city']
            ))
            
            for event in match['matchEvents']:
                cursor.execute('''
                INSERT OR IGNORE INTO match_events 
                (match_id, minute, type, team, scoringPlayer, assistingPlayer, cardColor, bookedPlayer, joiningPlayer, leavingPlayer) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    match_id,
                    event['minute'],
                    event['type'],
                    event.get('team'),
                    event.get('scoringPlayer'),
                    event.get('assistingPlayer'),
                    event.get('cardColor'),
                    event.get('bookedPlayer'),
                    event.get('joiningPlayer'),
                    event.get('leavingPlayer')
                ))

    # Commit and close connection
    conn.commit()
    conn.close()

else:
    print(f"Failed to retrieve data: {response.status_code}")