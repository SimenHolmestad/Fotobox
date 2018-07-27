from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView, ListView, CreateView
from .models import CameraStatus, Album, Photo, Settings
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_album_or_404(album_name):
    album = get_object_or_404(Album, slug=album_name)
    if album.hidden:
        raise Http404
    return album


class Index(ListView):
    template_name = "remote/index.html"
    context_object_name = "albums"

    def get_queryset(self):
        return Album.objects.filter(hidden=False)


class NewAlbum(CreateView):
    template_name = "remote/new_album.html"
    model = Album
    fields = ["name"]


def get_or_create_camera_status():
    if not CameraStatus.objects.exists():
        return CameraStatus.objects.create()
    return CameraStatus.objects.all()[0]


class Capture(TemplateView):
    template_name = "remote/capture.html"

    def get_context_data(self, **kwargs):
        context = super(Capture, self).get_context_data(**kwargs)
        photo = Photo.objects.all().last()
        if (Settings.get_or_create_settings().show_full_size_image_on_capture):
            context["image_link"] = photo.image.url
        else:
            context["image_link"] = photo.image_lowres.url
        context["album"] = self.kwargs["album"]
        return context

    def get(self, request, *args, **kwargs):
        album = get_album_or_404(self.kwargs["album"])

        status = get_or_create_camera_status()
        if (status.occupied):
            return redirect(reverse("remote:occupied", args=[album.slug]))
        status.occupied = True
        status.save()
        last_image_link = album.get_last_image_link()
        if (Settings.get_or_create_settings().do_countdown):
            subprocess.call(["python3", "remote/image_capture.py", album.slug, "T"])
        else:
            subprocess.call(["python3", "remote/image_capture.py", album.slug])
        status.occupied = False
        status.save()
        next_image_link = album.get_last_image_link()
        if next_image_link == last_image_link:  # this means no image was added
            return redirect(reverse("remote:not_connected", args=[album.slug]))
        photo = Photo()
        photo.album = album
        photo.image.name = next_image_link
        photo.save()
        return super(Capture, self).get(request, *args, **kwargs)


class AlbumView(ListView):
    template_name = "remote/album.html"
    context_object_name = "photos"
    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data(**kwargs)
        context["album"] = Album.objects.get(slug=self.kwargs["album"])
        return context

    def get_queryset(self):
        album = get_album_or_404(self.kwargs["album"])
        return Photo.objects.filter(album=album).order_by('-shot_time')


class PhotoView(TemplateView):
    template_name = "remote/photo.html"
    context_object_name = "photo"

    def get_context_data(self, **kwargs):
        album = get_album_or_404(self.kwargs["album"])
        photo = get_object_or_404(Photo, album=album, number_in_album=self.kwargs["number"])
        context = super(PhotoView, self).get_context_data(**kwargs)
        context["photo"] = photo
        context["album"] = self.kwargs["album"]
        photos_in_album = Photo.objects.filter(album=album).count()
        number_in_album = self.kwargs["number"]
        context["photos_in_album"] = photos_in_album
        context["current_photo"] = photos_in_album - number_in_album + 1
        if number_in_album < photos_in_album:
            context["previous_image_link"] = reverse("remote:photo", args=[album.slug, number_in_album + 1])
        if number_in_album > 1:
            context["next_image_link"] = reverse("remote:photo", args=[album.slug, number_in_album - 1])
        return context


class Occupied(TemplateView):
    template_name = "remote/occupied.html"

    def get_context_data(self, **kwargs):
        album = get_album_or_404(self.kwargs["album"])
        context = super(Occupied, self).get_context_data(**kwargs)
        context["album"] = album
        return context


class NotConnected(TemplateView):
    template_name = "remote/not_connected.html"

    def get_context_data(self, **kwargs):
        album = get_album_or_404(self.kwargs["album"])
        context = super(NotConnected, self).get_context_data(**kwargs)
        context["album"] = album
        return context
