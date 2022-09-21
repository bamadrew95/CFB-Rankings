import json
import xlsxwriter
from config import year

class CompileSchedules:
  def __init__(self):
    # Define attributes
    self.all_team_schedules = [] # Used to hold list of all teams' schedules, active or inactive
    self.teams = [] # Used in filtering FBS teams
    self.games = [] # Used in compiling game data for each team

    # Run methods
    self.open_files()
    self.initialize_team_schedule()
    self.find_active_teams()
    self.correct_week_0()
    self.insert_bye_weeks()
    self.correct_season_length() 
    self.define_null_conf()
    self.write_json()
    # self.write_xlsx() ############# Uncomment this to write data to XLSX format #############

########################### BEGIN METHODS ###########################

  def open_files(self):
    f = open('data/teams/' + str(year) + 'teams.json')
    self.teams_dict = json.load(f)

    f = open('data/games/' + str(year) + 'games.json')
    self.games_dict = json.load(f)

  # 1 = win, 0 = loss, tie = 0.5
  def eval_game_result(self, home, game_data):
    if home == 1:
      if game_data['_home_points'] > game_data['_away_points']:
        return 1
      elif game_data['_home_points'] < game_data['_away_points']:
        return 0
      else:
        return 0.5
    else:
      if game_data['_home_points'] > game_data['_away_points']:
        return 0
      elif game_data['_home_points'] < game_data['_away_points']:
        return 1
      else:
        return 0.5
  
  # 0.5 = neutral site, 1 = home, 0 = away
  def determine_location(self, team_id, game_data):
    if game_data['_neutral_site'] == True:
      return 0.5
    elif game_data['_home_id'] == team_id:
      return 1
    else:
      return 0
  
  # True = Game has been played, False = Game has not been played yet
  def completed_game(self, game_data):
    if game_data['_home_points'] == None or game_data['_away_points'] == None:
      return False
    else:
      return True

  def initialize_team_schedule(self):
    for team in self.teams_dict:
      team_data = {}
      team_data['id'] = team['id']
      team_data['team'] = team['team']
      team_data['year'] = year
      team_data['classification'] = team['classification']
      team_data['conference'] = team['conference']
      team_data['reg_game_data'] = []
      team_data['post_game_data'] = []

      for game in self.games_dict:
        if self.completed_game(game):
          if game['_home_id'] == team['id'] or game['_away_id'] == team['id']:
            game_data = {}
            game_data['game_id'] = game['_id']
            game_data['week'] = game['_week']

            if game['_home_id'] == team['id']:
              game_data['opp_id'] = game['_away_id']
              game_data['opp'] = game['_away_team']
              game_data['team_score'] = game['_home_points']
              game_data['opp_score'] = game['_away_points']
              game_data['result'] = self.eval_game_result(1, game)
            else:
              game_data['opp_id'] = game['_home_id']
              game_data['opp'] = game['_home_team']
              game_data['team_score'] = game['_away_points']
              game_data['opp_score'] = game['_home_points']
              game_data['result'] = self.eval_game_result(0, game)
            game_data['loc'] = self.determine_location(team['id'], game)
            game_data['season_type'] = game['_season_type']
            if game_data['season_type'] == 'regular':
              team_data['reg_game_data'].append(game_data)
            else:
              team_data['post_game_data'].append(game_data)
      self.all_team_schedules.append(team_data)
  
  # Make sure teams have actually played games that year
  def find_active_teams(self):
    self.active_team_schedules = []

    for sched in self.all_team_schedules:
      if sched['reg_game_data'] != []:
        self.active_team_schedules.append(sched)
  
  # Ensure week 0 games display correctly
  def correct_week_0(self):    
    
    for team in self.active_team_schedules:
      try:
        if team['reg_game_data'][0]['week'] == 1 and team['reg_game_data'][1]['week'] == 1:
          team['reg_game_data'][0]['week'] = 0
      except:
        continue
  
  def check_week(self, x, team_data):
    null_game = {
      'game_id': None,
      'week': x,
      'opp_id': None,
      'opp': None,
      'team_score': None,
      'opp_score': None,
      'result': None,
      'loc': None,
      'season_type': 'regular'
    }
    try:
      if team_data['reg_game_data'][x]['week'] != x and team_data['reg_game_data'][x]['season_type'] != 'postseason':
        team_data['reg_game_data'].insert(x, null_game)
    except:
      exit
  
  # Insert NULL game for BYE week
  def insert_bye_weeks(self):
    for team_data in self.active_team_schedules:
      x = 0
      while x < 20:
        self.check_week(x, team_data)
        x += 1

  # Append NULL game to end of season
  def append_game(self, x, team_data):
    null_game = {
      'game_id': None,
      'week': x,
      'opp_id': None,
      'opp': None,
      'team_score': None,
      'opp_score': None,
      'result': None,
      'loc': None,
      'season_type': 'regular'
    }
    team_data['reg_game_data'].append(null_game)

  # Add NULL games up to make every teams' regular season 16 games long
  def correct_season_length(self):
    for team_data in self.active_team_schedules:
      season_length = len(team_data['reg_game_data'])
      if season_length < 17:
        for i in range(season_length, 17):
          self.append_game(i, team_data)
  
  # Assign NULL conference dict keys the value 'unknown'
  def define_null_conf(self):
    for team_data in self.active_team_schedules:
      if team_data['classification'] == None:
        team_data['classification'] = 'unknown'
      if team_data['conference'] == None:
        team_data['conference'] = 'unknown'
  
  # Write data to JSON file
  def write_json(self):
    json_object = json.dumps(self.active_team_schedules, indent=4)

    with open('data/schedules/' + str(year) + 'schedules.json', 'w') as outfile:
      outfile.write(json_object)
  
  def write_xlsx(self):
    # Open JSON file
    f = open('data/schedules/' + str(year) + 'schedules.json')
    schedules_dict = json.load(f)

    # Prep data for XLS
    XLS_team_data = []

    for team_data in schedules_dict:
      team_data_list = []
      # print(f"{team}\n")
      team_data_list.append(team_data['id'])
      team_data_list.append(team_data['team'])
      team_data_list.append(team_data['year'])
      team_data_list.append(team_data['classification'])
      team_data_list.append(team_data['conference'])

      for game_data in team_data['reg_game_data']:
        for k in game_data:
          team_data_list.append(game_data[k])
      
      for game_data in team_data['post_game_data']:
        for k in game_data:
          team_data_list.append(game_data[k])

      XLS_team_data.append(team_data_list)

    # Insert top row labels
    xls_columns = ['id', 'team', 'year', 'classification', 'conference']
    game_columns = ['game id', 'week', 'opp', 'team score', 'opp score', 'result', 'location', 'season type']

    for i in range(21):
      for item in game_columns:
        xls_columns.append(item)

    XLS_team_data.insert(0, xls_columns)
    
    workbook = xlsxwriter.Workbook('data/excel/' + str(year) + 'data.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0

    for team in XLS_team_data:
      col = 0
      for item in team:
        worksheet.write(row, col, item)
        col += 1
      row += 1

    workbook.close()