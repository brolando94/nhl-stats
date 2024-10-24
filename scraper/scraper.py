import requests
from datetime import date, timedelta, datetime
from lxml import html
from typing_extensions import TypedDict

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
headers = {'User-Agent': f'{user_agent}'}


class Player(TypedDict):
    game_id:  str
    team: str
    player: str
    type: str # Skater or Goalie
    goals: int
    assists: int
    plus_minus: int
    shots: int
    missed_shots: int
    blocked_shots: int
    penalties: int
    penalty_minutes: int
    hits: int
    takeaways: int
    giveaways: int
    shifts: int
    time_on_ice: str
    power_play_time_on_ice: str
    short_handed_time_on_ice: str
    even_strength_time_on_ice: str
    faceoffs_won: int
    faceoffs_lost: int
    # goalie stats
    shots_against: int
    goals_against: int
    saves: int
    expected_saves: int
    power_play_saves: int
    short_handed_saves: int
    shootout_shots_against: int
    shootout_saves: int


class Game(TypedDict):
    game_id: str
    game_datetime: datetime
    favorite: str
    odds: int
    over_under: str


class Team(TypedDict): # team stats
    game_id:  str
    team: str
    outcome: str # win, loss
    home_away: str # was the team the home or away team
    home: bool
    away: bool
    overtime: bool
    opponent: str
    goals_for: int
    goals_against: int
    goals_for_p1: int
    goals_against_p1: int
    goals_for_p2: int
    goals_against_p2: int
    goals_for_p3: int
    goals_against_p3: int
    goals_for_ot: int
    goals_against_ot: int
    shots_for: int
    shots_against: int
    hits_for: int
    hits_against: int
    faceoffs_for: int
    faceoffs_against: int
    power_plays_for: int
    power_plays_against: int
    power_play_goals_for: int
    power_play_goals_against: int
    short_handed_goals_for: int
    short_handed_goals_against: int
    penalties_for: int
    penalties_against: int
    penalty_minutes_for: int
    penalty_minutes_against: int
    blocked_shots_for: int
    blocked_shots_against: int
    takeaways_for: int
    takeaways_against: int
    giveaways_for: int
    giveaways_against: int


def fetch_game_ids(days=None) -> list:
    if days is None:
        days = 1
    return_list = []
    request_date = date.today() - timedelta(days=days)
    date_str = f"{request_date.year}{request_date.month}{request_date.day}"
    url = f"https://www.espn.com/nhl/scoreboard/_/date/{date_str}"
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        content = html.fromstring(response.content)
        game_list = content.xpath("//section[@class='Scoreboard bg-clr-white flex flex-auto justify-between']")
        for game in game_list:
            return_list.append(str(game.xpath('@id')[0]))

        return return_list

    else:
        print(response.status_code)
        return fetch_game_ids(days)


def request_game_stats(game_id, stat_type):
    url = f'https://www.espn.com/nhl/{stat_type}/_/gameId/{game_id}'
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        print(response.status_code)
        return request_game_stats(game_id, stat_type)


