from django.core.management.base import BaseCommand
from django.utils import timezone
from climber.models import *
from stravalib.client import Client
import requests

class Command(BaseCommand):
	def handle(self, *args, **options):
		client = Client()
		client.access_token = '20bf9e2864c1411d17d9cab8c11aa8dbe626aedd'
		cityEntries = City.objects.all()
		resetPlaceChanges = False
		if not cityEntries:
			cityEntries = createDefaultCitySegments()
			resetPlaceChanges = True

		for city in cityEntries:
			updater = CityLeaderboardUpdater(city, client)
			updater.update()

		# Delete placement changes if data has just been reset
		if resetPlaceChanges:
			placementChanges = PlacementChange.objects.all()
			for pc in placementChanges.iterator():
				pc.delete()
		print("Updated at " + str(timezone.now()))


class CityLeaderboardUpdater:
	# Generates full city leaderboard based on segment leaderboards
	def update(self):
		self.removeOldPlacementChanges()

		updatedAthletes = []
		citySegments = Segment.objects.filter(city=self.city.name)
		try:
			for segment in citySegments:
				slu = SegmentLeaderboardUpdater(segment, self.client)
				slu.update()
				updatedAthletes += slu.getUpdatedAthletes()
			# Don't take duplicates into account
			allUpdatedAthletes = list(set(updatedAthletes))

			# Recalculate overall scores for athletes with updated segment times
			if allUpdatedAthletes:
				self.recalculateCityScores(allUpdatedAthletes)
				self.updateCityRanks()
		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
			print("Encountered error from Strava: " + str(e))
			# Recalculate overall scores for city athletes
			self.recalculateCityScores(self.getCityAthletes())
			self.updateCityRanks()

	def getCityAthletes(self):
		cityAthletes = Athlete.objects.raw(
					'''SELECT s.athleteId_id AS id
					   FROM   climber_athletesegmentscore s, climber_segment seg
					   WHERE  s.segmentId_id = seg.id and seg.city_id = %s
					''', [self.city.name])
		return cityAthletes

	def recalculateCityScores(self, athleteList):
		for athlete in athleteList:
			newScore, newCumulativeTime = self.calculateScoreAndCumulativeTime(athlete.id)
			if newScore < 1:
				athlete.delete()
			else:
				self.updateCityScore(athlete, newScore, newCumulativeTime)

	def calculateScoreAndCumulativeTime(self, athleteId):
		overallScore = 0
		cumulativeTime = 0
		segmentPlacements = AthleteSegmentScore.objects.raw(
					'''SELECT s.id
					   FROM   climber_athletesegmentscore s, climber_segment seg
					   WHERE  s.segmentId_id = seg.id and seg.city_id = %s and s.athleteId_id = %s
					''', [self.city.name, athleteId])
		for placement in segmentPlacements:
			overallScore += placement.segmentScore
			cumulativeTime += placement.segmentTime
		return overallScore, cumulativeTime

	def updateCityScore(self, athlete, newScore, newCumulativeTime):
		oldPlacement = AthleteCityScore.objects.filter(athleteId=athlete, city=self.city.name)
		if oldPlacement:
			oldPlacement[0].cityScore = newScore
			oldPlacement[0].cumulativeTime = newCumulativeTime
			oldPlacement[0].save()
		else:
			acs = AthleteCityScore(athleteId=athlete, city=self.city, cityScore=newScore,
								   cumulativeTime=newCumulativeTime, rank=-1)
			acs.save()

	def updateCityRanks(self):
		newLeaderboard = AthleteCityScore.objects.filter(city=self.city.name).order_by('-cityScore', 'cumulativeTime')
		for i, entry in enumerate(newLeaderboard):
			if entry.rank != (i+1):
				self.changeRank(entry, i+1)

	def changeRank(self, entry, newRank):
		# We don't care about rank changes outside top 500
		if newRank <= 500:
			print("Changed rank " + str(entry) + " to " + str(newRank))
			self.recordPlacementChange(entry, newRank)
		entry.rank = newRank
		entry.save()

	def recordPlacementChange(self, scoreEntry, newRank):
		nowTime = timezone.now()
		oldChanges = PlacementChange.objects.filter(athleteId=scoreEntry.athleteId, 
							city=self.city).order_by('-changeDate')
		# If today already has a PlacementChange recorded, modify it
		if oldChanges and oldChanges[0].changeDate.date() == nowTime.date():
			oldChanges[0].newRank = newRank
			oldChanges[0].save()
		else:
			pc = PlacementChange(athleteId=scoreEntry.athleteId, city=self.city,
							 oldRank=scoreEntry.rank, newRank=newRank, changeDate=nowTime)
			pc.save()

	def removeOldPlacementChanges(self):
		placementChanges = PlacementChange.objects.filter(city=self.city)
		for pc in placementChanges.iterator():
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
		processedSegmentScores = []
		self.updatedAthletes = []
		for leaderboard in leaderboards:
			allSegmentScores = AthleteSegmentScore.objects.filter(segmentId=self.segment.id)
			processedSegmentScores += self.updateLeaderboard(leaderboard, allSegmentScores)
		oldSegmentScores = [ath for ath in allSegmentScores if ath not in processedSegmentScores]
		self.deleteOldSegmentScores(oldSegmentScores)

	def updateLeaderboard(self, leaderboard, allSegmentScores):
		processedSegmentScores = []
		for athlete in leaderboard:
			# Get existing athlete data from database, if possible
			oldAthleteScore = allSegmentScores.filter(athleteId=athlete.athlete_id)

			# Add new or improved athlete and segment score to database
			newAthleteCount = 0
			if oldAthleteScore:
				newScore = self.calculateSegmentScore(athlete.rank, leaderboard.entry_count)
				if newScore != oldAthleteScore[0].segmentScore:
					self.updateAthleteSegmentScore(oldAthleteScore[0], newScore, athlete, 
												   leaderboard.entry_count)
					self.updatedAthletes.append(oldAthleteScore[0].athleteId)
				processedSegmentScores.append(oldAthleteScore[0])
			else:
				newAthlete = self.addAthlete(athlete, leaderboard.entry_count)
				newSegScore = self.addAthleteSegmentScore(newAthlete, athlete, 
														  leaderboard.entry_count)
				self.updatedAthletes.append(newAthlete)
				processedSegmentScores.append(newSegScore)
		return processedSegmentScores

	# Remove athletes whose times are no longer valid, e.g. over #1000, deleted ride, new year etc.
	def deleteOldSegmentScores(self, oldScores):
		for score in oldScores:
			self.updatedAthletes.append(score.athleteId)
			print("Deleted score: " + str(score))
			score.delete()


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
		return ass

	# Calculate score for given segment and use it to update segment score entry
	# This is an ugly hack since Django doesn't allow composite keys and tries to insert instead
	def updateAthleteSegmentScore(self, oldAthleteScore, newScore, apiAthlete, totalEfforts):
		oldAthleteScore.effortId = apiAthlete.effort_id
		oldAthleteScore.activityId = apiAthlete.activity_id
		oldAthleteScore.segmentTime = apiAthlete.elapsed_time.total_seconds()
		oldAthleteScore.segmentScore = newScore
		oldAthleteScore.save()
		
	# Maximum points that can be earned is 1,000 for 1st place -- all other placements get a
	# score as a fraction of 1,000 based on their percentile ranking, except when this score is
	# greater than 1,001 minus their rank.
	def calculateSegmentScore(self, rank, totalEfforts):
		maxScore = 1000
		score = min(round((1 - ((rank - 1) / totalEfforts)) * maxScore), maxScore + 1 - rank)
		if score < 0:
			score = 0
		return score

	def getUpdatedAthletes(self):
		return self.updatedAthletes

	def __init__(self, segment, client):
		self.segment = segment
		self.client = client
		# All athletes who were recently added or whose segment scores were updated
		self.updatedAthletes = []
		# Number of athlete scores we keep track of (x * 200)
		self.leaderboardPageNum = 5

