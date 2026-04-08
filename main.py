import os
import msvcrt
import configparser
import time
from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener, Button

from sprint_logic import SprintManager
from logic_layers import AutoClicker
from random_logic import RandomClicker

class MainMenu:
    def __init__(self):
        self.options = ["Toggle", "Auto Clicker", "Random Clicker", "Kapat"]
        self.selected_index = 0
        self.clicker_mode_active = False 
        self.sprint = SprintManager()
        self.c1 = AutoClicker("CLICKER_1")
        self.c2 = AutoClicker("CLICKER_2")
        self.rnd = RandomClicker()

    def get_status_text(self):
        if self.sprint.running:
            s_stat = f"[HAZIRLANIYOR: {self.sprint.cooldown_remaining}s]" if self.sprint.cooldown_remaining > 0 else "[AKTIF - BASILI]"
        else:
            s_stat = "[PASIF]"
        return s_stat, ("BASILIYOR" if self.c1.running else "DURDU"), ("BASILIYOR" if self.c2.running else "DURDU")

    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        s_stat, c1_s, c2_s = self.get_status_text()
        print("=== MULTI-MODULE GAME BOT ===\n")
        for i, option in enumerate(self.options):
            cursor = "> " if i == self.selected_index else "  "
            if i == 0: print(f"{cursor}{option:20} {s_stat}")
            elif i == 1: print(f"{cursor}{option:20} [{'DINLEMEDE' if self.clicker_mode_active else 'KAPALI'}]")
            elif i == 2: print(f"{cursor}{option:20} [{'AKTIF' if self.rnd.running else 'PASIF'}]")
            else: print(f"{cursor}{option}")
        print("\n" + "-"*45 + f"\nC1: {c1_s} | C2: {c2_s} | Rnd: {'AKTIF' if self.rnd.running else 'PASIF'}")

    def run(self):
        def on_press(key):
            if not self.clicker_mode_active: return
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                char = hasattr(key, 'char') and key.char or str(key).replace("Key.", "")
                if char == config['CLICKER_1']['trigger_key']:
                    self.c1.stop() if self.c1.running else self.c1.start()
                elif char == config['CLICKER_2']['trigger_key']:
                    self.c2.stop() if self.c2.running else self.c2.start()
            except: pass

        def on_click(x, y, button, pressed):
            if not self.clicker_mode_active or not pressed: return
            try:
                config = configparser.ConfigParser()
                config.read('config.ini')
                btn_name = "mouse4" if button == Button.x1 else "mouse5" if button == Button.x2 else None
                if btn_name:
                    if btn_name == config['CLICKER_1']['trigger_key']:
                        self.c1.stop() if self.c1.running else self.c1.start()
                    elif btn_name == config['CLICKER_2']['trigger_key']:
                        self.c2.stop() if self.c2.running else self.c2.start()
            except: pass

        Listener(on_press=on_press).start()
        MouseListener(on_click=on_click).start()

        while True:
            self.display()
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':
                    if self.selected_index == 0: self.sprint.stop() if self.sprint.running else self.sprint.start()
                    elif self.selected_index == 1:
                        self.clicker_mode_active = not self.clicker_mode_active
                        if not self.clicker_mode_active: self.c1.stop(); self.c2.stop()
                    elif self.selected_index == 2: self.rnd.stop() if self.rnd.running else self.rnd.start()
                    elif self.selected_index == 3: break
                elif key in [b'\x00', b'\xe0']:
                    key = msvcrt.getch()
                    if key == b'H': self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif key == b'P': self.selected_index = (self.selected_index + 1) % len(self.options)
            time.sleep(0.1)

if __name__ == "__main__":
    MainMenu().run()