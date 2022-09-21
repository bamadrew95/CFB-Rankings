from pathlib import Path
import cfbd
from cfbd.rest import ApiException
import json
from execute import year

api_key = 'YOUR_API_KEY_HERE'

PROJECT_PATH = Path(Path.cwd())

##################### CONFIGURE API CLASS #####################

class CFBDApi():
  """
  """
  def __init__(self):
    self.configuration = cfbd.Configuration()
    self.configuration.api_key['Authorization'] = api_key
    self.configuration.api_key_prefix['Authorization'] = 'Bearer'
    self.year = year
  
########################### BEGIN METHODS ###########################

  def games(self):
    games_api_instance = cfbd.GamesApi(cfbd.ApiClient(self.configuration))
    
    try:
      game_data = games_api_instance.get_games(year=self.year, season_type="regular")
    except ApiException as e:
      print("Error accessing game info: %s\n" % e)

    try:
      get_games_api_response = games_api_instance.get_games(year=self.year, season_type="postseason")
      for game_item in get_games_api_response:
        game_data.append(game_item)
      return game_data

    except ApiException as e:
      print("Error accessing game info: %s\n" % e)

  def teams(self):
    teams_api_instance = cfbd.TeamsApi(cfbd.ApiClient(self.configuration))
    try:
      team_data = teams_api_instance.get_teams()
      return team_data

    except ApiException as e:
      print("Error accessing TeamsApi->get_teams: %s\n" % e)

class Game:
  def __init__(self, game_id, week, opp_id, opp, team_score, opp_score, game_result, location, season_type):
    self.game_id = game_id
    self.week = week
    self.opp_id = opp_id
    self.opp = opp
    self.team_score = team_score
    self.opp_score = opp_score
    self.game_result = game_result
    self.location = location
    self.season_type = season_type

class Team:
  def __init__(self, team_id, team, classification, conf, sched):
    self.team_id = team_id
    self.team = team
    self.classification = classification
    self.conf = conf
    self.sched = sched

    # Run Methods
    self.assign_initial_rating()

  # Assign inital rating if no past rating exists
  def assign_initial_rating(self):
    prev_year = year - 1
    try:
      f = open('data/ratings/' + str(prev_year) + 'ratings.json')
      team_ratings_list = json.load(f)

      for team_data in team_ratings_list:
        if team_data['team_id'] == self.team_id:
          self.initial_rating = team_data['final_rating']
    except:
      if self.classification == 'fbs':
        self.initial_rating = float(50)
      elif self.classification == 'fcs':
        self.initial_rating = float(10)
      elif self.classification == 'ii':
        self.initial_rating = float(0)
      elif self.classification == 'iii':
        self.initial_rating = float(-10)
      else:
        self.initial_rating = float(0)
