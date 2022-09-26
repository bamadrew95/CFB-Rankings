import json
import pandas as pd
import numpy as np
from config import YEAR, Team, Game
from pprint import pprint
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning) # Gets rid of warnings from pd about performance thrown by py.where

year = YEAR

class CompileRatings:
  def __init__(self, week_to_calc, iterations):
    # Define attributes
    self.iterations = iterations
    self.teams = []

    # Run methods
    self.open_files()
    self.create_teams()
    self.set_week_num(week_to_calc)
    self.create_df()
    self.calculate_ratings()
    self.write_ratings_to_json()

###################### DEFINE METHODS ######################
  def open_files(self):
    f = open('data/schedules/' + str(year) + 'schedules.json')
    self.teams_json_data = json.load(f)

  def set_week_num(self, week_to_calc):
    self.weeks_in_season = len(self.teams_json_data[0]['reg_game_data']) + len(self.teams_json_data[0]['post_game_data'])
    if week_to_calc == 'all':
      self.week = self.weeks_in_season
    elif week_to_calc > self.weeks_in_season:
      raise ValueError('There are only ' + str(self.weeks_in_season) + ' weeks in this year\'s season. Try a smaller week number or put \'all\' to calculate the entire season.')
    else:
      self.week = week_to_calc
    
# Instantiate teams
  def create_teams(self):
    for team_data in self.teams_json_data:
      team_schedule = self._create_schedule(team_data)
      team = Team(team_data['id'], team_data['team'], team_data['classification'], team_data['conference'], team_schedule)
      team.rating_results = []
      self.teams.append(team)

    # Compile list of game objs for each team's schedule
  def _create_schedule(self, team_data):
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
  
  def create_df(self):
    year_data = []
    for team in self.teams:
      team_data = {}
      # Add info that is pertinent to this team here (is not unique to week)
      team_data['team_id'] = team.team_id
      team_data['team'] = team.team
      team_data['classification'] = team.classification
      team_data['conference'] = team.conf
      team_data['team_rating'] = team.initial_rating
      team_data['wins'] = 0
      team_data['losses'] = 0
      team_data['games_played'] = 0
      # Build data for each week in corresponding labels
      for week in range(self.week):
        week_label = 'week' + str(week) + '_'
        team_data[week_label + 'opp_id'] = team.sched[week].opp_id
        team_data[week_label + 'opp'] = team.sched[week].opp
        team_data[week_label + 'team_score'] = team.sched[week].team_score
        team_data[week_label + 'opp_score'] = team.sched[week].opp_score
        team_data[week_label + 'result'] = team.sched[week].game_result
        team_data[week_label + 'season_type'] = team.sched[week].season_type
        if team.sched[week].location == 1:
          team_data[week_label + 'home_adv'] = -3.2142858
        elif team.sched[week].location == 0.5:
          team_data[week_label + 'home_adv'] = 0
        else:
          team_data[week_label + 'home_adv'] = 3.2142858
      year_data.append(team_data)
    # Create a dataframe for the entire year's schedule
    self.df = pd.DataFrame(year_data)
    self.df.set_index('team_id', inplace=True)

    for week in range(self.week):
      week_label = 'week' + str(week) + '_'
      self.df[week_label + 'bye'] = np.where(self.df[week_label + 'opp_id'] == 0, True, False)
      self.df[week_label + 'margin'] = self.df[week_label + 'team_score'] - self.df[week_label + 'opp_score']

  def calculate_ratings(self):
    self.ratings_list = []
    for week in range(self.week):
      week_ratings = []
      week_label = 'week' + str(week) + '_'
      # Everything done once at the beginning of week
      self.df[week_label + 'team_rating'] = self.df['team_rating']

      for team in self.teams:
        opp_id = self.df._get_value(team.team_id, week_label + 'opp_id')
        self.df.at[team.team_id, week_label + 'opp_rating'] = self.df._get_value(opp_id, 'team_rating')
      
      # Everything iterated through 100 times per week
      for x in range(self.iterations):

        # Predicted Performance
        self.df[week_label + 'pred_perf'] = 1 / (1 + (10 ** (((self.df[week_label + 'opp_rating'] + self.df[week_label + 'home_adv']) - self.df[week_label + 'team_rating']) / 42)))
        # Actual Performance
        self.df[week_label + 'actual_perf'] = 1 / (1 + (10 ** (-self.df[week_label + 'margin'] / 42)))
        # Elo Adjustment
        self.df[week_label + 'elo_adj'] = np.where(self.df[week_label + 'bye'], 0, (self.df[week_label + 'actual_perf'] - self.df[week_label + 'pred_perf']) * 10)
        # Adjust ratings
        self.df[week_label + 'team_rating'] = self.df[week_label + 'team_rating'] + self.df[week_label + 'elo_adj']
        self.df[week_label + 'opp_rating'] = self.df[week_label + 'opp_rating'] - self.df[week_label + 'elo_adj']
        # Assign new rating as team_rating
        self.df['team_rating'] = self.df[week_label + 'team_rating']
      
      # Store week results in dict
      week_ratings = self.df['team_rating'].to_dict()
      # Run function to assign these rating to team objects
      for team in self.teams:
        team.rating_results.append(week_ratings[team.team_id])
    
  def write_ratings_to_json(self):
    for week in range(self.week):
      week_label = 'week' + str(week) + '_rating'
      week_rating_data = []
      for team in self.teams:
        team_dict = {}
        team_dict['team_id'] = team.team_id
        team_dict['team'] = team.team
        team_dict['rating'] = team.rating_results[week]
        team_dict['classification'] = team.classification
        team_dict['conference'] = team.conf
        week_rating_data.append(team_dict)
      
       # Write data to JSON file
      json_object = json.dumps(week_rating_data, indent=4)
      if week < 20:
        with open('data/ratings/' + str(year) + '/week' + str(week) + '_ratings.json', 'w') as outfile:
          outfile.write(json_object)
      else:
        with open('data/ratings/' + str(year) + '/' + str(year) + 'final_ratings.json', 'w') as outfile:
          outfile.write(json_object)