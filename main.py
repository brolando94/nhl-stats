from scraper.scraper import parse_game_details, request_game_stats, fetch_game_ids, parse_team_stats, parse_boxscore_stats
from lxml import html
import sqlite3
from data import db_ops
from tqdm import tqdm


# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('data/game_data.db')


gids = fetch_game_ids(days=1)
for gid in tqdm(gids):
    matchup_response = request_game_stats(gid, 'matchup')
    team_data = parse_team_stats(game_id=gid, content=html.fromstring(matchup_response.content))
    db_ops.insert_list_of_dicts(conn=conn, table_name='teams', data=team_data)
    bs_response = request_game_stats(gid, 'boxscore')
    boxscore_data = parse_boxscore_stats(game_id=gid, content=html.fromstring(bs_response.content))
    # split skaters and goalies
    skater_list = []
    goalie_list = []
    for player in boxscore_data:
        if player['type'] == 'Skater':
            skater_list.append(player)
        else:
            goalie_list.append(player)
    db_ops.insert_list_of_dicts(conn=conn, table_name='skaters', data=skater_list)
    db_ops.insert_list_of_dicts(conn=conn, table_name='goalies', data=goalie_list)

    game_data = parse_game_details(game_id=gid, content=html.fromstring(bs_response.content))
    db_ops.insert_list_of_dicts(conn=conn, table_name='games', data=[game_data])

print()
# Close the connection
conn.close()