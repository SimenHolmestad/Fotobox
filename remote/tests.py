from django.test import TestCase
from django.core.files import File
from remote.models import Album, Photo
from PIL import Image
import os
from io import BytesIO

class image_save_test(TestCase):
    def test_save_image(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = "/".join(dir_path.split("/")[0:-1])
        print (dir_path)
        photo = Photo()
        photo.album = Album.objects.create(name = "test_album")
        photo.image.name = "remote_images/bilde_1.JPG"        
        photo.save()
