from django.db import models
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image
import os
from io import BytesIO

THUMBNAIL_SIZE = 1024, 1024


class CameraStatus (models.Model):
    occupied = models.BooleanField(default=False)

    # make sure only one cameraStatus can exist
    def save(self, *args, **kwargs):
        if CameraStatus.objects.exists() and not self.pk:
            # self.pk == false -> the object is not yet stored in the database
            raise ValidationError("There can only be one CameraStatus instance")
        return super(CameraStatus, self).save(*args, **kwargs)


def create_folder(folder_location):
    try:
        os.makedirs(folder_location)
    except:
        print(folder_location + " already in place")


class Photo (models.Model):
    shot_time = models.DateTimeField(default=timezone.now)
    image = models.ImageField()
    image_lowres = models.ImageField()
    album = models.ForeignKey("Album", on_delete=models.CASCADE)
    number_in_album = models.IntegerField(default=0)  # for lookups

    def save(self, *args, **kwargs):
        self.album.last_modified = timezone.now()
        self.album.save()
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail - is the file type valid?')
        if not self.pk:
            self.number_in_album = Photo.objects.filter(album=self.album).count() + 1
        super(Photo, self).save(*args, **kwargs)

    def time_elapsed_since_taken(self):
        """ returns a string containing the time elapsed since the photo was taken """
        now = timezone.now()
        delta = now - self.shot_time
        if delta.days // 365 > 0:
            return "Mer enn " + str(delta.days // 365) + " år siden"

        if delta.days // 30 > 0:
            if delta.days // 30 == 1:
                return "Mer enn 1 måned siden"
            else:
                return "Mer enn " + str(delta.days // 30) + " måneder siden"

        if delta.days > 0:
            if delta.days == 1:
                return "1 dag siden"
            else:
                return str(delta.days) + " dager siden"

        hours = delta.seconds // 3600
        if hours == 1:
            hour_string = "1 time"
        else:
            hour_string = str(hours) + " timer"

        minutes = (delta.seconds % 3600) // 60
        if minutes == 1:
            minute_string = "1 minutt"
        else:
            minute_string = str(minutes) + " minutter"

        seconds = (delta.seconds % 3600) - minutes * 60
        if seconds == 1:
            second_string = "1 sekund"
        else:
            second_string = str(seconds) + " sekunder"

        if hours > 0:
            if minutes == 0:
                return hour_string + " siden"
            return hour_string + " og " + minute_string + " siden"
        if minutes > 0:
            return minute_string + " siden"
        else:
            return second_string + " siden"

    def make_thumbnail(self):
        image = Image.open(self.image.path)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        image_filename = self.image.url.split("/")[-1]
        image_folder = "/".join(self.image.path.split("/")[0:-1])
        create_folder(image_folder + "/lowres")
        rel_image_folder = "/".join(self.image.url.split("/")[2:-1])  # we have to omit media, therefore the [2:-1]

        thumb_filename = rel_image_folder + "/lowres/" + image_filename.split(".")[0] + "_lowres.JPG"

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, "JPEG")
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        print("lowres_filename: " + thumb_filename)
        self.image_lowres.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True

    def get_absolute_url(self):
        return reverse("remote:photo", args=[self.album.slug, self.number_in_album])


class Album (models.Model):
    time_made = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(default=timezone.now)
    priority = models.PositiveIntegerField(default=1)
    name = models.CharField("Navn", max_length=30)
    description = models.TextField("Beskrivelse", default="")
    slug = models.SlugField(max_length=30, allow_unicode=False, unique=True)
    hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ['-priority', '-last_modified']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.description == "":
            self.description = "Dette albumet har ingen beskrivelse"
        super(Album, self).save(*args, **kwargs)

    def __str__(self):
        return "Album: " + self.name

    def get_absolute_url(self):
        return reverse("remote:album", args=[self.slug])

    def get_last_image_link(self):
        """ gets the path to the last image created in this albums folder """
        save_location = os.path.join(settings.BASE_DIR, "media", self.slug)
        try:
            f = open(os.path.join(save_location, ".image_number.txt"), "r")
        except IOError:
            return "No_image"
        image_count = int(f.readlines()[0])
        if image_count == 0:
            return "No_image"
        f.close()
        return self.slug + "/bilde_" + str(image_count) + ".JPG"


class Settings (models.Model):
    """
    A model for storing settings, making it possible to change settings on
    the django admin-site
    """
    show_full_size_image_on_capture = models.BooleanField(default=True)
    do_countdown = models.BooleanField(default=False)
    contact_first_name = models.CharField(max_length=12, default="noen")
    contact_phone_number = models.CharField(max_length=15, default="")
    main_album = models.ForeignKey(Album, blank=True, null=True, default=None, on_delete=models.SET_NULL)  # if you want only one album to be displayed, choose this

    def get_or_create_settings():
        if not Settings.objects.exists():
            return Settings.objects.create()
        return Settings.objects.all()[0]

    # Make sure only one settings instance can exist
    def save(self, *args, **kwargs):
        if Settings.objects.exists() and not self.pk:
            # self.pk == false -> the object is not yet stored in the database
            raise ValidationError("There can only be one Settings instance")
        return super(Settings, self).save(*args, **kwargs)
