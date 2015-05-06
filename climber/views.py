from django.shortcuts import get_object_or_404, render
from .models import *

def leaderboard(request, cityName):
    cityRow = get_object_or_404(City, pk=cityName)
    cpg = CityPodiumGenerator(cityRow)
    entries = cpg.generateEntries()
    segments = cpg.segs

    return render(request, 'climber/index.html', {'podium': entries, 'segments': segments})

def index(request):
	return render(request, 'climber/index.html')


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

		self.weeklyChange = WeeklyChangeEntry()
		self.weeklyChange.consolidateChanges(self.cityScore,
				PlacementChange.objects.filter(athleteId=athlete, city=city))

		self.segmentScores = []
		for seg in segments:
			score = AthleteSegmentScore.objects.filter(segmentId=seg, athleteId=athlete)
			if len(score) < 1:
				self.segmentScores.append(None)
			else:
				self.segmentScores.append(score[0])

class WeeklyChangeEntry:
	def consolidateChanges(self, currentScore, changes):
		if len(changes) < 1:
			self.netChange = 0
			self.dateOfChange = timezone.now() - timedelta(days=7)
		else:
			orderedChanges = changes.order_by("-changeDate")
			newestChange = orderedChanges[0]
			oldestChange = orderedChanges[len(orderedChanges)-1]
			self.dateOfChange = newestChange.changeDate
			self.netChange = oldestChange.oldRank - newestChange.newRank

	def __init__(self):
		# All fields set in consolidateChanges()
		self.netChange = None
		self.dateOfChange = None
