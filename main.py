import requests
import tqdm
import psycopg2
import psycopg2.errors

# Database credentials. Change as needed
DB_HOST = "Alexs-Air"
DB_NAME = "nba"
DB_USER = "alex"
DB_PASS = "mariners"

class Player():
    """
    Represents a player from the NBA combine. Contains important data and statistics.
    """
    def __init__(self, player_id, first_name, last_name, height, weight, wingspan, standing_reach, vertical_leap, bench_press_reps, lane_agility_time, three_quarter_sprint_time, bmi):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.height = height
        self.weight = weight
        self.wingspan = wingspan
        self.standing_reach = standing_reach
        self.vertical_leap = vertical_leap
        self.bench_press_reps = bench_press_reps
        self.lane_agility_time = lane_agility_time
        self.three_quarter_sprint_time = three_quarter_sprint_time
        self.bmi = bmi
        self.team = self.get_team()
        self.vertical_leap_score = 0
        self.three_quarter_sprint_score = 0
        self.bench_press_score = 0

    def get_team(self):
        """
        Gets the player's team based on their ID from the commonplayerinfo endpoint
        """
        url = f"https://stats.nba.com/stats/commonplayerinfo?LeagueID=&PlayerID={self.player_id}"
        headers = {'Host': 'stats.nba.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'x-nba-stats-origin': 'stats', 'x-nba-stats-token': 'true', 'Connection': 'keep-alive', 'Referer': 'https://stats.nba.com/', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
        try:
            resp_json = requests.get(url=url, headers=headers).json()
        except Exception as e:
            print(f"Error getting team for player {self.player_id}: {e}")
            return None
        results = resp_json['resultSets'][0]['rowSet']
        headers = resp_json['resultSets'][0]['headers']
        return results[0][headers.index('TEAM_ABBREVIATION')]

    def calculate_scores(self, vertical_leap_avg, three_quarter_sprint_avg, bench_press_avg):
        """
        Calculates the scores for the player based on the averages of the combine, where 100 is the average score.
        """
        try:
            self.vertical_leap_score = (self.vertical_leap / vertical_leap_avg) * 100
        except TypeError:
            print("Error calculating vertical leap score: Vertical Leap data is missing")
        try:
            self.three_quarter_sprint_score = (self.three_quarter_sprint_time / three_quarter_sprint_avg) * 100
        except TypeError:
            print("Error calculating three quarter sprint score: Three Quarter Sprint data is missing")
        try:
            self.bench_press_score = (self.bench_press_reps / bench_press_avg) * 100
        except TypeError:
            print("Error calculating bench press score: Bench Press data is missing")

def get_request(year):
    """
    Calls the endpoint for the NBA combine stats and returns the JSON response.
    year: User selected year for stats
    """
    try:
        print("Getting draft combine request ...")
        url = f"https://stats.nba.com/stats/draftcombinestats?LeagueID=00&SeasonYear={year}"
        headers = {'Host': 'stats.nba.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'x-nba-stats-origin': 'stats', 'x-nba-stats-token': 'true', 'Connection': 'keep-alive', 'Referer': 'https://stats.nba.com/', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
        resp_json = requests.get(url=url, headers=headers).json()
        return resp_json
    except requests.exceptions.RequestException as e:
        print(f"Error getting request: {e}")
        
def initalize_players():
    year = input("Enter the draft class (ex. 2019-20): ")

    # Get the response from the NBA API
    api_response = get_request(year)
    if not api_response:
        return None
    results = api_response['resultSets'][0]['rowSet']
    headers = api_response['resultSets'][0]['headers']

    # Store total vertical leap, three-quarter sprint time, and bench press reps for future calculations
    vertical_leap_total = 0
    vertical_leap_count = 0
    three_quarter_sprint_total = 0
    three_quarter_sprint_count = 0
    bench_press_total = 0
    bench_press_count = 0

    # For each result, create a player object with the parameters by mapping the headers to the correct index. Store objects in a list
    players = []
    print("Iterating through players from draft class ...")
    for result in tqdm.tqdm(results):
        player_id = result[headers.index('PLAYER_ID')]
        first_name = result[headers.index('FIRST_NAME')].split()[0]
        last_name = result[headers.index('LAST_NAME')]
        height = result[headers.index('HEIGHT_WO_SHOES')]
        weight = result[headers.index('WEIGHT')]
        wingspan = result[headers.index('WINGSPAN')]
        standing_reach = result[headers.index('STANDING_REACH')]
        vertical_leap = result[headers.index('STANDING_VERTICAL_LEAP')]
        bench_press_reps = result[headers.index('BENCH_PRESS')]
        lane_agility_time = result[headers.index('LANE_AGILITY_TIME')]
        three_quarter_sprint_time = result[headers.index('THREE_QUARTER_SPRINT')]
        max_vertical_leap = result[headers.index('MAX_VERTICAL_LEAP')]
        bmi = result[headers.index('BODY_FAT_PCT')]

        player = Player(player_id, first_name, last_name, height, weight, wingspan, standing_reach, vertical_leap, bench_press_reps, lane_agility_time, three_quarter_sprint_time, bmi)
        players.append(player)

        if vertical_leap:
            vertical_leap_total += vertical_leap
            vertical_leap_count += 1
        if three_quarter_sprint_time:
            three_quarter_sprint_total += three_quarter_sprint_time
            three_quarter_sprint_count += 1
        if bench_press_reps:
            bench_press_total += bench_press_reps
            bench_press_count += 1
        
    print("Calculating averages ...")
    # Calculate averages for the combine
    vertical_leap_avg = vertical_leap_total / vertical_leap_count
    three_quarter_sprint_avg = three_quarter_sprint_total / three_quarter_sprint_count
    bench_press_avg = bench_press_total / bench_press_count
    
    # Use averages to calculate scores for vertical, sprint, and bench press
    print("Calculating scores ...")
    for player in tqdm.tqdm(players):
        player.calculate_scores(vertical_leap_avg, three_quarter_sprint_avg, bench_press_avg)
    
    return players

def store_in_db(players):
    """
    Stores the player data in a PostgreSQL database
    """
    connection = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = connection.cursor()
    
    print("Storing player data in database ...")
    for player in tqdm.tqdm(players):
        try:
            cursor.execute("""
                INSERT INTO draft_combine_stats (
                    id,
                    first_name,
                    last_name,
                    team,
                    height,
                    weight,
                    wingspan,
                    standing_reach,
                    vertical_leap,
                    bench_press_reps,
                    lane_agility_time,
                    three_quarter_sprint_time,
                    vertical_leap_score,
                    three_quarter_sprint_score,
                    bench_press_score,
                    bmi
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                    player.player_id,
                    player.first_name,
                    player.last_name,
                    player.team,
                    player.height,
                    player.weight,
                    player.wingspan,
                    player.standing_reach,
                    player.vertical_leap,
                    player.bench_press_reps,
                    player.lane_agility_time,
                    player.three_quarter_sprint_time,
                    player.vertical_leap_score,
                    player.three_quarter_sprint_score,
                    player.bench_press_score,
                    player.bmi
                ))
            connection.commit()
        except psycopg2.errors.UndefinedTable as e:
            print("Table doesn't exist. Creating table ...")
            cursor.execute("""
                CREATE TABLE draft_combine_stats (
                    id INTEGER PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    team VARCHAR(3),
                    height FLOAT,
                    weight FLOAT,
                    wingspan FLOAT,
                    standing_reach FLOAT,
                    vertical_leap FLOAT,
                    bench_press_reps INTEGER,
                    lane_agility_time FLOAT,
                    three_quarter_sprint_time FLOAT,
                    vertical_leap_score FLOAT,
                    three_quarter_sprint_score FLOAT,
                    bench_press_score FLOAT,
                    bmi FLOAT
                )
            """)
            print("Table created.")
        except psycopg2.errors.UniqueViolation as e:
            print(f"Player {player.player_id} already exists in the database.")
            continue
        except psycopg2.errors.InFailedSqlTransaction as e:
            print("Error storing data in database.")
            continue
    cursor.close()
    print("Data stored successfully.")
    
def main():
    players = initalize_players()
    
    store_in_db(players) if players else print("Error getting players.")


if __name__ == "__main__":
    main()