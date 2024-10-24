import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('game_data.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
                    game_id TEXT,
                    team TEXT,
                    outcome TEXT,
                    home_away TEXT,
                    home BOOL,
                    away BOOL,
                    overtime BOOL,
                    opponent TEXT,
                    goals_for INTEGER,
                    goals_against INTEGER,
                    goals_for_p1 INTEGER,
                    goals_against_p1 INTEGER,
                    goals_for_p2 INTEGER,
                    goals_against_p2 INTEGER,
                    goals_for_p3 INTEGER,
                    goals_against_p3 INTEGER,
                    goals_for_ot INTEGER,
                    goals_against_ot INTEGER,
                    shots_for INTEGER,
                    shots_against INTEGER,
                    hits_for INTEGER,
                    hits_against INTEGER,
                    faceoffs_for INTEGER,
                    faceoffs_against INTEGER,
                    power_plays_for INTEGER,
                    power_plays_against INTEGER,
                    power_play_goals_for INTEGER,
                    power_play_goals_against INTEGER,
                    short_handed_goals_for INTEGER,
                    short_handed_goals_against INTEGER,
                    penalties_for INTEGER,
                    penalties_against INTEGER,
                    penalty_minutes_for INTEGER,
                    penalty_minutes_against INTEGER,
                    blocked_shots_for INTEGER,
                    blocked_shots_against INTEGER,
                    takeaways_for INTEGER,
                    takeaways_against INTEGER,
                    giveaways_for INTEGER,
                    giveaways_against INTEGER,
                    PRIMARY KEY (game_id, team)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS skaters (
                    game_id TEXT,
                    team TEXT,
                    player TEXT,
                    type TEXT,
                    goals TEXT,
                    assists INTEGER,
                    plus_minus INTEGER,
                    shots INTEGER,
                    missed_shots INTEGER,
                    blocked_shots INTEGER,
                    penalties INTEGER,
                    penalty_minutes INTEGER,
                    hits INTEGER,
                    takeaways INTEGER,
                    giveaways INTEGER,
                    shifts INTEGER,
                    time_on_ice TIME,
                    power_play_time_on_ice TIME,
                    short_handed_time_on_ice TIME,
                    even_strength_time_on_ice TIME,
                    faceoffs_won INTEGER,
                    faceoffs_lost INTEGER,
                    PRIMARY KEY (game_id, team, player)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS goalies (
                    game_id TEXT,
                    team TEXT,
                    player TEXT,
                    type TEXT,
                    shots_against INTEGER,
                    goals_against INTEGER,
                    saves INTEGER,
                    expected_saves INTEGER,
                    power_play_saves INTEGER,
                    short_handed_saves INTEGER,
                    shootout_shots_against INTEGER,
                    shootout_saves INTEGER,
                    time_on_ice TIME,
                    penalty_minutes INTEGER,
                    PRIMARY KEY (game_id, team, player)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT,
                    game_datetime TEXT,
                    favorite TEXT,
                    odds INTEGER,
                    over_under REAL,
                    PRIMARY KEY (game_id)
                )''')
# Commit the changes
conn.commit()

# Close the connection
conn.close()
