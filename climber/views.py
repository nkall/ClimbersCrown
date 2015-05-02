from django.shortcuts import get_object_or_404, render

from .models import City
# ...
def city(request, cityName):
    city = City.objects.get(pk=cityName)
    city = get_object_or_404(City, pk=cityName)
    return render(request, 'climber/index.html', {'city': city})

def index(request):
	return render(request, 'climber/index.html')