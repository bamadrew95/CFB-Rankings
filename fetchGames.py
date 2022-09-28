from config import CFBDApi
import json

##################### DEFINE CLASS #####################
class FetchGames:
  def __init__(self, YEAR):
    self.year = YEAR
    print('Initiaing Games API call...')
    self.api_call()
    self.compile_json_data()
    self.write_json()
    self.completion_message()

########################### BEGIN METHODS ###########################

  # API CALL METHOD
  def api_call(self):
    self.game_data = CFBDApi(self.year).games()
  
  # COMPILE GAME DATA INTO JSON FORMAT
  def compile_json_data(self):
    self.game_dicts_list = []

    for game in self.game_data:
      del game._configuration
      del game._start_time_tbd
      del game._attendance
      del game._venue_id
      del game._venue
      del game._home_line_scores
      del game._home_post_win_prob
      del game._home_pregame_elo
      del game._home_postgame_elo
      del game._away_line_scores
      del game._away_post_win_prob
      del game._away_pregame_elo
      del game._away_postgame_elo
      del game._excitement_index
      del game._highlights
      del game._notes
      del game.discriminator
      self.game_dicts_list.append(game.__dict__)

    # WRITE DATA TO JSON FILE
  def write_json(self):
    json_object = json.dumps(self.game_dicts_list, indent=4)

    with open('data/games/' + str(self.year) + 'games.json', 'w') as outfile:
      outfile.write(json_object)
    
  def completion_message(self):
    print('FetchGames module completed succesfully.')