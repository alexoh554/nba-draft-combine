import requests
import tqdm

class Player():
    """
    Represents a player from the NBA combine. Contains important data and statistics.
    """
    def __init__(self, player_id, height, weight, wingspan, standing_reach, vertical_leap, bench_press_reps, lane_agility_time, three_quarter_sprint_time, bmi):
        self.player_id = player_id
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
    print("Getting draft combine request ...")
    url = "https://stats.nba.com/stats/draftcombinestats?LeagueID=00&SeasonYear=2019-20"
    headers = {'Host': 'stats.nba.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'x-nba-stats-origin': 'stats', 'x-nba-stats-token': 'true', 'Connection': 'keep-alive', 'Referer': 'https://stats.nba.com/', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    resp_json = requests.get(url=url, headers=headers).json()
    return resp_json

def initalize_players():
    year = 0

    # Get the response from the NBA API
    api_response = get_request(year)
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

        player = Player(player_id, height, weight, wingspan, standing_reach, vertical_leap, bench_press_reps, lane_agility_time, three_quarter_sprint_time, bmi)
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
    

def main():
    initalize_players()


if __name__ == "__main__":
    main()