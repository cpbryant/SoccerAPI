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

def searchTeam(team, cursor):
    cursor.execute('''
                   SELECT * FROM teams WHERE name=?
                   ''', (team,))
    teamDetails = cursor.fetchone()

    if teamDetails:
        columns = [description[0] for description in cursor.description]
        teamDict = dict(zip(columns, teamDetails))
        print(teamDict)
    else:
        print('Team is not in 2024 Euros')

def view_groups(cursor):
    cursor.execute('''
                   SELECT * FROM GROUPS
                   ''')
    groups = cursor.fetchall()
    for group in groups:
        print(f"Group: {group[1]}")
    
    quest = input("Would you like more information on a specific group (yes/no): ")
    if quest == 'yes':
        group = input('Enter group letter: ')
        return group_details(group, cursor)
    else:
        toMenu = input("Return to main menu (yes/no): ")
        if toMenu == 'yes':
            return main()
        else:
            print('Goodbye!')    

def group_details(group, cursor):
    cursor.execute('''
                   SELECT number, stage, date, minutesCompleted, description, teamA_score,
                   teamB_score, winningTeam FROM matches WHERE description=?
                   ''', (f'group {group}',))
    groupDetails = cursor.fetchall()

    for detail in groupDetails:
        print(f'''Group: {detail[4]}\t Number: {detail[0]}\t Stage: {detail[1]}\t Date: {detail[2]}\t Minutes Completed: {detail[3]}\t Team A Score: {detail[5]}\t Team B Score: {detail[6]}\t Winning Team: {detail[7]}
              ''')
    
    # columns = [description[0] for description in cursor.description]
    # groupDicts = []
    # for row in groupDetails:
    #     groupDict = dict(zip(columns, row))
    #     groupDicts.append(groupDict)
    
    # for grouped in groupDicts:
    #     print(grouped)

    #print(f"Team: {standing[0]}, Points: {standing[1]}, Matches Played: {standing[2]}, Wins: {standing[3]}, Draws: {standing[4]}, Losses: {standing[5]}, Goal Difference: {standing[6]}")


def view_matches(cursor, match_date):
    cursor.execute('''
                   SELECT stage, date, description, teamA_score, teamB_score, winningTeam 
                   FROM matches WHERE date LIKE ?
                   ''', (f'{match_date}%',))
    matches = cursor.fetchall()
    
    matches_list = []
    if matches:
        for match in matches:
            matches_list.append({
                'Stage' : match[0],
                'Date' : match[1],
                'Description' : match[2],
                'Team A Score' : match[3],
                'Team B Score' : match[4],
                'Winning Team' : match[5]
            })
        print(matches_list)
    else:
        print(f"No matches found on {match_date}")

     
    for match in matches_list:
         #print(f'Match: {match[1]}')
         print(match)
     

def see_team_standings(cursor):
    cursor.execute('''
                   SELECT name, points, matchesPlayed, wins, draws, losses, goalDifference 
                   FROM TEAMS
                   ORDER BY points DESC, goalDifference DESC
                   ''')
    standings = cursor.fetchall()
    for standing in standings:
        print(f"Team: {standing[0]}, Points: {standing[1]}, Matches Played: {standing[2]}, Wins: {standing[3]}, Draws: {standing[4]}, Losses: {standing[5]}, Goal Difference: {standing[6]}")



def main():
    groups_url = "https://euro-20242.p.rapidapi.com/groups"
    headers = {
        "x-rapidapi-key": "7268c35a14mshd1f8682123f484bp19d057jsnedc2299f51ed",
        "x-rapidapi-host": "euro-20242.p.rapidapi.com"
        #  "x-rapidapi-key": "bba200fd56mshe960f0b2d77da71p110687jsnd7a81dfd6206",
        #  "x-rapidapi-host": "euro-20242.p.rapidapi.com"
    }

    data = get_groups_data(groups_url, headers)
    
    if data:
        conn = sqlite3.connect('euro2024.db')
        cursor = conn.cursor()
        create_tables(cursor)
        
        for group in data:
            insert_group_data(cursor, group)
        
        conn.commit()
        
        while True:
            print('''
                1. View Match Details\n
                2. View Team Details\n
                3. View Group Details\n
                4. View Team Standings''')
            choice = input('Please select an option using the associated number: ')

            if choice == '1':
                match_date = input("Enter the match date (YYYY-MM-DD): ")
                return view_matches(cursor, match_date)
            elif choice == '2':
                userTeam = input("What team would you like information on: ")
                return searchTeam(userTeam, cursor)
            elif choice == '3':
                return view_groups(cursor)
            elif choice == '4':
                return see_team_standings(cursor)
        
        conn.close()

    

if __name__ == "__main__":
    main()