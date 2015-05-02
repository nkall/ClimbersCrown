from django.core.management.base import BaseCommand
from climber.models import *
from stravalib.client import Client


STRAVA_CLIENT_ID='5802'
STRAVA_CLIENT_SECRET=''

class Command(BaseCommand):
	def handle(self, *args, **options):
		client = Client()
		client.access_token = '20bf9e2864c1411d17d9cab8c11aa8dbe626aedd'

		cities = [city.name for city in City.objects.all()]
		for city in cities:
			updater = LeaderboardUpdater(city, client)
			updater.update()

class LeaderboardUpdater:
	def update(self):
		self.generateLeaderboard()

	# Generates full city leaderboard based on segment leaderboards
	def generateLeaderboard(self):
		citySegments = Segment.objects.filter(city=self.cityName)
		segmentLeaderboards = [self.client.get_segment_leaderboard(segment.id)
								for segment in citySegments]
		for leaderboard in segmentLeaderboards:
			


	# Retrieves individual segment leaderboard from Strava
	def retrieveSegmentLeaderboard(self, segmentId):
		pass

	def __init__(self, cityName, client):
		self.cityName = cityName
		self.client = client
