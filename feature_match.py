import cv2
import numpy as np
import pyautogui
import mss
import mss.tools
import time

MONITOR = None
SCALE = (None, None)

def match_region(greyscale, template):
    grey_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h, w = grey_template.shape

    res = cv2.matchTemplate(greyscale, grey_template, cv2.TM_CCORR_NORMED)
    threshold = 0.95
    loc = np.where(res >= threshold)

    return {"loc": loc, "wh": (w, h)}

def draw_region(screenshot, match):
    loc = match["loc"]
    w, h = match["wh"]
    x = None
    y = None
    for pt in zip(*loc[::-1]):
        print(f"Point: {pt[0] * SCALE[0]}, {pt[1] * SCALE[1]}")
        x = pt[0] * SCALE[0]
        y = pt[1] * SCALE[1]
        el_w = w * SCALE[0]
        el_h = h * SCALE[1]
        el_x = (x + (el_w / 2))
        el_y = (y + (el_h / 2))
        cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 1)
    return (x, y), (el_x, el_y)

def get_screenshot(monitor = 1):
    global MONITOR
    with mss.mss() as sct:
        mon = sct.monitors[monitor]
        MONITOR = mon
        screenshot = sct.grab(mon)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output = "./screenshot.png")

def capture_screen(monitor = 1):
    global MONITOR, SCALE 
    with mss.mss() as sct:
        MONITOR = sct.monitors[monitor]
        screen_grab = sct.grab(MONITOR)
        screen = np.array(screen_grab)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGBA2BGR)

        SCALE = (MONITOR["width"] / screen_grab.width, MONITOR["height"] / screen_grab.height)
    return screen

def main():
    templates = [
        "./templates/names.png"
    ]

    # get_screenshot()
    # screenshot = cv2.imread("./screenshot.png")

    screenshot = capture_screen()
    greyscale = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    matches = []

    for i in templates:
        template = cv2.imread(i)
        match = match_region(greyscale, template)
        matches.append(match)
    
    for i in matches:
        xy, el = draw_region(screenshot, i)
        print(f"element: {el[0]}, {el[1]}")
        print(f"xy: {xy[0]}, {xy[1]}")

    cv2.imwrite("./result.png", screenshot)

if __name__ == "__main__":
    time.sleep(3)
    main()
