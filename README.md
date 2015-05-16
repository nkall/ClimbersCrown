# ClimbersCrown
Files worth reading:
* `climber/models.py`: Database schema setup
* `climber/management/commands/update.py`: Cron job that pulls current data from Strava and updates leaderboards (most important part)
* `climber/views.py`: Pulls leaderboards from model and serves them to podium template
* `climber/templates/climber/podium/index.html`: "View" (template) for the leaderboards
