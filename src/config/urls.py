from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

v0 = [
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
