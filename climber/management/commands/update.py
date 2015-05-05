from django.core.management.base import BaseCommand
from django.utils import timezone
from climber.models import *
from stravalib.client import Client

class Command(BaseCommand):
	def handle(self, *args, **options):
		client = Client()
		client.access_token = '20bf9e2864c1411d17d9cab8c11aa8dbe626aedd'
		for city in City.objects.all():
			updater = CityLeaderboardUpdater(city, client)
			updater.update()


class CityLeaderboardUpdater:
	# Generates full city leaderboard based on segment leaderboards
	def update(self):
		citySegments = Segment.objects.filter(city=self.city.name)
		allUpdatedAthletes = []
		for segment in citySegments:
			slu = SegmentLeaderboardUpdater(segment, self.client)
			slu.update()
			# Concatenate athlete lists without duplicates
			allUpdatedAthletes = list(set(allUpdatedAthletes)|set(slu.getUpdatedAthletes()))

		# Recalculate overall scores for athletes with updated segment times
		if allUpdatedAthletes != []:
			for athlete in allUpdatedAthletes:
				newScore = self.calculateScore(athlete.id)
				self.updateCityScore(athlete, newScore)
			self.updateCityRanks()
		self.removeOldPlacementChanges()
		print(AthleteCityScore.objects.filter(city=self.city.name).order_by('cityScore')[0])

	def calculateScore(self, athleteId):
		overallScore = 0
		segmentPlacements = AthleteSegmentScore.objects.raw(
					'''SELECT s.id, s.segmentScore
					   FROM   climber_athletesegmentscore s, climber_segment seg
					   WHERE  s.segmentId_id = seg.id and seg.city_id = %s and s.athleteId_id = %s
					''', [self.city.name, athleteId])
		for placement in segmentPlacements:
			overallScore += placement.segmentScore
		return overallScore

	def updateCityScore(self, athlete, newScore):
		oldPlacement = AthleteCityScore.objects.filter(athleteId=athlete, city=self.city.name)
		if len(oldPlacement) < 1:
			acs = AthleteCityScore(athleteId=athlete, city=self.city, cityScore=newScore, 
								   rank=-1)
			acs.save()
		else:
			oldPlacement[0].cityScore = newScore
			oldPlacement[0].save()

	def updateCityRanks(self):
		newLeaderboard = AthleteCityScore.objects.filter(city=self.city.name).order_by('-cityScore')
		for i, entry in enumerate(newLeaderboard):
			if entry.rank != (i+1):
				print("Changed rank " + str(entry) + " to " + str(i+1))
				self.changeRank(entry, i+1)

	def changeRank(self, entry, newRank):
		self.recordPlacementChange(entry, newRank)
		entry.rank = newRank
		entry.save()

	def recordPlacementChange(self, scoreEntry, newRank):
		pc = PlacementChange(athleteId=scoreEntry.athleteId, city=self.city,
							 oldRank=scoreEntry.rank, newRank=newRank, changeDate=timezone.now())
		pc.save()

	def removeOldPlacementChanges(self):
		placementChanges = PlacementChange.objects.all()
		for pc in placementChanges:
			if pc.isOutOfDate():
				pc.delete()

	def __init__(self, city, client):
		self.city = city
		self.client = client


class SegmentLeaderboardUpdater:
	# Update database with individual segment leaderboard from Strava
	def update(self):
		leaderboards = []
		for page in range(1, self.leaderboardPageNum + 1):
			leaderboard = self.client.get_segment_leaderboard(self.segment.id,
									top_results_limit=200, timeframe='this_year', page=page)
			leaderboards.append(leaderboard)
			# Stop querying if we've reached entry limit
			if leaderboard.entry_count < page * 200:
				break
		self.updatedAthletes = []
		for leaderboard in leaderboards:
			self.updateLeaderboard(leaderboard)

	def updateLeaderboard(self, leaderboard):
		for athlete in leaderboard:
			# Ignore the "contextual" athlete scores around the account which registered the app
			if athlete.rank > self.leaderboardPageNum * 200:
				break

			# Get existing athlete data from database, if possible
			oldAthleteScore = AthleteSegmentScore.objects.filter(athleteId=athlete.athlete_id, 
																segmentId=self.segment.id)

			# Add new or improved athlete and segment score to database
			if len(oldAthleteScore) < 1:
				newAthlete = self.addAthlete(athlete, leaderboard.entry_count)
				self.addAthleteSegmentScore(newAthlete, athlete, leaderboard.entry_count)
				self.updatedAthletes.append(newAthlete)
			elif (oldAthleteScore[0].segmentTime != athlete.elapsed_time.total_seconds()):
				self.updateAthleteSegmentScore(oldAthleteScore[0], athlete, 
											   leaderboard.entry_count)
				self.updatedAthletes.append(oldAthleteScore[0].athleteId)

	# Adds new athlete to database, plus their score for the given segment
	def addAthlete(self, athlete, totalEfforts):
		# Male is the default gender internally to make it easier
		if athlete.athlete_gender is None:
			athlete.athlete_gender = 'M'
		# Add athlete entry to our db
		a = Athlete(id=athlete.athlete_id, name=athlete.athlete_name, 
					gender=athlete.athlete_gender)
		a.save()
		return a

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
		oldAthleteScore.save()
		
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
		# All athletes who were recently added or whose segment times were updated
		self.updatedAthletes = []
		# Number of athlete scores we keep track of (x * 200)
		self.leaderboardPageNum = 5
