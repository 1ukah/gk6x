import json, time, keyboard
import numpy as np
import hid
from screeninfo import get_monitors
from mss import mss as mss_module

VID = 0x1EA8
PID = 0x0908
device = hid.device()
device.open(VID, PID)

monitor = get_monitors()[0]
WIDTH, HEIGHT = monitor.width, monitor.height
ZONE = 60
SMALLER_ZONE = 4
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE - 52),
)

class gkx6plus:
    def __init__(self):
        self.sct = mss_module()
        self.gkx6plus = False

        with open('keyboard.json') as json_file:
            data = json.load(json_file)

        self.tdelay = data["tdelay"]
        self.bdelay = data["bdelay"]
        self.rundelay = data["rundelay"]
        self.ctolerance = data["ctolerance"]
        #self.R, self.G, self.B = (203, 24, 199)
        self.R, self.G, self.B = (250, 100, 250)

    def find(self):
        img = np.array(self.sct.grab(GRAB_ZONE))
        img_h, img_w, _ = img.shape

        pixels = img.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R - self.ctolerance) & (pixels[:, 0] < self.R + self.ctolerance) &
            (pixels[:, 1] > self.G - self.ctolerance) & (pixels[:, 1] < self.G + self.ctolerance) &
            (pixels[:, 2] > self.B - self.ctolerance) & (pixels[:, 2] < self.B + self.ctolerance)
        )
        matching_pixels = pixels[color_mask]

        

        if len(matching_pixels) == 0:
            
            return  

        vertical_coords = np.array([
            np.where(color_mask)[0] % img_w,
            np.where(color_mask)[0] // img_w
        ]).T
        unique_x = np.unique(vertical_coords[:, 0])

        

        if len(unique_x) < 2:
            
            return 

        x1, x2 = min(unique_x), max(unique_x)
        smaller_zone_left = int(WIDTH / 2 - SMALLER_ZONE / 2)
        smaller_zone_right = int(WIDTH / 2 + SMALLER_ZONE / 2)
        smaller_zone_center = (smaller_zone_left + smaller_zone_right) // 2


        center_x_in_image = smaller_zone_center - GRAB_ZONE[0]
        

        if not (x1 < center_x_in_image < x2):
            
            return 

        smaller_zone = img[:, smaller_zone_left - GRAB_ZONE[0] : smaller_zone_right - GRAB_ZONE[0]]
        if np.any(
            (smaller_zone[:, :, 0] > self.R - self.ctolerance) &
            (smaller_zone[:, :, 0] < self.R + self.ctolerance) &
            (smaller_zone[:, :, 1] > self.G - self.ctolerance) &
            (smaller_zone[:, :, 1] < self.G + self.ctolerance) &
            (smaller_zone[:, :, 2] > self.B - self.ctolerance) &
            (smaller_zone[:, :, 2] < self.B + self.ctolerance)
        ):
            

            delay_percentage = self.tdelay / 100.0
            actual_delay = self.bdelay + self.bdelay * delay_percentage
            time.sleep(actual_delay)
            device.write([0x00, 0x01])
            time.sleep(self.rundelay)
            
    def hold(self):
        while True:
            while keyboard.is_pressed('alt'):
                self.gkx6plus = True
                self.find()
                time.sleep(0.1)
            else:
                time.sleep(0.1)

    def run(self):
        self.hold()

gkx6plus().run()