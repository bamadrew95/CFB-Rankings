import json
from config import year, Team, Game

class CompileRatings:
  def __init__(self, week_to_calc, postseason):
    # Define attributes
    self.week = week_to_calc
    self.post = postseason
    self.teams = []

    # Run methods
    self.open_files()
    self.create_teams()
    self.calc_ratings()
    # self.test()

###################### DEFINE METHODS ######################
  def open_files(self):
    f = open('data/schedules/' + str(year) + 'schedules.json')
    self.teams_json_data = json.load(f)

# Instantiate teams
  def create_teams(self):
    for team_data in self.teams_json_data:
      team_sched = self.create_schedule(team_data)
      team = Team(team_data['id'], team_data['team'], team_data['classification'], team_data['conference'], team_sched)
      self.teams.append(team)

  # Compile list of game objs for each team schudule
  def create_schedule(self, team_data):
    team_schedule = []
    reg_season_games = team_data['reg_game_data']
    post_season_games = team_data['post_game_data']

    for reg_game in reg_season_games:
      game_obj = Game(reg_game['game_id'], reg_game['week'], reg_game['opp_id'], reg_game['opp'], reg_game['team_score'], reg_game['opp_score'], reg_game['result'], reg_game['loc'], reg_game['season_type'])
      team_schedule.append(game_obj)
    for post_game in post_season_games:
      game_obj = Game(post_game['game_id'], post_game['week'], post_game['opp_id'], post_game['opp'], post_game['team_score'], post_game['opp_score'], post_game['result'], post_game['loc'], post_game['season_type'])
      team_schedule.append(game_obj)
    return team_schedule
  
  def calc_ratings(self):
    for x in range(self.week):
      for y in range(2000):
        for team_data in self.teams:
          for game_data in team_data.sched:
            if game_data.week == x:
              self.calc_game_result(game_data, team_data)

  def calc_game_result(self, game_data, team_data):
    if game_data.game_id != None:
      margin = self.calc_margin(game_data)
      opp_rat = self.find_opp_rat(game_data)
      elo_adj = self.calc_elo_adj(team_data.current_rating, opp_rat, margin)
      self.adj_rating(elo_adj, team_data)

  def calc_margin(self, game_data):
    margin = game_data.team_score - game_data.opp_score
    return margin

  def find_opp_rat(self, game_data):   
    for team_data in self.teams:
      if hasattr(team_data, 'current_rating') == False:
        team_data.current_rating = team_data.initial_rating

      if team_data.team_id == game_data.opp_id:
        opp_rat = team_data.current_rating
        return opp_rat
  
  def calc_elo_adj(self, team_rat, opp_rat, margin):
    raw_perf = self.calc_raw_perf(margin)
    pred_perf = self.calc_pred_perf(team_rat, opp_rat)

    elo_adj = round((raw_perf - pred_perf) * 15, 12)
    return elo_adj

  def adj_rating(self, elo_adj, team_data):
    team_data.current_rating = team_data.current_rating + elo_adj
  
  def calc_raw_perf(self, margin):
    a = round(-margin / 28, 11)
    b = round(10 ** a, 13)
    c = round(1 + b, 13)
    raw_perf = round(1 / c, 13)
    return raw_perf

  def calc_pred_perf(self, team_rat, opp_rat):
    a = round(opp_rat - team_rat / 28, 11)
    b = round(a / 30, 13)
    c = round(10 ** b, 13)
    d = round(1 + c, 13)
    pred_perf = round(1 / d, 13)
    return pred_perf