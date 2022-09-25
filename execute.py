from fetchGames import FetchGames
from fetchTeams import FetchTeams
from compileSchedules import CompileSchedules
from checkScheduleIntegrity import ScheduleCheck
from compileRatings import CompileRatings

######################### RUN PROGRAM FILES #########################``
# fetch_games = FetchGames()
# fetch_teams = FetchTeams()
# compile_schedules = CompileSchedules()
# check_schedules = ScheduleCheck()
compile_ratings = CompileRatings(16, True) # arg1 = how many weeks to calc, arg2 = True to include postseason games
