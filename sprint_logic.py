import time
import configparser
from pynput.keyboard import Key, Controller
import threading

class SprintManager:
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.keyboard = Controller()
        self.running = False
        self.cooldown_remaining = 0
        self._thread = None

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        settings = config['SETTINGS']
        return {
            "key": settings.get('key_to_press').lower(),
            "hold": settings.getint('hold_duration'),
            "wait": settings.getint('wait_duration')
        }

    def _logic_loop(self):
        self.cooldown_remaining = 5
        while self.cooldown_remaining > 0 and self.running:
            time.sleep(1)
            self.cooldown_remaining -= 1
        
        if not self.running: return

        cfg = self.load_config()
        special_keys = {'shift': Key.shift, 'space': Key.space, 'enter': Key.enter}
        target_key = special_keys.get(cfg['key'], cfg['key'])

        while self.running:
            self.keyboard.press(target_key)
            for _ in range(cfg['hold'] * 10): 
                if not self.running: break
                time.sleep(0.1)
            
            self.keyboard.release(target_key)
            for _ in range(cfg['wait'] * 10):
                if not self.running: break
                time.sleep(0.1)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._logic_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False
        self.cooldown_remaining = 0