from django.db import models
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image
import os
from io import BytesIO

THUMBNAIL_SIZE = 1024, 1024


class Settings (models.Model):
    """
    A model for storing settings, making it possible to change settings on
    the django admin-site
    """
    show_full_size_image_on_capture = models.BooleanField(default=True)
    do_countdown = models.BooleanField(default=False)

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
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, allow_unicode=False, unique=True)
    hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ['-priority', '-last_modified']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Album, self).save(*args, **kwargs)

    def to_string(self):
        return "Album: " + self.name

    def get_absolute_url(self):
        return reverse("remote:album", args=[self.slug])
