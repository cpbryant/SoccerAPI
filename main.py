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

def searchTeam(cursor):
    userTeam = input("What team would you like information on: ")
    cursor.execute('''
                   SELECT name, coach, points, matchesPlayed, wins, draws, losses, 
                   goalsScored, goalsConceded, goalDifference FROM teams WHERE name=?
                   ''', (userTeam,))
    teamDetails = cursor.fetchall()

    if teamDetails:
        for detail in teamDetails:
            print(f"Team: {detail[0]}, Coach: {detail[1]}, Points: {detail[2]}, Matches Played: {detail[3]}", 
                  f"Wins: {detail[4]}, Draws: {detail[5]}, Losses: {detail[6]}, Goals Scored:{detail[7]}", 
                  f"Goals Conceded:{detail[8]}, Goal Difference: {detail[9]}")
        # columns = [description[0] for description in cursor.description]
        # teamDict = dict(zip(columns, teamDetails))
        # print(teamDict)
    else:
        print('Team is not in Euro 2024')
    
    print('\n------------\nOptions:\n 1. Select another team\n 2. Return to main menu\n 3. Exit')
    choice = input('Please select an option using the associated number: ')
    if choice == '1':
        return searchTeam(cursor)
    elif choice == '2':
        return main()
    else:
        print('Goodbye!')
    

def view_groups(cursor):
    cursor.execute('''
                   SELECT * FROM GROUPS
                   ''')
    groups = cursor.fetchall()
    for group in groups:
        print(f"Group: {group[1]}")
    
    quest = input("Would you like more information on a specific group (yes/no): ")
    if quest == 'yes':
        # group = input('Enter group letter: ')
        return group_details(cursor)
    else:
        print('\n------------\nOptions:\n 1. Return to main menu\n 2. Exit')
        choice = input('Please select an option using the associated number: ')
        if choice == '1':
            return main()
        else:
            print('Goodbye!')  

def group_details(cursor):
    group = input('Enter group letter: ')
    cursor.execute('''
                   SELECT number, stage, date, minutesCompleted, description, teamA_score,
                   teamB_score, winningTeam FROM matches WHERE description=?
                   ''', (f'group {group}',))
    groupDetails = cursor.fetchall()

    for detail in groupDetails:
        print(f"Group: {detail[4]}, Number: {detail[0]}, Stage: {detail[1]}, Date: {detail[2]}", 
              f"Minutes Completed: {detail[3]}, Team A Score: {detail[5]}, Team B Score: {detail[6]}", 
              f"Winning Team: {detail[7]}")
    
    print('\n------------\Options:\n 1. Choose another group\n 2. Return to main menu\n 3. Exit')
    choice = input('Please select an option using the associated number: ')
    if choice == '1':
        return group_details(cursor)
    elif choice == '2':
        return main()
    else:
        print('Goodbye!')

def view_matches(cursor):
    match_date = input("Enter the match date (YYYY-MM-DD): ")
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
        for match in matches_list:
            print(f"Stage: {match['Stage']}, Date: {match['Date']}, Description: {match['Description']}, "
              f"Team A Score: {match['Team A Score']}, Team B Score: {match['Team B Score']}, "
              f"Winning Team: {match['Winning Team']}")
    else:
        print(f"No matches found on {match_date}")

    print('\n------------\nOptions:\n 1. Select another date\n 2. Return to main menu\n 3. Exit')
    choice = input('Please select an option using the associated number: ')
    if choice == '1':
        return view_matches(cursor)
    elif choice == '2':
        return main()
    else:
        print('Goodbye!') 

def see_team_standings(cursor):
    cursor.execute('''
                   SELECT name, points, matchesPlayed, wins, draws, losses, goalDifference 
                   FROM TEAMS
                   ORDER BY points DESC, goalDifference DESC
                   ''')
    standings = cursor.fetchall()
    for standing in standings:
        print(f"Team: {standing[0]}, Points: {standing[1]}, Matches Played: {standing[2]}, Wins: {standing[3]}", 
              f"Draws: {standing[4]}, Losses: {standing[5]}, Goal Difference: {standing[6]}")
    
    print('\n------------\nOptions:\n 1. Return to main menu\n 2. Exit')
    choice = input('Please select an option using the associated number: ')
    if choice == '1':
        return main()
    else:
        print('Goodbye!') 


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
                return view_matches(cursor)
            elif choice == '2':
                return searchTeam(cursor)
            elif choice == '3':
                return view_groups(cursor)
            elif choice == '4':
                return see_team_standings(cursor)
        
        conn.close()



if __name__ == "__main__":
    main()