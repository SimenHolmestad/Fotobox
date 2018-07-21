from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.utils import IntegrityError
from remote.models import Album, Photo
from PIL import Image
import os
import tempfile
import shutil
from io import BytesIO

MEDIA_ROOT = settings.BASE_DIR + "/media"


def create_album(temp_dir):
    """ returns an album which defaults to the temp_dir """
    album_name = temp_dir.split("/")[-1]  # the directory name
    return Album.objects.create(name=album_name)


def create_photo(album):
    """ creates a photo for testing-purposes """
    size = (200, 200)
    color = (255, 0, 0, 0)
    img = Image.new("RGB", size, color)
    image_file = BytesIO()
    img.save(image_file, format="JPEG")
    image_file.seek(0)
    filename = "bilde_" + str((len(Photo.objects.filter(album=album)) + 1)) + ".jpg"  # makes unique filenames
    file_path = os.path.join(album.slug, filename)

    photo = Photo()
    photo.album = album
    photo.image.save(file_path, ContentFile(image_file.read()), save=True)
    photo.save()
    return photo


RUN_CAPTURE_TESTS = False


class CaptureTestCase (TestCase):
    def setUp(self):
        if not RUN_CAPTURE_TESTS:
            return


class AlbumTestCase (TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.test_dir2 = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.client = Client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_dir2)

    def test_album_in_index(self):
        album = create_album(self.test_dir)
        response = self.client.get(reverse("remote:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, album.name)

    def test_hidden_album(self):
        album1 = create_album(self.test_dir)
        album2 = create_album(self.test_dir2)
        album1.hidden = True
        album1.save()
        response = self.client.get(reverse("remote:index"))
        self.assertContains(response, album2.name)
        self.assertNotContains(response, album1.name)
        response = self.client.get(reverse("remote:album", args=[album1.name]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("remote:album", args=[album2.name]))
        self.assertEqual(response.status_code, 200)

    def test_same_slug(self):
        create_album(self.test_dir)
        try:
            create_album(self.test_dir)
            self.fail()
        except IntegrityError:
            pass
