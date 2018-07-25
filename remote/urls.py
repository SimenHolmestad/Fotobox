from django.urls import path
from . import views

app_name = 'remote'

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('nytt_album', views.NewAlbum.as_view(), name="new_album"),
    path('<album>/ta_bilde', views.Capture.as_view(), name="capture"),
    path('<album>', views.AlbumView.as_view(), name="album"),
    path('<album>/<int:number>', views.PhotoView.as_view(), name="photo"),
    path('<album>/opptatt', views.Occupied.as_view(), name="occupied"),
    path('<album>/ikke_tilkoplet', views.NotConnected.as_view(), name="not_connected"),
]
