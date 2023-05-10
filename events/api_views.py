from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


def api_list_conferences(request):
    conferences = Conference.objects.all()
    return JsonResponse(
        {"conferences": conferences},
        encoder=ConferenceListEncoder,
    )


def api_show_conference(request, id):
    conference = Conference.objects.get(id=id)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )


def api_list_locations(request):
    locations = Location.objects.all()
    return JsonResponse(
        {"locations": locations},
        encoder=LocationListEncoder,
    )


def api_show_location(request, id):
    location = Location.objects.get(id=id)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )
