from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from remote.models import Album, Photo, CameraStatus, Settings
from PIL import Image
import os
import tempfile
import shutil
import datetime
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
    filename = "bilde_" + str((len(Photo.objects.filter(album=album)) + 1)) + ".JPG"  # makes unique filenames
    file_path = os.path.join(album.slug, filename)

    photo = Photo()
    photo.album = album
    photo.image.save(file_path, ContentFile(image_file.read()), save=True)
    photo.save()
    return photo


CAMERA_CONNECTED = False  # The page should be tested both when the camera is connected and not.


class CaptureTestCase (TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.client = Client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_capture(self):
        """ This test will actually take a picture with the camera. This takes some time """
        if not CAMERA_CONNECTED:
            print("CAMERA_CONNECTED is set to False")
            print("Did not run test_capture")
            return
        self.assertEqual(len(Photo.objects.all()), 0)
        album = create_album(self.test_dir)
        response = self.client.get(reverse("remote:capture", args=[album.slug]))
        self.assertEqual(len(Photo.objects.all()), 1)
        self.assertEqual(Photo.objects.all()[0].album, album)
        self.assertContains(response, Photo.objects.all()[0].image.url)
        test_dir_contents = os.listdir(self.test_dir)
        self.assertTrue("bilde_1.JPG" in test_dir_contents)
        self.assertTrue(".image_number.txt" in test_dir_contents)

    def test_capture_when_occupied(self):
        camera_status = CameraStatus.objects.create()
        camera_status.occupied = True
        camera_status.save()
        album = create_album(self.test_dir)
        response = self.client.get(reverse("remote:capture", args=[album.slug]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("remote:capture", args=[album.slug]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, reverse("remote:capture", args=[album.slug]))

    def test_capture_when_no_camera(self):
        if CAMERA_CONNECTED:
            print("CAMERA_CONNECTED is set to True")
            print("Did not run test_capture_when_no_camera")
            return
        album = create_album(self.test_dir)
        response = self.client.get(reverse("remote:capture", args=[album.slug]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("remote:capture", args=[album.slug]), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, reverse("remote:capture", args=[album.slug]))


class AlbumTestCase (TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.test_dir2 = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.client = Client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_dir2)

    def test_ordering(self):
        album1 = create_album(self.test_dir)
        album2 = create_album(self.test_dir2)
        create_photo(album1)
        create_photo(album2)  # should make album2 priotitized as it is now the last modified
        album_query = Album.objects.all()
        self.assertEquals(list(album_query), [album2, album1])

        album1.priority = 10
        album1.save()
        album_query2 = Album.objects.all()
        self.assertEquals(list(album_query2), [album1, album2])

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
        response = self.client.get(reverse("remote:album", args=[album1.slug]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("remote:album", args=[album2.slug]))
        self.assertEqual(response.status_code, 200)

    def test_same_slug(self):
        create_album(self.test_dir)
        try:
            create_album(self.test_dir)
            self.fail()
        except IntegrityError:
            pass

    def test_album_when_main_album(self):
        album1 = create_album(self.test_dir)
        album2 = create_album(self.test_dir2)
        project_settings = Settings.get_or_create_settings()
        project_settings.main_album = album1
        project_settings.save()
        response = self.client.get(reverse("remote:album", args=[album1.slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("remote:album", args=[album2.slug]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("remote:index"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("remote:index"), follow=True)
        self.assertContains(response, album1.name)
        self.assertNotContains(response, "Tilbake til albumliste")


class PhotoTestCase (TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.test_dir2 = tempfile.mkdtemp(dir=MEDIA_ROOT)
        self.album = create_album(self.test_dir)
        self.album2 = create_album(self.test_dir2)
        self.client = Client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_dir2)

    def test_low_res_image_generated(self):
        create_photo(self.album)
        test_dir_contents = os.listdir(self.test_dir)
        self.assertTrue("lowres" in test_dir_contents)
        self.assertTrue("bilde_1.JPG" in test_dir_contents)
        lowres_dir_contents = os.listdir(os.path.join(self.test_dir, "lowres"))
        self.assertTrue("bilde_1_lowres.JPG" in lowres_dir_contents)

    def test_time_elapsed_since_taken(self):
        photo = create_photo(self.album)
        photo.shot_time = timezone.now() - datetime.timedelta(days=370)
        self.assertEqual(photo.time_elapsed_since_taken(), "Mer enn 1 år siden")
        photo.shot_time = timezone.now() - datetime.timedelta(days=40)
        self.assertEqual(photo.time_elapsed_since_taken(), "Mer enn 1 måned siden")
        photo.shot_time = timezone.now() - datetime.timedelta(days=70)
        self.assertEqual(photo.time_elapsed_since_taken(), "Mer enn 2 måneder siden")
        photo.shot_time = timezone.now() - datetime.timedelta(days=1, seconds=50)
        self.assertEqual(photo.time_elapsed_since_taken(), "1 dag siden")
        photo.shot_time = timezone.now() - datetime.timedelta(days=2, seconds=50)
        self.assertEqual(photo.time_elapsed_since_taken(), "2 dager siden")
        photo.shot_time = timezone.now() - datetime.timedelta(seconds=7261)
        self.assertEqual(photo.time_elapsed_since_taken(), "2 timer og 1 minutt siden")
        photo.shot_time = timezone.now() - datetime.timedelta(seconds=3725)
        self.assertEqual(photo.time_elapsed_since_taken(), "1 time og 2 minutter siden")
        photo.shot_time = timezone.now() - datetime.timedelta(seconds=125)
        self.assertEqual(photo.time_elapsed_since_taken(), "2 minutter siden")
        photo.shot_time = timezone.now() - datetime.timedelta(seconds=3601)
        self.assertEqual(photo.time_elapsed_since_taken(), "1 time siden")
        photo.shot_time = timezone.now() - datetime.timedelta(seconds=26)
        self.assertEqual(photo.time_elapsed_since_taken(), "26 sekunder siden")

    def test_album_id(self):
        photo1 = create_photo(self.album)
        photo2 = create_photo(self.album2)
        photo3 = create_photo(self.album)
        self.assertEqual(photo1.number_in_album, 1)
        self.assertEqual(photo2.number_in_album, 1)
        self.assertEqual(photo3.number_in_album, 2)
        response = self.client.get(reverse("remote:photo", args=[self.album.slug, photo1.number_in_album]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(photo3.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.album.get_absolute_url())
        self.assertContains(response, photo1.get_absolute_url())
        self.assertContains(response, photo3.get_absolute_url())
        self.assertNotContains(response, photo2.get_absolute_url())

    def test_navigation_links(self):
        photo1 = create_photo(self.album)
        response = self.client.get(reverse("remote:photo", args=[self.album.slug, photo1.number_in_album]))
        self.assertNotContains(response, "Neste bilde")
        self.assertNotContains(response, "Forrige bilde")

        photo2 = create_photo(self.album)
        response = self.client.get(reverse("remote:photo", args=[self.album.slug, photo1.number_in_album]))
        self.assertNotContains(response, "Neste bilde")
        self.assertContains(response, "Forrige bilde")
        response = self.client.get(reverse("remote:photo", args=[self.album.slug, photo2.number_in_album]))
        self.assertContains(response, "Neste bilde")
        self.assertNotContains(response, "Forrige bilde")

        photo3 = create_photo(self.album)
        response = self.client.get(reverse("remote:photo", args=[self.album.slug, photo2.number_in_album]))
        self.assertContains(response, "Neste bilde")
        self.assertContains(response, "Forrige bilde")
