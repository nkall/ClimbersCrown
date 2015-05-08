from django.shortcuts import get_object_or_404, render
from .models import *
from datetime import datetime

def leaderboard(request, cityName):
	cityRow = get_object_or_404(City, pk=cityName)
	cpg = CityPodiumGenerator(cityRow)
	entries = cpg.generateEntries()
	segments = cpg.segs
	year = datetime.now().year
	test = CityName(cityRow)
	formattedCityName = CityName(cityRow).formattedName
	otherCities = [CityName(c) for c in City.objects.exclude(pk=cityName)]

	return render(request, 'climber/index.html', {'podium': entries, 'segments': segments,
												  'city':formattedCityName,
												  'otherCities':otherCities,
												  'thisYear':year})

def index(request):
	return render(request, 'climber/index.html')

'''
' ' Various classes used to generate leaderboard
'''

class CityName:
	def __init__(self, city):
		self.name = city.name
		self.formattedName = city.name.replace('_',' ')

class CityPodiumGenerator:
	def generateEntries(self):
		entries = []
		cityScores = AthleteCityScore.objects.filter(city=self.city).order_by('rank')[:500] \
						.prefetch_related('athleteId')
		for score in cityScores:
			entries.append(Entry(score.athleteId, self.city, score, self.segs))
		return entries

	def __init__(self, city):
		self.city = city
		self.segs = Segment.objects.filter(city=self.city)

class Entry:
	def __init__(self, athlete, city, cityScore, segments):
		self.athlete = athlete
		self.cityScore = cityScore
		self.isChamp = (cityScore.rank == 1)

		self.weeklyChange = WeeklyChangeEntry()
		self.weeklyChange.consolidateChanges(self.cityScore,
				PlacementChange.objects.filter(athleteId=athlete, city=city))

		self.segmentScores = []
		for seg in segments:
			sse = SegmentScoreEntry()
			sse.genScoreEntry(seg, athlete)
			self.segmentScores.append(sse)

class SegmentScoreEntry:
	def genScoreEntry(self, segment, athlete):
		scoreEntry = AthleteSegmentScore.objects.filter(segmentId=segment, athleteId=athlete)
		if scoreEntry:
			score = scoreEntry[0]
			self.hasScore = True
			self.scoreVal = score.segmentScore
			self.effortTimeStr = self.formatEffortTime(score.segmentTime)
			self.effortUrl = self.formatEffortUrl(score.activityId, score.effortId)

	def formatEffortTime(self, time):
		hours = int(time / 3600)
		minutes = int(time / 60) - (hours * 60)
		seconds = time % 60
		formattedTime = ""
		if hours > 0:
			formattedTime += str(hours) + ":"
			if minutes < 10:
				formattedTime += "0"
		formattedTime += str(minutes) + ":"

		if seconds < 10:
			formattedTime += "0"
		formattedTime += str(seconds)

		return formattedTime

	def formatEffortUrl(self, activityId, effortId):
		return "http://www.strava.com/activities/" + str(activityId) + "/segments/" + str(effortId)

	def __init__(self):
		self.hasScore = False
		self.scoreVal = -1
		self.effortTimeStr = ""
		self.effortUrl = ""


class WeeklyChangeEntry:
	def consolidateChanges(self, currentScore, changes):
		if len(changes) < 1:
			self.netChange = 0
			self.dateOfChange = (timezone.now() - timedelta(days=7)).strftime("%d %b %Y")
		else:
			orderedChanges = changes.order_by("-changeDate")
			oldestChange = orderedChanges[len(orderedChanges)-1]
			newestChange = orderedChanges[0]
			if oldestChange.oldRank > 500 or oldestChange.oldRank == -1:
				self.isNew = True
				self.dateOfChange = oldestChange.changeDate.strftime("%d %b %Y")
			else:
				self.dateOfChange = oldestChange.changeDate.strftime("%d %b %Y")
				self.netChange = oldestChange.oldRank - newestChange.newRank
				if self.netChange > 0:
					self.isUp = True
				elif self.netChange < 0:
					self.isDown = True
					self.netChange = -self.netChange

	def __init__(self):
		# All fields set in consolidateChanges()
		self.netChange = None
		self.dateOfChange = None
		self.isNew = False
		self.isUp = False
		self.isDown = False