def parse_team_stats(content: html, game_id: str) -> list[Team]:
    home_stats = Team(game_id=game_id, home_away='Home', home=True, away=False)
    away_stats = Team(game_id=game_id, home_away='Away', home=False, away=True)

    teams = content.xpath("//div[@class='Gamestrip__Info Gamestrip__Info--post']//h2")
    home_stats['team'] = str(teams[1].text)
    away_stats['team'] = str(teams[0].text)
    home_stats['opponent'] = str(teams[0].text)
    away_stats['opponent'] = str(teams[1].text)

    # scores
    scores = content.xpath("//div[@class='Gamestrip__ScoreContainer flex flex-column items-center justify-center relative']/div[1]")
    home_stats['goals_for'] = int(str(scores[1].text))
    home_stats['goals_against'] = int(str(scores[0].text))
    away_stats['goals_against'] = home_stats['goals_for']
    away_stats['goals_for'] = home_stats['goals_against']

    # overtime
    overtime = content.xpath("(//div[@class='ResponsiveTable Gamestrip__Table']//tr)[3]/td")
    if len(overtime) == 6:
        home_stats['overtime'] = True
        away_stats['overtime'] = True
    else:
        home_stats['overtime'] = False
        away_stats['overtime'] = False

    # outcome
    if home_stats['goals_for'] > home_stats['goals_against']:
        home_stats['outcome'] = 'Win'
        if home_stats['overtime']:
            away_stats['outcome'] = 'OT Loss'
        else:
            away_stats['outcome'] = 'Loss'

    else:
        away_stats['outcome'] = 'Win'
        if away_stats['overtime']:
            home_stats['outcome'] = 'OT Loss'
        else:
            home_stats['outcome'] = 'Loss'

    # goals by period
    for i in range(1, 4):
        home_stats[f'goals_for_p{i}'] = int(str(content.xpath(f"(//div[@class='ResponsiveTable Gamestrip__Table']//tr)[3]/td[{i + 1}]")[0].text))
        home_stats[f'goals_against_p{i}'] = int(str(content.xpath(f"(//div[@class='ResponsiveTable Gamestrip__Table']//tr)[2]/td[{i + 1}]")[0].text))
        away_stats[f'goals_against_p{i}'] = home_stats[f'goals_for_p{i}']
        away_stats[f'goals_for_p{i}'] = home_stats[f'goals_against_p{i}']
    # overtime goals
    if home_stats['overtime']:
        home_stats['goals_for_ot'] = int(str(content.xpath("(//div[@class='ResponsiveTable Gamestrip__Table']//tr)[3]/td[5]")[0].text))
        home_stats['goals_against_ot'] = int(str(content.xpath("(//div[@class='ResponsiveTable Gamestrip__Table']//tr)[2]/td[5]")[0].text))
        away_stats['goals_against_ot'] = home_stats['goals_for_ot']
        away_stats['goals_for_ot'] = home_stats['goals_against_ot']
    else:
        home_stats['goals_for_ot'] = None
        home_stats['goals_against_ot'] = None
        away_stats['goals_against_ot'] = None
        away_stats['goals_for_ot'] = None

    stat_map = [['shots', '2'], ['hits', '3'], ['faceoffs', '4'], ['power_plays', '6'], ['power_play_goals', '7'],
                ['short_handed_goals', '9'], ['penalties', '10'], ['penalty_minutes', '11'],
                ['blocked_shots', '12'], ['takeaways', '13'], ['giveaways', '14']]

    for stat in stat_map:
        home_stats[f'{stat[0]}_for'] = int(str(content.xpath(f"(//div[@class='ResponsiveTable TeamStats--vertical']//tr)[{stat[1]}]/td[3]")[0].text))
        home_stats[f'{stat[0]}_against'] = int(str(content.xpath(f"(//div[@class='ResponsiveTable TeamStats--vertical']//tr)[{stat[1]}]/td[2]")[0].text))
        away_stats[f'{stat[0]}_for'] = home_stats[f'{stat[0]}_against']
        away_stats[f'{stat[0]}_against'] = home_stats[f'{stat[0]}_for']

    return [home_stats, away_stats]


