import time
import configparser
import threading
import random
from pynput.keyboard import Key, Controller as KController
from pynput.mouse import Button, Controller as MController

class RandomClicker:
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.keyboard = KController()
        self.mouse = MController()
        self.running = False
        self._thread = None

    def execute_click(self, target_str):
        target_str = target_str.lower()
        mouse_map = {'mouse1': Button.left, 'mouse2': Button.right, 'mouse3': Button.middle}
        if target_str in mouse_map:
            self.mouse.click(mouse_map[target_str])
        else:
            special = {'shift': Key.shift, 'space': Key.space, 'ctrl': Key.ctrl, 'alt': Key.alt}
            target = special.get(target_str, target_str)
            try:
                self.keyboard.press(target)
                time.sleep(0.02)
                self.keyboard.release(target)
            except: pass

    def _loop(self):
        config = configparser.ConfigParser()
        while self.running:
            config.read(self.config_path)
            cfg = config["RANDOM_CLICKER"]
            min_v = float(cfg.get('min_interval', 1))
            max_v = float(cfg.get('max_interval', 5))
            if min_v >= max_v: break
            self.execute_click(cfg.get('target_key', 'r'))
            wait_time = random.uniform(min_v, max_v)
            stop_at = time.time() + wait_time
            while time.time() < stop_at and self.running:
                time.sleep(0.05)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False