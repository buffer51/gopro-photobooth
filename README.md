# GoPro Photobooth

This repository contains code to run a small Photobooth using a GoPro.

## GoPro Server

`gopro_server.py` contains a small Python server to interact with the GoPro.
Once connected to the GoPro's wifi, it does 3 things:
- Wakes the GoPro and polls it to keep it up
- Pulls pictures from the GoPro and post-processes them (see Calibration below)
- Triggers pictures when the user types the letter `t`

## Web Server

`web_server.py` contains a small Python server that serves files locally.
With the content in `slideshow/` and post-processed pictures in `pictures/processed/`,
it serves a small slideshow that refreshes as new pictures become available.

Navigate to `http://localhost:80` to view it.

## Calibration

In order to remove the fisheye effect of the GoPro, the GoPro server uses
calibration data. To produce it, follow the procedure described in `calibration/README.md`.

## Physical Button

The physical button setup is based on [Using a push button with Raspberry Pi GPIO](https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/).
