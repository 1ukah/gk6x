import json, time, keyboard
import numpy as np
import hid
import cv2
from screeninfo import get_monitors
from mss import mss as mss_module

VID = 0x1EA8
PID = 0x0908
device = hid.device()
device.open(VID, PID)

monitor = get_monitors()[0]
WIDTH, HEIGHT = monitor.width, monitor.height
ZONE = 60
SMALLER_ZONE = 30

class gkx6plus:
    def __init__(self):
        self.sct = mss_module()

        with open('keyboard.json') as json_file:
            data = json.load(json_file)

        self.tdelay = data["tdelay"]
        self.bdelay = data["bdelay"]
        self.rundelay = data["rundelay"]
        self.ctolerance = data["ctolerance"]
        self.R, self.G, self.B = (203, 24, 199)

    def find(self):
        global ZONE, SMALLER_ZONE

        current_grab_zone = (
            int(WIDTH / 2 - ZONE),
            int(HEIGHT / 2 - ZONE),
            int(WIDTH / 2 + ZONE),
            int(HEIGHT / 2 + ZONE),
        )

        #print(f"Current grab zone: {current_grab_zone}")

        img = np.array(self.sct.grab(current_grab_zone))
        img_h, img_w, _ = img.shape
        #print(f"Captured image size: {img_h}x{img_w}")

        mask = (
            (img[:, :, 0] > self.R - self.ctolerance) & (img[:, :, 0] < self.R + self.ctolerance) &
            (img[:, :, 1] > self.G - self.ctolerance) & (img[:, :, 1] < self.G + self.ctolerance) &
            (img[:, :, 2] > self.B - self.ctolerance) & (img[:, :, 2] < self.B + self.ctolerance)
        )

        #print(f"Mask sum: {mask.sum()}")

        gray_mask = (mask * 255).astype(np.uint8)

        contours, _ = cv2.findContours(gray_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #print(f"Found {len(contours)} contours")

        valid_contour_found = False
        min_distance = float('inf')
        closest_contour = None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            #print(f"Contour bounding box: x={x}, y={y}, w={w}, h={h}")

            contour_center_x = x + w // 2
            contour_center_y = y + h // 2

            distance_to_crosshair = np.sqrt(
                (contour_center_x - WIDTH // 2) ** 2 +
                (contour_center_y - HEIGHT // 2) ** 2
            )

            #print(f"Distance to crosshair: {distance_to_crosshair}")

            vertical_line = any(
                all(mask[y + i, x + j] for i in range(min(h, img_h - y)))
                for j in range(w)
            )

            if vertical_line and distance_to_crosshair < min(SMALLER_ZONE, ZONE) * 1.5:
                if distance_to_crosshair < min_distance:
                    min_distance = distance_to_crosshair
                    closest_contour = contour
                    valid_contour_found = True

        if valid_contour_found:
            #print(f"Closest contour distance: {min_distance}")
            #print("Valid contour found. Sending data.")

            delay_percentage = self.tdelay / 100.0
            actual_delay = self.bdelay + self.bdelay * delay_percentage
            #print(f"Delay before sending data: {actual_delay}")
            time.sleep(actual_delay)

            device.write([0x00, 0x01])
            #print("Data sent.")
            time.sleep(self.rundelay)
        else:
            #print("No valid contour found. No data sent.")
            ZONE += 10
            SMALLER_ZONE += 5
            #print(f"ZONE increased to {ZONE}")
            #print(f"SMALLER_ZONE increased to {SMALLER_ZONE}")

    def hold(self):
        while True:
            if keyboard.is_pressed('alt'):
                #print("ALT key pressed, scanning for contours...")
                self.find()
                time.sleep(0.1)
            else:
                time.sleep(0.1)

    def run(self):
        self.hold()

gkx6plus().run()
