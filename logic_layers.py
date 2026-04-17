import time
import configparser
import threading
from pynput.keyboard import Key, Controller as KController
from pynput.mouse import Button, Controller as MController

class AutoClicker:
    def __init__(self, section, config_path='config.ini'):
        self.config_path = config_path
        self.section = section
        self.keyboard = KController()
        self.mouse = MController()
        self.running = False
        self._thread = None

    def execute_click(self, target_str):
        target_str = target_str.lower()
        mouse_map = {'mouse1': Button.left, 'mouse2': Button.right, 'mouse3': Button.middle, 'mouse4': Button.x1, 'mouse5': Button.x2}
        
        if target_str in mouse_map:
            self.mouse.click(mouse_map[target_str])
        else:
            special = {'shift': Key.shift, 'space': Key.space, 'ctrl': Key.ctrl, 'alt': Key.alt, 'enter': Key.enter}
            target = special.get(target_str, target_str)
            if target_str.startswith('f') and target_str[1:].isdigit():
                try: target = getattr(Key, target_str)
                except: pass
            try:
                self.keyboard.press(target)
                time.sleep(0.02)
                self.keyboard.release(target)
            except: pass

    def _loop(self):
        config = configparser.ConfigParser()
        while self.running:
            config.read(self.config_path)
            if not config.has_section(self.section): break
            cfg = config[self.section]
            self.execute_click(cfg.get('target_key', 'q'))
            delay = float(cfg.get('delay', 1.0))
            stop_time = time.time() + delay
            while time.time() < stop_time and self.running:
                time.sleep(0.01)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False