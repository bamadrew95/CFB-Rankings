from config import CFBDApi
import json
from config import year

class FetchTeams:
  def __init__(self):
    self.api_call()
    self.open_games_file()
    self.create_teams_list()
    self.write_json()

########################### BEGIN METHODS ###########################

  def api_call(self):
    self.team_data = CFBDApi().teams()
  
  def open_games_file(self):
    f = open('data/games/' + str(year) + 'games.json')
    self.game_data = json.load(f)

  def create_teams_list(self):
    self.team_dict_list = []

    for team in self.team_data:
      team_dict = {}
      team_dict['id'] = team.id
      team_dict['team'] = team.school
      # Add class and conf from Game file (This causes them to be correct according to the year)
      for game in self.game_data:
        if team_dict['id'] == game['_home_id']:
          team_dict['classification'] = game['_home_division']
          team_dict['conference'] = game['_home_conference']
          self.team_dict_list.append(team_dict)
          break
        elif team_dict['id'] == game['_away_id']:
          team_dict['classification'] = game['_away_division']
          team_dict['conference'] = game['_away_conference']
          self.team_dict_list.append(team_dict)
          break
  
  # WRITE DATA TO JSON FILE
  def write_json(self):
    json_object = json.dumps(self.team_dict_list, indent=4)

    with open('data/teams/' + str(year) + 'teams.json', 'w') as outfile:
      outfile.write(json_object)