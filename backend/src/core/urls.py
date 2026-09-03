from django.urls import path
from src.core.views import api

urlpatterns = [
    path("", api.urls),
]