# In case of db flush
def createDefaultCitySegments():
	cities = ['San_Diego', 'San_Diego_County', 'Santa_Cruz', 'San_Francisco']#, 'SF_Bay_Area']
	cityRows = []
	for city in cities:
		cityRow = City(name=city)
		cityRows.append(cityRow)
		cityRow.save()
	segments = [{'id':638425, 'name':'Soledad Mtn Rd', 'city':cityRows[0]},
				{'id':633159, 'name':'Torrey Pines', 'city':cityRows[0]},
				{'id':1340110, 'name':'Cabrillo Tide Pools', 'city':cityRows[0]},
				{'id':273807, 'name':'Palomar South Grade', 'city':cityRows[1]},
				{'id':612298, 'name':'Honey Springs', 'city':cityRows[1]},
				{'id':563739, 'name':'Dehesa Grade', 'city':cityRows[1]},
				{'id':7960449, 'name':'Empire Grade', 'city':cityRows[2]},
				{'id':646647, 'name':'Mtn Charlie', 'city':cityRows[2]},
				{'id':629483, 'name':'Bonny Doon Rd', 'city':cityRows[2]},
				{'id':141491, 'name':'Twin Peaks', 'city':cityRows[3]},
				{'id':7167086, 'name':'Legion of Honor Hill', 'city':cityRows[3]},
				{'id':229781, 'name':'Hawk Hill', 'city':cityRows[3]}#,
				#{'id':1470688, 'name':'Mt. Diablo', 'city':cityRows[3]},
				#{'id':678363, 'name':'Mt. Tamalpais', 'city':cityRows[3]},
				#{'id':6473039, 'name':'Mt. Hamilton', 'city':cityRows[3]}
				]
	for segment in segments:
		segRow = Segment(segment['id'], segment['name'], segment['city'])
		segRow.save()
	return cityRows
