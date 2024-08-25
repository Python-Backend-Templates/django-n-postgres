from django.conf import settings
from django.urls import include, path
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


class PingPongAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        from django.contrib.contenttypes.models import ContentType
        import requests

        from config.celery import app

        app.send_task("config.celery.ping")

        try:
            print(requests.post(url="http://localhost:8000/api/v0/ping/").status_code)
        except Exception as e:
            print(e)
        print(ContentType.objects.all())
        return Response("pong")

    def post(self, request, *args, **kwargs):
        print("POSTED")
        return Response("OK")


v0 = [
    path("ping/", PingPongAPIView.as_view(), name="ping-pong"),
]


urlpatterns = [
    path("api/v0/", include((v0, "v0"), namespace="v0")),
]


swagger_v0_urls = [
    path("api/v0/schema/", SpectacularAPIView.as_view(api_version="v0"), name="schema"),
    path(
        "api/v0/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v0/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if not settings.PROD:
    urlpatterns += swagger_v0_urls
