from django.contrib import admin

# Register your models here.
from .models import Athlete, City, Segment, AthleteSegmentScore, AthleteCityScore, PlacementChange
admin.site.register(Athlete)
admin.site.register(City)
admin.site.register(Segment)
admin.site.register(AthleteSegmentScore)
admin.site.register(AthleteCityScore)
admin.site.register(PlacementChange)