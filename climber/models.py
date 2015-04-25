from django.db import models

class Athlete(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)

class City(models.Model):
	name = models.CharField(max_length=200, primary_key=True)

class Segment(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	city = models.ForeignKey(City)

class AthleteSegmentScore(models.Model):
	athleteId = models.ForeignKey(Athlete)
	segmentId = models.ForeignKey(Segment)
	effortId = models.IntegerField()

	# Time taken to complete the segment, expressed in seconds
	segmentTime = models.IntegerField()
	segmentScore = models.IntegerField()

class AthleteCityScore(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)

	cumulativeTime = models.IntegerField()
	cityScore = models.IntegerField()

	leaderboardPlacement = models.IntegerField()

# Placement changes are only saved over the past week
class PlacementChange(models.Model):
	athleteId = models.ForeignKey(Athlete)
	city = models.ForeignKey(City)
	oldPlacement = models.IntegerField()
	newPlacement = models.IntegerField()
	changeDate = models.DateTimeField()