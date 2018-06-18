from django.urls import path, include
from . import views

app_name = 'remote'

urlpatterns = [
    path('', views.Index.as_view(), name = "index"),
    path('new_album', views.NewAlbum.as_view(), name="new_album"),
    path('<album>/capture', views.Capture.as_view(), name = "capture"),
    path('<album>', views.AlbumView.as_view(), name = "album"),
    path('<album>/<int:number>', views.PhotoView.as_view(), name = "photo"),    
    path('occupied', views.Occupied.as_view(), name = "occupied"),
]
