# camera remote

A "photobooth"-application for raspberry pi and dslr. You can capture an image from the browser and it will display in the browser as well as on the raspberry pi screen. It does work on the raspberry pi 3 and might work on other versions as well.

## beware

This program will mercilessly delete all files on your dslr, so make sure you don´t have important files on your cameras sd-card before starting.

## displaying image on monitor

To be able to display an image on the monitor, you will need to have seh installed and run this command prior to startup:

```
export DISPLAY=:0
```
This will set your monitor as the output display so seh can do its thing.

## design

The page design is heavily inspired (read stolen) from https://getbootstrap.com/docs/4.1/examples/album/