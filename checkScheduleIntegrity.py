import json
from config import YEAR, PROJECT_PATH

year = YEAR

class ScheduleCheck:
    """
    """

    def __init__(self):
        """
        """
        # Schedules file
        f = open('data/schedules/' + str(year) + 'schedules.json')
        self.schedules_dict = json.load(f)
        self.run()
    
    def run(self):
        """
        """
        self.check_week_increments()
        self.check_season_lengths()
        self.print_number_of_team()
    
    def check_week_increments(self):
        """
        Check that all teams have a weeks numbered sequentially.
        """
        for team in self.schedules_dict:
            counter = 0
            for game in team['reg_game_data']:
                try:
                    assert(game['week'] == counter)
                except AssertionError:
                    print(f"Error on { team['team'] }'s schedule at week { counter }.")
                counter += 1
    
    def check_season_lengths(self):
        """
        Checks len 
        """
        length = len(self.schedules_dict[0]['reg_game_data'])

        for team in self.schedules_dict:
            try:
                assert(length == len(team['reg_game_data']))
            except AssertionError:
                print(f"Error with {team['team']}'s season length. They have { len(team['reg_game_data']) } games listed.")
    
    def print_number_of_team(self):
        """
        Notifies the user how many teams are included.
        """
        print(f"{ len(self.schedules_dict) } schedules checked.")