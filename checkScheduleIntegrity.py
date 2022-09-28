import json

class ScheduleCheck:
    """
    """

    def __init__(self, YEAR):
        """
        """
        self.year = YEAR
        self.error = 0
        self.run()
        
    
    def run(self):
        """
        """
        print(f'Checking schedule integrity for { self.year }...')
        self.open_file()
        self.check_week_increments()
        self.check_season_lengths()
        self.check_for_errors()
        self.completion_message()

    def open_file(self):
        f = open('data/schedules/' + str(self.year) + 'schedules.json')
        self.schedules_dict = json.load(f)
    
    def check_week_increments(self):
        """
        Check that all teams have a weeks numbered sequentially.
        """
        for team in self.schedules_dict:
            counter = 0
            for game in team['reg_game_data']:
                if game['week'] != counter:
                    print(f"Error on { team['team'] }'s schedule at week { counter }.")
                    self.error += 1
                counter += 1
    
    def check_season_lengths(self):
        """
        Checks schedule length and compares with first team's schedule length
        """
        length = len(self.schedules_dict[0]['reg_game_data'])

        for team in self.schedules_dict:
            if length != len(team['reg_game_data']):
                print(f"Error with {team['team']}'s season length. They have { len(team['reg_game_data']) } games listed.")
                self.error += 1
    
    def check_for_errors(self):
        assert self.error == 0, str(self.error) + ' schedule error(s) found.'

    def completion_message(self):
        print(f"{ len(self.schedules_dict) } schedules checked. No errors found.")