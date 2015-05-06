from django.db import models
from django.utils import timezone
from datetime import timedelta

class Athlete(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	gender = models.CharField(max_length=1)
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
	activityId = models.IntegerField()

	# Time taken to complete the segment, expressed in seconds
	segmentTime = models.IntegerField()
	segmentScore = models.IntegerField()

	# Surrogate composite primary key (thanks StackOverflow)
	class Meta:
		unique_together = (("athleteId", "segmentId"),)

	def __str__(self):
		return str(self.athleteId) + " " + str(self.segmentScore) + " " + str(self.segmentId)

class AthleteCityScore(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)

	cityScore = models.IntegerField()
	cumulativeTime = models.IntegerField()
	rank = models.IntegerField()
	def __str__(self):
		return str(self.athleteId) + " " + str(self.city) + " " + str(self.rank)

# Placement changes are only saved over the past week
class PlacementChange(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)
	oldRank = models.IntegerField()
	newRank = models.IntegerField()
	changeDate = models.DateTimeField()

	def __str__(self):
		return str(self.changeDate) + " " + str(self.oldRank) + " " + str(self.newRank)

	def isOutOfDate(self):
		return self.changeDate >= timezone.now() - timedelta(days=7)
