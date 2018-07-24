from django.contrib import admin
from .models import CameraStatus, Photo, Album, Settings

admin.site.register(CameraStatus)
admin.site.register(Photo)
admin.site.register(Album)
admin.site.register(Settings)
