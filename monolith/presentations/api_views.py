from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Presentation
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference
from events.api_views import ConferenceListEncoder
import pika

class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]
    encoders = {"conference": ConferenceListEncoder()}

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        "company_name",
        "conference",
    ]
    encoders = {"conference": ConferenceListEncoder()}

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference id"}, status=400
            )
        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, id):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = Conference.objects.get(id=id)
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference id"},
                status=400,
            )
        Presentation.objects.filter(id=id).update(**content)
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["PUT"])
def api_approve_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.approve()

    parameters = pika.ConnectionParameters(host="rabbitmq")
    dictionary = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    dumped_dict = json.dumps(dictionary)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body = dumped_dict,
    )
    connection.close()

    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.reject()
    parameters = pika.ConnectionParameters(host="rabbitmq")
    dictionary = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    dumped_dict = json.dumps(dictionary)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=dumped_dict,
    )
    connection.close()

    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
