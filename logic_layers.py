import time
import configparser
import threading
from pynput.keyboard import Key, Controller

class AutoClicker:
    def __init__(self, section, config_path='config.ini'):
        self.config_path = config_path
        self.section = section
        self.keyboard = Controller()
        self.running = False
        self._thread = None

    def get_key(self, key_str):
        key_str = key_str.lower()
        special = {'shift': Key.shift, 'space': Key.space, 'ctrl': Key.ctrl, 'alt': Key.alt, 'enter': Key.enter}
        if key_str.startswith('f') and key_str[1:].isdigit():
            try: return getattr(Key, key_str)
            except AttributeError: return key_str
        return special.get(key_str, key_str)

    def _loop(self):
        config = configparser.ConfigParser()
        while self.running:
            config.read(self.config_path)
            cfg = config[self.section]
            target = self.get_key(cfg['target_key'])
            
            self.keyboard.press(target)
            time.sleep(0.05)
            self.keyboard.release(target)
            
            delay = float(cfg['delay'])
            stop_time = time.time() + delay
            while time.time() < stop_time and self.running:
                time.sleep(0.05)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False