import cv2
import json
import numpy as np
import os
import pickle
import RPi.GPIO as GPIO
import requests
import socket
import struct
import time
from getmac import get_mac_address
from threading import Thread

DEBUG_LOGS = False
RAW_PICTURES_FOLDER = './pictures/raw'
PROCESSED_PICTURES_FOLDER = './pictures/processed'
CHANNEL = 10 # GPIO button channel
EVENT_DELAY = 5 # In seconds

class MyGoPro:
    ### Static methods ###
    def parse_media(media):
        media = [m['n'] for m in media]
        pictures = [m for m in media if m.endswith('.JPG')]
        videos = [m for m in media if m.endswith('.MP4')]
        return pictures, videos

    ### Methods ###
    def __init__(self):
        self.ip_addr = '10.5.5.9'

        self.get_mac_address()
        self.keep_alive()
        self.load_calibration_data()

        print('Init...')
        # TODO(pmustiere): Wait for a first thing to work before doing the other requests
        requests.get('http://10.5.5.9/gp/gpControl/setting/53/1') # Default boot mode to picture, just in case
        self.refresh_pictures()
        print('Ready\n')

    def get_mac_address(self):
        # Retrieve MAC address
        self.mac_address = get_mac_address(ip='10.5.5.9')
        if not self.mac_address:
            print('ERROR: Failed to get MAC address')
            exit(1)

        self.mac_address = str(self.mac_address)
        if len(self.mac_address) == 17: # Remove separators, if needed
            self.mac_address = self.mac_address.replace(self.mac_address[2], '')

    def keep_alive(self):
        def keep_alive_function(ip_addr):
            while True:
                # Send power on command
                if DEBUG_LOGS:
                    print('[keep_alive_thread] Waking up GoPro...')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = bytes('FFFFFFFFFFFF' + self.mac_address * 16, 'utf-8')
                message = b''
                for i in range(0, len(data), 2):
                    message += struct.pack(b'B', int(data[i: i + 2], 16))
                sock.sendto(message, (self.ip_addr, 9))
                if DEBUG_LOGS:
                    print('[keep_alive_thread] Awake\n')

                while True:
                    try:
                        if DEBUG_LOGS:
                            print('[keep_alive_thread] Keep alive')
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto('_GPHD_:0:0:2:0.000000\n'.encode(), (ip_addr, 8554))
                        time.sleep(2.5)

                        response = requests.get('http://10.5.5.9:8080/gp/gpControl/status', timeout=1)
                        response.raise_for_status()
                    except:
                        print('[keep_alive_thread] GoPro not responding, going to wake it up')

        self.keep_alive_thread = Thread(target=keep_alive_function, args=(self.ip_addr,))
        self.keep_alive_thread.start()

    def load_calibration_data(self):
        with open('calibration/results/calibration_data.pkl', 'rb') as f:
            self.calibration_data = pickle.load(f)
        print('Loaded calibration data')

    def list_media(self):
        response = requests.get('http://10.5.5.9:8080/gp/gpMediaList')
        response.raise_for_status()
        response = response.json()
        self.gopro_id = response['media'][0]['d']
        self.gopro_pictures, self.gopro_videos = MyGoPro.parse_media(response['media'][0]['fs'])

    def list_downloaded_pictures(self):
        self.downloaded_pictures = os.listdir(RAW_PICTURES_FOLDER)

    def list_processed_pictures(self):
        self.processed_pictures = os.listdir(PROCESSED_PICTURES_FOLDER)

    def get_picture(self, picture):
        response = requests.get('http://10.5.5.9:8080/videos/DCIM/{}/{}'.format(self.gopro_id, picture), stream=True)
        response.raise_for_status()
        with open('{}/{}'.format(RAW_PICTURES_FOLDER, picture), 'wb') as f:
            for chunk in response:
                f.write(chunk)
        print('Downloaded picture \'{}\''.format(picture))

    def process_picture(self, picture):
        DIM, K, D = self.calibration_data
        img = cv2.imread('{}/{}'.format(RAW_PICTURES_FOLDER, picture))

        h,w = img.shape[:2]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
        undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        cv2.imwrite('{}/{}'.format(PROCESSED_PICTURES_FOLDER, picture), undistorted_img)

        print('Processed picture \'{}\''.format(picture))

    def refresh_pictures(self, update=True):
        def refresh_pictures_function():
            while True:
                try:
                    time.sleep(1)
                    if DEBUG_LOGS:
                        print('[refresh_pictures_thread] Refreshing pictures...')

                    self.list_media()
                    self.list_downloaded_pictures()
                    for picture in [p for p in self.gopro_pictures if p not in self.downloaded_pictures]:
                        self.get_picture(picture)

                    self.list_downloaded_pictures()
                    self.list_processed_pictures()
                    for picture in [p for p in self.downloaded_pictures if p not in self.processed_pictures]:
                        self.process_picture(picture)
                except:
                    print('[refresh_pictures_thread] got an error')

        self.refresh_pictures_thread = Thread(target=refresh_pictures_function)
        self.refresh_pictures_thread.start()

    def take_picture(self):
        print('Taking a picture...')
        response = requests.get('http://10.5.5.9/gp/gpControl/command/shutter?p=1')
        response.raise_for_status()
        time.sleep(2)
        print('Done\n')

class GPIOButton():
    def __init__(self, event_hook):
        self.pressed = False
        self.last_press = None
        self.event_hook = event_hook

        GPIO.setmode(GPIO.BOARD)
    	GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(CHANNEL, GPIO.BOTH, callback=button.gpio_event)

    def gpio_event(self, channel):
        if GPIO.input(CHANNEL):
            self.down()
        else:
            self.up()

    def down(self):
        self.pressed = True

    def up(self):
        if self.pressed:
            self.maybe_event()

        self.pressed = False

    def maybe_event(self):
        current_time = time.time()

        if not self.last_press or current_time-self.last_press > EVENT_DELAY:
            self.event_hook()
            self.last_press = current_time

if __name__ == '__main__':
    gopro = MyGoPro()
    button = GPIOButton(gopro.take_picture())

    while True:
        time.sleep(60)
