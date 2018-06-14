from django.urls import path, include
from . import views

app_name = 'remote'

urlpatterns = [
    path('', views.Index.as_view(), name = "index"),
    path('capture', views.Capture.as_view(), name = "capture"),
]
