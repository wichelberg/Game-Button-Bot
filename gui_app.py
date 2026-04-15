import customtkinter as ctk
import configparser
import uuid
from pynput.keyboard import Listener, Key, Controller as KController
from pynput.mouse import Listener as MouseListener, Button, Controller as MController
from sprint_logic import SprintManager
from logic_layers import AutoClicker
from random_logic import RandomClicker
from hold_logic import HoldScrollManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GameBotUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wichelberg Dynamic Center")
        self.geometry("800x950")
        
        self.sprint = SprintManager()
        self.rnd = RandomClicker()
        self.hold_scroll = HoldScrollManager()
        
        self.active_clickers = {} 
        self.clicker_frames = {} 
        
        self.autoclicker_enabled = False
        self.holdscroll_enabled = False

        self.setup_ui()
        self.load_dynamic_clickers()
        self.start_listeners()

    def save_config_value(self, section, key, value):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if section not in config: config.add_section(section)
        config.set(section, key, str(value))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def remove_config_section(self, section):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config.has_section(section):
            config.remove_section(section)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        config = configparser.ConfigParser()
        config.read('config.ini')

        ctk.CTkLabel(self, text="Wichelberg Dynamic Center", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=20)

        s_frame = ctk.CTkFrame(self)
        s_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(s_frame, text="Toggle Settings", font=("Roboto", 16, "bold")).pack(pady=5)
        
        s_sett = ctk.CTkFrame(s_frame, fg_color="transparent")
        s_sett.pack(pady=5)
        self.sprint_key = self.create_input(s_sett, "Key:", config['SETTINGS']['key_to_press'], 60)
        self.sprint_hold = self.create_input(s_sett, "Hold:", config['SETTINGS']['hold_duration'], 40)
        self.sprint_wait = self.create_input(s_sett, "Wait:", config['SETTINGS']['wait_duration'], 40)
        ctk.CTkButton(s_sett, text="Kaydet", width=50, command=self.save_sprint).pack(side="left", padx=5)
        self.sprint_btn = ctk.CTkButton(s_frame, text="Toggle: RUN", command=self.toggle_sprint)
        self.sprint_btn.pack(pady=10, padx=20, fill="x")

        self.ac_master_frame = ctk.CTkFrame(self)
        self.ac_master_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        
        ac_header = ctk.CTkFrame(self.ac_master_frame, fg_color="transparent")
        ac_header.pack(fill="x", padx=10)
        
        self.ac_switch = ctk.CTkSwitch(ac_header, text="Auto Clicker Master", font=("Roboto", 14, "bold"), command=self.toggle_ac_master)
        self.ac_switch.pack(side="left", pady=10)
        
        ctk.CTkButton(ac_header, text="+ Bot Ekle", width=80, fg_color="#27ae60", hover_color="#2ecc71", command=self.add_new_clicker).pack(side="right", padx=10)

        self.clickers_container = ctk.CTkScrollableFrame(self.ac_master_frame, height=300)
        self.clickers_container.pack(fill="x", padx=10, pady=5)

        hs_frame = ctk.CTkFrame(self)
        hs_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.hs_switch = ctk.CTkSwitch(hs_frame, text="Hold & Scroll", font=("Roboto", 14, "bold"), command=self.toggle_hs_master)
        self.hs_switch.pack(pady=10)

        hs_box = ctk.CTkFrame(hs_frame, fg_color="#2c3e50")
        hs_box.pack(pady=5, fill="x", padx=10)
        self.hs_trig = self.create_input(hs_box, "Trig:", config['HOLD_SCROLL']['trigger_key'], 70)
        self.hs_mode = ctk.CTkOptionMenu(hs_box, values=["hold", "scroll_up", "scroll_down"], width=100)
        self.hs_mode.set(config['HOLD_SCROLL']['mode'])
        self.hs_mode.pack(side="left", padx=5)
        self.hs_target = self.create_input(hs_box, "Tgt:", config['HOLD_SCROLL']['target_key'], 40)
        ctk.CTkButton(hs_box, text="Ok", width=30, command=self.save_hs).pack(side="left", padx=5)

        rnd_frame = ctk.CTkFrame(self)
        rnd_frame.grid(row=4, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(rnd_frame, text="Random Clicker Settings", font=("Roboto", 14, "bold")).pack(pady=5)
        
        rnd_sett = ctk.CTkFrame(rnd_frame, fg_color="transparent")
        rnd_sett.pack(pady=5)
        self.rnd_target = self.create_input(rnd_sett, "Tgt:", config['RANDOM_CLICKER']['target_key'], 60)
        self.rnd_int = self.create_input(rnd_sett, "Max Int:", config['RANDOM_CLICKER']['max_interval'], 50)
        ctk.CTkButton(rnd_sett, text="Ok", width=30, command=self.save_rnd).pack(side="left", padx=5)
        
        self.rnd_btn = ctk.CTkButton(rnd_frame, text="Random Clicker: KAPALI", fg_color="gray", command=self.toggle_random)
        self.rnd_btn.pack(pady=10, padx=20, fill="x")

        self.log = ctk.CTkTextbox(self, height=80)
        self.log.grid(row=5, column=0, pady=10, padx=20, sticky="nsew")
        self.update_loop()

    def create_input(self, parent, label, default, width):
        ctk.CTkLabel(parent, text=label).pack(side="left", padx=2)
        entry = ctk.CTkEntry(parent, width=width)
        entry.insert(0, default)
        entry.pack(side="left", padx=5)
        return entry

    def load_dynamic_clickers(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        for section in config.sections():
            if section.startswith("CLICKER_"):
                self.render_clicker_row(section, config[section])

    def add_new_clicker(self):
        new_id = f"CLICKER_{uuid.uuid4().hex[:4].upper()}"
        default_data = {"trigger_key": "x", "target_key": "y", "delay": "1.0"}
        self.save_config_value(new_id, "trigger_key", "x")
        self.save_config_value(new_id, "target_key", "y")
        self.save_config_value(new_id, "delay", "1.0")
        self.render_clicker_row(new_id, default_data)
        self.log.insert("end", f"\n[Sistem] Yeni bot eklendi: {new_id}")

    def render_clicker_row(self, section_id, data):
        frame = ctk.CTkFrame(self.clickers_container, fg_color="#34495e")
        frame.pack(fill="x", pady=2, padx=5)
        
        ctk.CTkLabel(frame, text=f"ID: {section_id.split('_')[1]}", font=("Roboto", 10, "bold")).pack(side="left", padx=5)
        
        trig_entry = ctk.CTkEntry(frame, width=60)
        trig_entry.insert(0, data['trigger_key'])
        trig_entry.pack(side="left", padx=2)
        
        tgt_entry = ctk.CTkEntry(frame, width=40)
        tgt_entry.insert(0, data['target_key'])
        tgt_entry.pack(side="left", padx=2)
        
        dly_entry = ctk.CTkEntry(frame, width=40)
        dly_entry.insert(0, data['delay'])
        dly_entry.pack(side="left", padx=2)

        ctk.CTkButton(frame, text="Kaydet", width=40, command=lambda s=section_id, t=trig_entry, tg=tgt_entry, d=dly_entry: self.update_clicker_config(s, t, tg, d)).pack(side="left", padx=2)
        ctk.CTkButton(frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c", command=lambda s=section_id, f=frame: self.remove_clicker(s, f)).pack(side="right", padx=5)
        
        self.active_clickers[section_id] = AutoClicker(section_id)
        self.clicker_frames[section_id] = frame

    def update_clicker_config(self, s, t, tg, d):
        self.save_config_value(s, "trigger_key", t.get())
        self.save_config_value(s, "target_key", tg.get())
        self.save_config_value(s, "delay", d.get())
        self.log.insert("end", f"\n[{s}] Ayarları güncellendi.")

    def remove_clicker(self, section_id, frame):
        if section_id in self.active_clickers:
            self.active_clickers[section_id].stop()
            del self.active_clickers[section_id]
        self.remove_config_section(section_id)
        frame.destroy()
        self.log.insert("end", f"\n[Sistem] {section_id} silindi.")

    def save_sprint(self):
        self.save_config_value('SETTINGS', 'key_to_press', self.sprint_key.get())
        self.save_config_value('SETTINGS', 'hold_duration', self.sprint_hold.get())
        self.save_config_value('SETTINGS', 'wait_duration', self.sprint_wait.get())
        self.log.insert("end", "\n[Sprint] Ayarları kaydedildi.")

    def save_hs(self):
        self.save_config_value("HOLD_SCROLL", "trigger_key", self.hs_trig.get())
        self.save_config_value("HOLD_SCROLL", "mode", self.hs_mode.get())
        self.save_config_value("HOLD_SCROLL", "target_key", self.hs_target.get())
        self.log.insert("end", "\n[Hold] Ayarları kaydedildi.")

    def save_rnd(self):
        self.save_config_value("RANDOM_CLICKER", "target_key", self.rnd_target.get())
        self.save_config_value("RANDOM_CLICKER", "max_interval", self.rnd_int.get())
        self.log.insert("end", "\n[Random] Ayarları kaydedildi.")

    def toggle_sprint(self):
        if self.sprint.running: self.sprint.stop()
        else: self.sprint.start()

    def toggle_ac_master(self):
        self.autoclicker_enabled = self.ac_switch.get()
        if not self.autoclicker_enabled:
            for ac in self.active_clickers.values(): ac.stop()

    def toggle_hs_master(self):
        self.holdscroll_enabled = self.hs_switch.get()
        if not self.holdscroll_enabled: self.hold_scroll.stop()

    def toggle_random(self):
        if self.rnd.running: self.rnd.stop()
        else: self.rnd.start()

    def update_loop(self):
        if self.sprint.running:
            color = "#f39c12" if self.sprint.cooldown_remaining > 0 else "#27ae60"
            text = f"Ready in: {self.sprint.cooldown_remaining}s" if self.sprint.cooldown_remaining > 0 else "SPRINT: AKTİF"
            self.sprint_btn.configure(text=text, fg_color=color)
        else:
            self.sprint_btn.configure(text="Toggle: RUN", fg_color="#e74c3c")
        
        if self.rnd.running: self.rnd_btn.configure(text="Random Clicker: AKTİF", fg_color="#27ae60")
        else: self.rnd_btn.configure(text="Random Clicker: KAPALI", fg_color="gray")
        self.after(200, self.update_loop)

    def start_listeners(self):
        def handle_trigger(trigger_name):
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            if self.autoclicker_enabled:
                for section_id, ac in self.active_clickers.items():
                    if trigger_name == config[section_id]['trigger_key']:
                        ac.stop() if ac.running else ac.start()
            
            if self.holdscroll_enabled:
                if trigger_name == config['HOLD_SCROLL']['trigger_key']:
                    self.hold_scroll.toggle()

        def on_press(key):
            try:
                char = hasattr(key, 'char') and key.char or str(key).replace("Key.", "")
                handle_trigger(char.lower())
            except: pass

        def on_click(x, y, button, pressed):
            if not pressed: return
            btn_map = {Button.left: "mouse1", Button.right: "mouse2", Button.middle: "mouse3", Button.x1: "mouse4", Button.x2: "mouse5"}
            btn_name = btn_map.get(button, f"mouse_{button.name}")
            handle_trigger(btn_name)

        Listener(on_press=on_press).start()
        MouseListener(on_click=on_click).start()

if __name__ == "__main__":
    app = GameBotUI()
    app.mainloop()