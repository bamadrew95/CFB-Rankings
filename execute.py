from fetchGames import FetchGames
from fetchTeams import FetchTeams
from compileSchedules import CompileSchedules
from checkScheduleIntegrity import ScheduleCheck
from compileRatings import CompileRatings

YEAR = 2004

######################### RUN PROGRAM FILES #########################
# fetch_games = FetchGames(YEAR)
# fetch_teams = FetchTeams(YEAR)
compile_schedules = CompileSchedules(YEAR)
check_schedules = ScheduleCheck(YEAR)
compile_ratings = CompileRatings(YEAR, 'all', 2000) # arg1 = how many weeks to calc ('all' for entire season), arg2 = Number of iterations
