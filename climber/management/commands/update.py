from django.core.management.base import BaseCommand
from climber.models import *
from stravalib.client import Client

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
		self.updateLeaderboard()

	# Generates full city leaderboard based on segment leaderboards
	def updateLeaderboard(self):
		citySegments = Segment.objects.filter(city=self.cityName)
		allUpdatedAthletes = []
		for segment in citySegments:
			slu = SegmentLeaderboardUpdater(segment, self.client)
			slu.update()
			# Concatenate athlete lists without duplicates
			allUpdatedAthletes = list(set(allUpdatedAthletes)|set(slu.getUpdatedAthletes()))

		# TODO: Recalculate overall scores for athletes with updated segment times
		for athlete in allUpdatedAthletes:
			print(athlete)

	# TODO
	def updateScore(self):
		pass

	# TODO
	def recordPlacementChange(self, oldAthleteData, athlete):
		pass

	def __init__(self, cityName, client):
		self.cityName = cityName
		self.client = client


class SegmentLeaderboardUpdater:
	# Update database with individual segment leaderboard from Strava
	def update(self):
		leaderboard = self.client.get_segment_leaderboard(self.segment.id, 
									top_results_limit=self.entryLimit, timeframe='this_year')
		self.updatedAthletes = []
		for athlete in leaderboard:
			wasUpdated = True
			# Ignore the "contextual" athlete scores around the account which registered the app
			if athlete.rank > self.entryLimit:
				break

			# Get existing athlete data from database, if possible
			oldAthleteScore = AthleteSegmentScore.objects.filter(athleteId=athlete.athlete_id, 
																segmentId=self.segment.id)

			# Add new or improved athlete and segment score to database
			if len(oldAthleteScore) < 1:
				self.addSegmentAthlete(athlete, leaderboard.entry_count)
			elif (oldAthleteScore[0].segmentTime != athlete.elapsed_time.total_seconds()):
				self.updateAthleteSegmentScore(oldAthleteScore[0], athlete, 
											   leaderboard.entry_count)
			else:
				wasUpdated = False

			if wasUpdated:
				self.updatedAthletes.append(athlete.athlete_id)

	def addSegmentAthlete(self, athlete, totalEfforts):
		# Male is the default gender internally to make it easier
		if athlete.athlete_gender is None:
			athlete.athlete_gender = 'M'
		# Add athlete entry to our db
		a = Athlete(id=athlete.athlete_id, name=athlete.athlete_name, 
					gender=athlete.athlete_gender)
		a.save()
		self.addAthleteSegmentScore(a, athlete, totalEfforts)

	# Calculate score for given segment and use it to add new segment score entry
	def addAthleteSegmentScore(self, dbAthlete, apiAthlete, totalEfforts):
		score = self.calculateSegmentScore(apiAthlete.rank, totalEfforts)
		ass = AthleteSegmentScore(athleteId=dbAthlete, segmentId=self.segment,
								  effortId=apiAthlete.effort_id, activityId=apiAthlete.activity_id,
								  segmentTime=apiAthlete.elapsed_time.total_seconds(),
								  segmentScore=score)
		ass.save()

	# Calculate score for given segment and use it to update segment score entry
	# This is an ugly hack since Django doesn't allow composite keys and tries to insert instead
	def updateAthleteSegmentScore(self, oldAthleteScore, apiAthlete, totalEfforts):
		score = self.calculateSegmentScore(apiAthlete.rank, totalEfforts)
		oldAthleteScore.effortId = apiAthlete.effort_id
		oldAthleteScore.activityId = apiAthlete.activity_id
		oldAthleteScore.segmentTime = apiAthlete.elapsed_time.total_seconds()
		oldAthleteScore.segmentScore = score
		oldAthleteScore.save(update_fields=['effortId', 'activityId', 'segmentTime', 
											'segmentScore'])
		
	# Maximum points that can be earned is 1,000 for 1st place -- all other placements get a
	# score as a fraction of 1,000 based on their percentile ranking, except when this score is
	# greater than 1,001 minus their rank.
	def calculateSegmentScore(self, rank, totalEfforts):
		maxScore = 1000
		score = min(round((1 - ((rank - 1) / totalEfforts)) * maxScore), maxScore + 1 - rank)
		if score < 1:
			score = 1
		return score

	def getUpdatedAthletes(self):
		return self.updatedAthletes

	def __init__(self, segment, client):
		self.segment = segment
		self.client = client
		# IDs of all athletes who were recently added or whose segment times were updated
		self.updatedAthletes = []
		# Number of athlete scores we keep track of (top x scores)
		self.entryLimit = 50

