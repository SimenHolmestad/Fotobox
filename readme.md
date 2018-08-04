# Fotobox

A "photobooth"-application for Raspberry Pi and dslr. It lets you capture images and sort them in albums from a web interface. I use a Raspberry Pi 3, but it will probably work on other versions as well. The site interface is in norwegian.

## Beware

This program will mercilessly delete all files on your dslr, so make sure you don´t have important files on your cameras sd-card before starting.

## Displaying images on monitor from RP

To make this program able to display images on the monitor, you will need to install feh and run this command prior to startup:

```
export DISPLAY=:0
```
This will set your monitor as the output display so feh can do its thing.
It´s fully possible (and functional) to run the project without a monitor connected to the RP thoug.

## Requirements

This project uses Gphoto2 for connecting to the dslr. I recommend downloading it with https://github.com/gonzalo/gphoto2-updater.

The rest can be intalled with `pip install -r requirements.txt`

I haven´t really tried setting up the project from scratch yet (It´s on the todo-list), so there might be something missing here.

## Customizing the site

You can customize how the site behaves with the Settings-model from the admin-site. Here you can change wether you want a countdown to be displayed on monitor before capture, and wether you want full-sized or down-sized images to be shown on the page after an image is captured. You can also set contact information shown on site and select a main album, making it the only album accessible on the site.

## Design

The site design is heavily inspired by (read "stolen from") https://getbootstrap.com/docs/4.1/examples/album/