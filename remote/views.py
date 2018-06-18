from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404

from django.views.generic import TemplateView, ListView, DetailView
from .models import CameraStatus, Album, Photo
import os, subprocess
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_FULL_SIZE_IMAGE_ON_CAPTURE = True

class Index(TemplateView):
    template_name = "remote/index.html"    

def make_resized_image(file_path):
    return
    
def get_last_image_link(folder_name):
    save_location = "/home/pi/prosjekter/cameraRemote/media/" + folder_name
    os.chdir(save_location)
    f = open(".image_number.txt", "r")
    image_count = int(f.readlines()[0])
    f.close()
    os.chdir(BASE_DIR)
    make_resized_image(folder_name + "/bilde_" + str(image_count) + ".JPG");
    return folder_name + "/bilde_" + str(image_count) + ".JPG"

def get_or_create_camera_status():
    if not CameraStatus.objects.exists():
        return CameraStatus.objects.create()
    return CameraStatus.objects.all()[0]

class Capture(TemplateView):
    template_name = "remote/capture.html"

    def get_context_data(self, **kwargs):
        context = super(Capture, self).get_context_data( **kwargs)
        photo = Photo.objects.all().last()
        if (SHOW_FULL_SIZE_IMAGE_ON_CAPTURE):
            context["image_link"] = photo.image.url
        else:
            context["image_link"] = photo.image_lowres.url
        context["album"] = self.kwargs["album"]
        return context
    
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, name=self.kwargs["album"])
        
        status = get_or_create_camera_status()
        if (status.occupied):
            return redirect("remote:occupied")
        status.occupied=True;
        status.save()
        subprocess.call(["python3", "remote/image_capture.py", album.name])
        status.occupied=False;
        status.save()
        photo = Photo()
        photo.album = album
        photo.image.name=get_last_image_link(album.name)
        photo.save()
        return super(Capture, self).get(request, *args, **kwargs)

class AlbumView(ListView):
    template_name = "remote/album.html"
    context_object_name = "photos"
    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data( **kwargs)
        context["album"] = self.kwargs["album"]
        return context
    
    def get_queryset(self):
        album = get_object_or_404(Album, name=self.kwargs["album"])
        return Photo.objects.filter(album=album).order_by('-shot_time')

class PhotoView(TemplateView):
    template_name = "remote/photo.html"
    context_object_name = "photo"
    
    def get_context_data(self, **kwargs):
        album = get_object_or_404(Album, name=self.kwargs["album"])
        try:
            photo = Photo.objects.filter(album=album).order_by('-shot_time')[self.kwargs["number"]-1]
        except:
            raise Http404
        context = super(PhotoView, self).get_context_data( **kwargs)
        context["photo"] = photo
        context["album"] = self.kwargs["album"]
        return context
    
class Occupied(TemplateView):
    template_name = "remote/occupied.html"
