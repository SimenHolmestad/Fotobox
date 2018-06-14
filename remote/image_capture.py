from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import sys, signal, os, subprocess

#Kill the gphoto-process that starts when
#the camera is first connected. This is because
#a window opens when the camera is connected and
#we have to kill the process related to that window.
def kill_gphoto2_process():
    p = subprocess.Popen(["ps", "-A",], stdout=subprocess.PIPE)
    out, err = p.communicate()

    #find the line with the gphoto-process and kill it.
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            #kill the process (must be done with the process id)
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

def clear_screen():
    p = subprocess.Popen(["ps"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    #kill any open screen process
    for line in out.splitlines():
        if b'feh' in line:
            #kill the process (must be done with the process id)
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

def show_image(file_name):
    try:
        subprocess.Popen("feh --hide-pointer -x -q -B black -g 1850x1080 " + file_name, shell=True)
    except:
        print ("could not use screen, run 'export DISPLAY=:0")

#Commands to be sent to the shell
clear_command = ["--folder", "/store_00020001/DCIM/100CANON", "-R", "--delete-all-files"]
trigger_command = ["--trigger-capture"]
download_command = ["--get-all-files"]

#The folder name is the argument given, or else the date is used as the folder name
if len(sys.argv) > 1:
    folder_name = sys.argv[1];
else:
    shot_date = datetime.now().strftime("%Y-%m-%d")    
    folder_name = shot_date
save_location = "/home/pi/prosjekter/cameraRemote/media/" + folder_name

def create_save_folder():
    try:
        os.makedirs(save_location)
    except:
        print("Directory already in place")
    print("Images will be saved in " + save_location)
    os.chdir(save_location)
    if not ".image_number.txt" in os.listdir("."):
        f = open(".image_number.txt", "w+")
        f.write("0")
        f.close()

def get_next_image_number():
    f = open(".image_number.txt", "r");
    image_count = int(f.readlines()[0])
    f.close()
    f = open(".image_number.txt", "w+")
    f.write(str(image_count + 1))
    f.close()
    return image_count + 1

def capture_image():
    gp(clear_command) # deletes the images in the folder
    gp(trigger_command)
    sleep(2) #so that the camera's got time to load the image to the sd-card
    gp(download_command)

# Warning: If multiple images not containing "bilde" (of .JPG or .CR2) exists
#in this folder this function will overwrite all but one of them, so be careful
def rename_files(ID):
    for filename in os.listdir("."):
        if "bilde" not in filename:
            if filename.endswith(".JPG"):
                name = ID + ".JPG"
                os.rename(filename, (name))
                print ("Renamed the jpg to " + name)
            elif filename.endswith(".CR2"):
                name = ID + ".CR2"
                os.rename(filename, name)
                print ("Renamed the raw-file to " + name)
                
kill_gphoto2_process()
create_save_folder()
capture_image()
id = "bilde_" + str(get_next_image_number())
rename_files(id)
clear_screen()
show_image(id + ".JPG")
