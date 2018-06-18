from django.contrib import admin
from .models import CameraStatus, Photo, Album

admin.site.register(CameraStatus)
admin.site.register(Photo)
admin.site.register(Album)
