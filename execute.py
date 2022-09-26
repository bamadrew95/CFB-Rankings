from fetchGames import FetchGames
from fetchTeams import FetchTeams
from compileSchedules import CompileSchedules
from checkScheduleIntegrity import ScheduleCheck
from compileRatings import CompileRatings

######################### RUN PROGRAM FILES #########################``
fetch_games = FetchGames()
fetch_teams = FetchTeams()
compile_schedules = CompileSchedules()
check_schedules = ScheduleCheck()
compile_ratings = CompileRatings('all', 2000) # arg1 = how many weeks to calc ('all' for entire season), arg2 = Number of iterations