def parse_boxscore_stats(content: html, game_id: str) -> list[Player]:
    time_modify_list = ['time_on_ice', 'power_play_time_on_ice', 'short_handed_time_on_ice',
                        'even_strength_time_on_ice']
    return_list = []
    for i in range(1, 3):
        base_path = f"//div[@class='Wrapper'][{i}]"
        team = str(content.xpath(f"{base_path}//div[@class='BoxscoreItem__TeamName h5']")[0].text)
        for j in range(1, 3):
            if j == 1:
                player_add = 2
                player_type = 'Skater'
                stat_map = [['goals', '1'], ['assists', '2'], ['plus_minus', '3'], ['shots', '4'],
                            ['missed_shots', '5'], ['blocked_shots', '6'],  ['penalties', '7'],
                            ['penalty_minutes', '8'], ['hits', '9'], ['takeaways', '10'], ['giveaways', '11'],
                            ['shifts', '12'], ['time_on_ice', '13'], ['power_play_time_on_ice', '14'],
                            ['short_handed_time_on_ice', '15'], ['even_strength_time_on_ice', '16'],
                            ['faceoffs_won', '17'], ['faceoffs_lost', '18']]
            else:
                player_add = 1
                player_type = 'Goalie'
                stat_map = [['shots_against', '1'], ['goals_against', '2'], ['saves', '3'], ['expected_saves', '5'],
                            ['power_play_saves', '6'], ['short_handed_saves', '7'], ['shootout_shots_against', '8'],
                            ['shootout_saves', '9'], ['time_on_ice', '10'], ['penalty_minutes', '11']]

            # collect players
            player_base_path = f"{base_path}//div[@class='Boxscore flex flex-column'][{j}]"
            player_count = len(content.xpath(f"{player_base_path}//a[@class='AnchorLink truncate db Boxscore__AthleteName']"))

            for k in range(1, player_count + player_add):
                player = Player(game_id=game_id, team=team, type=player_type)
                # see if there is a player name. The header columns wont have one
                player_path = f"{player_base_path}//tr[@data-idx='{k}']"
                try:
                    player['player'] = str(content.xpath(f"({player_path})[1]//a[@class='AnchorLink truncate db Boxscore__AthleteName']")[0].text)
                except IndexError:
                    continue

                for stat in stat_map:
                    player[f'{stat[0]}'] = str(content.xpath(f"({player_path})[2]//td[{stat[1]}]")[0].text)
                    if stat[0] in time_modify_list:
                        player[f'{stat[0]}'] = f"00:{player[f'{stat[0]}']}"

                return_list.append(player)

    return return_list


def parse_game_details(content: html, game_id: str) -> Game:
    game_info = Game(game_id=game_id)

    # game date and time
    raw_time_list = content.xpath("//div[@class='n8 GameInfo__Meta']/span[1]/text()")
    game_time_list = str(raw_time_list[0]).split(" ")
    if game_time_list[1] == "PM":
        hours = str(int(game_time_list[0].split(':')[0]) + 12)
        minutes = str(game_time_list[0].split(':')[1])
        game_time = f"{hours}:{minutes}:00"
    else:
        game_time = f"{game_time_list[0]}:00"

    raw_game_date_list = str(raw_time_list[2]).split(" ")
    month = _month_to_num(raw_game_date_list[0])
    day = raw_game_date_list[1][:-1]
    if len(day) == 1:
        day = f'0{day}'
    year = raw_game_date_list[2]

    game_info['game_datetime'] = datetime.strptime(f'{year}-{month}-{day} {game_time}', '%Y-%m-%d %H:%M:%S')

    # betting odds
    line_list = str(content.xpath("//div[@class='n8 GameInfo__BettingItem flex-expand line']/text()")[2]).split(" ")
    game_info['favorite'] = line_list[0]
    game_info['odds'] = int(line_list[1])
    game_info['over_under'] = str(content.xpath("//div[@class='n8 GameInfo__BettingItem flex-expand ou']/text()")[2])

    return game_info


def _month_to_num(month):
    match month.lower():
        case 'january':
            return '01'
        case 'february':
            return '02'
        case 'march':
            return '03'
        case 'april':
            return '04'
        case 'may':
            return '05'
        case 'june':
            return '06'
        case 'july':
            return '07'
        case 'august':
            return '08'
        case 'september':
            return '09'
        case 'october':
            return '10'
        case 'november':
            return '11'
        case 'december':
            return '12'


