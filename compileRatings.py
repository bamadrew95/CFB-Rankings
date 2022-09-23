import json
import pandas as pd
from config import year, Team, Game
from pprint import pprint

class CompileRatings:
  def __init__(self, week_to_calc, postseason):
    # Define attributes
    self.week = week_to_calc
    self.post = postseason
    self.teams = []

    # Run methods
    self.open_files()
    self.create_teams()
    self.create_sched_df()
    self.create_ratings_df()
    self.calculate_ratings()

###################### DEFINE METHODS ######################
  def open_files(self):
    f = open('data/schedules/' + str(year) + 'schedules.json')
    self.teams_json_data = json.load(f)

# Instantiate teams
  def create_teams(self):
    for team_data in self.teams_json_data:
      team_schedule = self.create_schedule(team_data)
      team = Team(team_data['id'], team_data['team'], team_data['classification'], team_data['conference'], team_schedule)
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

  def create_sched_df(self) -> pd.DataFrame():
    """
    Returns:
      dataframe: 
    """
    for team in self.teams:
      # print(vars(team.sched))
      game_list = []
      for game_obj in team.sched:
        game_dict = {}
        if game_obj.week <= self.week and game_obj.season_type != 'postseason':
          self._add_game(game_dict, game_obj, game_list, team)
        if self.post and game_obj.season_type == 'postseason':
          self._add_game(game_dict, game_obj, game_list, team)

      # Create a dataframe for each team's schedule
      df = pd.DataFrame(game_list)
      df['margin'] = df['team_score'] - df['opp_score']
      team.sched_df = df
  
  # Add game and all pertinent info to game_dict and append to game_list
  def _add_game(self, game_dict, game_obj, game_list, team_obj):
    game_dict['team_id'] = team_obj.team_id
    game_dict['opp_id'] = game_obj.opp_id
    game_dict['team_score'] = game_obj.team_score
    game_dict['opp_score'] = game_obj.opp_score
    game_dict['location'] = game_obj.location
    game_list.append(game_dict)

  def create_ratings_df(self):
    """
    Create DataFrame that contains only team ratings, column names are Team IDs
    """
    column_ids = []
    team_ratings = []
    for team in self.teams:
      column_ids.append(team.team_id)
      team_ratings.append(team.initial_rating)
      
    df = pd.DataFrame([team_ratings], columns=column_ids)
    df[0] = 0

    self.team_ratings_df = df


  def calculate_ratings(self):
    """
    Where the rubber meets the road. Iterates through the team.sched_df and team_ratings_df to compile a final rating for the given week.
    Stores final ratings in each team's obj (team.final_rating)
    """

    for team in self.teams:
      
      for week in range(self.week + 1):
        for y in range(5):
          # Gather current ratings
          team.sched_df.at[week, 'team_prev_rating'] = self.team_ratings_df.at[0, team.team_id]
          if team.sched_df.isnull().values.any(): # Make sure there are no NaN values
            team.sched_df.fillna(0, inplace=True)
          team.sched_df.at[week, 'opp_rating'] = self.team_ratings_df.at[0, team.sched_df.at[week, 'opp_id']]
          
          # Calc Prdeicted performance, actual performance, and elo adj
          team.sched_df['predicted_performance'] = 1 / (1 + (10 ** ((team.sched_df['opp_rating'] - team.sched_df['team_prev_rating']) / 30)))
          team.sched_df['actual_performance'] = 1 / (1 + (10.0 ** (-team.sched_df['margin'] / 28)))
          team.sched_df['elo_adj'] = (team.sched_df['actual_performance'] - team.sched_df['predicted_performance']) * 15
          # Add elo adj to previous rating for resulting rating and Assign new rating to team rating dataframe
          if team.sched_df.at[week, 'opp_id'] != 0:
            team.sched_df.at[week, 'result_rating'] = team.sched_df.at[week, 'team_prev_rating'] + team.sched_df.at[week, 'elo_adj']
            self.team_ratings_df.at[0, team.team_id] = team.sched_df.at[week, 'result_rating'] # Assign new rating to team rating dataframe
          else:
            team.sched_df.at[week, 'result_rating'] = team.sched_df.at[week, 'team_prev_rating']

    print(self.team_ratings_df)

          

  def _calc_elo_adjust(self, team, week):
    """
    team_rat, opp_rat, margin, loc
    """
    HOME_FIELD_ADV = 3.2142858
    my_df = team.df

    def actual_perf(margin, x):
      data = 1 / (1 + (10 ** (-margin / 28)))
      my_df['actual_perf'][week] = data
      # return data

    def predicted_perf(team_rat, opp_rat, loc):
      data = 1 / (1 + (10 ** ((opp_rat - team_rat) / 30)))
      if loc == 1:
        data -= HOME_FIELD_ADV
      elif loc == 0:
        data += HOME_FIELD_ADV
      my_df['predicted_perf'][week] = data
      # return data
    
    def calc_elo_adj(actual_perf, predicted_perf):
      elo_adj = (actual_perf - predicted_perf) * 15
      return elo_adj



test = CompileRatings(20, True)
# for team in test.teams:
#   print(team.final_rating)