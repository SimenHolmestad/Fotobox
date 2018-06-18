from django.db import models
from datetime import datetime
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
import os
from io import BytesIO

# Create your models here.

THUMBNAIL_SIZE = 1024, 1024

class CameraStatus (models.Model):
    occupied = models.BooleanField(default=False)

    #make sure only one cameraStatus can exist
    def save(self, *args, **kwargs):
        if CameraStatus.objects.exists() and not self.pk:
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError("There can only be one cameraStatus instance")
        return super(CameraStatus, self).save(*args, **kwargs)

def create_folder(folder_location):
    try:
        os.makedirs(folder_location)
    except:
        print(folder_location + " already in place")
    
class Photo (models.Model):
    shot_time = models.DateTimeField(default=datetime.now)
    image = models.ImageField()
    image_lowres = models.ImageField()
    album = models.ForeignKey("Album", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail - is the file type valid?')
        super(Photo, self).save(*args, **kwargs)

    def make_thumbnail(self):
        image = Image.open(self.image.path)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        image_filename = self.image.url.split("/")[-1]
        image_folder = "/".join(self.image.path.split("/")[0:-1])
        create_folder(image_folder + "/lowres")
        rel_image_folder = "/".join(self.image.url.split("/")[2:-1]) # we have to omit media, therefore the [2:-1]

        thumb_filename = rel_image_folder + "/lowres/" + image_filename.split(".")[0] + "_lowres.JPG"

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, "JPEG")
        temp_thumb.seek(0)
        
        # set save=False, otherwise it will run in an infinite loop
        print ("thumf_filename: " + thumb_filename)
        self.image_lowres.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True

class Album (models.Model):
    time_made = models.DateTimeField(default=datetime.now)
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, allow_unicode=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Album, self).save(*args, **kwargs)

    def to_string(self):
        return "Album: " + self.name

    def get_absolute_url(self):
        return reverse("remote:album", args=[self.slug])
