import time
import configparser
import threading
from pynput.keyboard import Key, Controller as KController
from pynput.mouse import Controller as MController

class HoldScrollManager:
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.keyboard = KController()
        self.mouse = MController()
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
        config.read(self.config_path)
        cfg = config['HOLD_SCROLL']
        
        mode = cfg['mode'].lower() # 'hold', 'scroll_up', 'scroll_down'
        target = self.get_key(cfg['target_key'])

        if mode == 'hold':
            # Mod 'hold' ise tuşu bir kere basılı tutar
            self.keyboard.press(target)
            while self.running:
                time.sleep(0.1)
            self.keyboard.release(target)
        
        elif mode == 'scroll_up':
            while self.running:
                self.mouse.scroll(0, 1) # Yukarı kaydır
                time.sleep(0.02) # Çok hızlı işlemci yememesi için minik bekleme
        
        elif mode == 'scroll_down':
            while self.running:
                self.mouse.scroll(0, -1) # Aşağı kaydır
                time.sleep(0.02)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False

    def toggle(self):
        if self.running: self.stop()
        else: self.start()