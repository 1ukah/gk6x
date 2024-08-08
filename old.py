import json, time, keyboard
import numpy as np
import hid
from screeninfo import get_monitors
from mss import mss as mss_module

VID = 0x1EA8
PID = 0x0908
device = hid.device()
device.open(VID, PID)

#    monitor = get_monitors()[1]
#    WIDTH, HEIGHT = monitor.width, monitor.height
#    LEFT, TOP = monitor.x, monitor.y
#    ZONE = 5
#    GRAB_ZONE = {
#        'left': int(LEFT + WIDTH / 2 - ZONE),
#        'top': int(TOP + HEIGHT / 2 - ZONE),
#        'width': ZONE * 2,
#        'height': ZONE * 2
#    }

monitor = get_monitors()[0]
WIDTH, HEIGHT = monitor.width, monitor.height
ZONE = 5
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE),
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
        self.R, self.G, self.B = (250, 100, 250)
        #self.R, self.G, self.B = (203, 24, 199)

    def find(self):
        img = np.array(self.sct.grab(GRAB_ZONE))
        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R - self.ctolerance) & (pixels[:, 0] < self.R + self.ctolerance) &
            (pixels[:, 1] > self.G - self.ctolerance) & (pixels[:, 1] < self.G + self.ctolerance) &
            (pixels[:, 2] > self.B - self.ctolerance) & (pixels[:, 2] < self.B + self.ctolerance)
        )
        matching_pixels = pixels[color_mask]
        if self.gkx6plus and len(matching_pixels) > 0:
            delay_percentage = self.tdelay / 100.0  
            actual_delay = self.bdelay + self.bdelay * delay_percentage
            time.sleep(actual_delay)
            data = [0x00, 0x01]
            device.write(data)
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