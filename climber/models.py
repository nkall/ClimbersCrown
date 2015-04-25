from django.db import models

class Athlete(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	def __str__(self):
		return self.name

class City(models.Model):
	name = models.CharField(max_length=200, primary_key=True)
	def __str__(self):
		return self.name

class Segment(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	city = models.ForeignKey(City)
	def __str__(self):
		return self.name

class AthleteSegmentScore(models.Model):
	athleteId = models.ForeignKey(Athlete)
	segmentId = models.ForeignKey(Segment)
	effortId = models.IntegerField()

	# Time taken to complete the segment, expressed in seconds
	segmentTime = models.IntegerField()
	segmentScore = models.IntegerField()
	def __str__(self):
		return str(self.athleteId) + " " + str(self.segmentScore)

class AthleteCityScore(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)

	cumulativeTime = models.IntegerField()
	cityScore = models.IntegerField()

	leaderboardPlacement = models.IntegerField()
	def __str__(self):
		return str(self.athleteId) + " " + self.city + " " + str(self.leaderboardPlacement)

# Placement changes are only saved over the past week
class PlacementChange(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)
	oldPlacement = models.IntegerField()
	newPlacement = models.IntegerField()
	changeDate = models.DateTimeField()

	def __str__(self):
		return str(self.changeDate) + " " + str(self.oldPlacement) + " " + str(self.newPlacement)

	def isOutOfDate(self):
		return self.changeDate >= timezone.now() - datetime.timedelta(days=7)
