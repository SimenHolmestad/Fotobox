from django.shortcuts import render
from django.views.generic import TemplateView
import os, subprocess
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    image_path = "/media/" + folder_name
    make_resized_image(image_path + "/bilde_" str(image_count) + ".JPG");
    return image_path + "/bilde_" + str(image_count) + ".JPG"
    
class Capture(TemplateView):
    template_name = "remote/capture.html"

    def get_context_data(self, **kwargs):
        context = super(Capture, self).get_context_data( **kwargs)
        context["image_link"] = get_last_image_link("remote_images")
        return context
    
    def get(self, request, *args, **kwargs):
        subprocess.call(["python3", "remote/image_capture.py", "remote_images"])
        return super(Capture, self).get(request, *args, **kwargs)
