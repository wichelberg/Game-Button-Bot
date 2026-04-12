import customtkinter as ctk
import configparser
from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener, Button
from sprint_logic import SprintManager
from logic_layers import AutoClicker
from random_logic import RandomClicker
from hold_logic import HoldScrollManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GameBotUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wichelberg Center")
        self.geometry("700x950")
        
        self.sprint = SprintManager()
        self.c1 = AutoClicker("CLICKER_1")
        self.c2 = AutoClicker("CLICKER_2")
        self.rnd = RandomClicker()
        self.hold_scroll = HoldScrollManager()

        self.autoclicker_enabled = False
        self.holdscroll_enabled = False

        self.setup_ui()
        self.start_listeners()

    def save_config_value(self, section, key, value):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if section not in config: config.add_section(section)
        config.set(section, key, str(value))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        config = configparser.ConfigParser()
        config.read('config.ini')

        ctk.CTkLabel(self, text="Wichelberg Center", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=20)

        # --- 1. MAX SPRINT (Tuş + Hold + Wait) ---
        s_frame = ctk.CTkFrame(self)
        s_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(s_frame, text="Toggle", font=("Roboto", 16, "bold")).pack(pady=5)
        
        s_sett = ctk.CTkFrame(s_frame, fg_color="transparent")
        s_sett.pack(pady=5)
        ctk.CTkLabel(s_sett, text="Tuş:").pack(side="left", padx=2)
        self.sprint_key = ctk.CTkEntry(s_sett, width=60)
        self.sprint_key.insert(0, config['SETTINGS']['key_to_press'])
        self.sprint_key.pack(side="left", padx=5)
        
        ctk.CTkLabel(s_sett, text="Hold:").pack(side="left", padx=2)
        self.sprint_hold = ctk.CTkEntry(s_sett, width=40)
        self.sprint_hold.insert(0, config['SETTINGS']['hold_duration'])
        self.sprint_hold.pack(side="left", padx=5)
        
        ctk.CTkLabel(s_sett, text="Wait:").pack(side="left", padx=2)
        self.sprint_wait = ctk.CTkEntry(s_sett, width=40)
        self.sprint_wait.insert(0, config['SETTINGS']['wait_duration'])
        self.sprint_wait.pack(side="left", padx=5)
        
        ctk.CTkButton(s_sett, text="Kaydet", width=50, command=self.save_sprint).pack(side="left", padx=5)
        self.sprint_btn = ctk.CTkButton(s_frame, text="Toggle: RUN", command=self.toggle_sprint)
        self.sprint_btn.pack(pady=10, padx=20, fill="x")

        # --- 2. AUTO CLICKER (Trigger + Target + Delay) ---
        ac_frame = ctk.CTkFrame(self)
        ac_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        self.ac_switch = ctk.CTkSwitch(ac_frame, text="Auto Clicker", font=("Roboto", 14, "bold"), command=self.toggle_ac_master)
        self.ac_switch.pack(pady=10)

        # C1
        c1_box = ctk.CTkFrame(ac_frame, fg_color="#2c3e50")
        c1_box.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(c1_box, text="C1 Trig:").pack(side="left", padx=2)
        self.c1_trig = ctk.CTkEntry(c1_box, width=70)
        self.c1_trig.insert(0, config['CLICKER_1']['trigger_key'])
        self.c1_trig.pack(side="left", padx=2)
        ctk.CTkLabel(c1_box, text="Tgt:").pack(side="left", padx=2)
        self.c1_target = ctk.CTkEntry(c1_box, width=40)
        self.c1_target.insert(0, config['CLICKER_1']['target_key'])
        self.c1_target.pack(side="left", padx=2)
        ctk.CTkLabel(c1_box, text="Dly:").pack(side="left", padx=2)
        self.c1_delay = ctk.CTkEntry(c1_box, width=40)
        self.c1_delay.insert(0, config['CLICKER_1']['delay'])
        self.c1_delay.pack(side="left", padx=2)
        ctk.CTkButton(c1_box, text="Ok", width=30, command=lambda: self.save_ac(1)).pack(side="left", padx=5)

        # C2
        c2_box = ctk.CTkFrame(ac_frame, fg_color="#2c3e50")
        c2_box.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(c2_box, text="C2 Trig:").pack(side="left", padx=2)
        self.c2_trig = ctk.CTkEntry(c2_box, width=70)
        self.c2_trig.insert(0, config['CLICKER_2']['trigger_key'])
        self.c2_trig.pack(side="left", padx=2)
        ctk.CTkLabel(c2_box, text="Tgt:").pack(side="left", padx=2)
        self.c2_target = ctk.CTkEntry(c2_box, width=40)
        self.c2_target.insert(0, config['CLICKER_2']['target_key'])
        self.c2_target.pack(side="left", padx=2)
        ctk.CTkLabel(c2_box, text="Dly:").pack(side="left", padx=2)
        self.c2_delay = ctk.CTkEntry(c2_box, width=40)
        self.c2_delay.insert(0, config['CLICKER_2']['delay'])
        self.c2_delay.pack(side="left", padx=2)
        ctk.CTkButton(c2_box, text="Ok", width=30, command=lambda: self.save_ac(2)).pack(side="left", padx=5)

        # --- 3. HOLD & SCROLL ---
        hs_frame = ctk.CTkFrame(self)
        hs_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.hs_switch = ctk.CTkSwitch(hs_frame, text="Hold & Scroll", font=("Roboto", 14, "bold"), command=self.toggle_hs_master)
        self.hs_switch.pack(pady=10)

        hs_box = ctk.CTkFrame(hs_frame, fg_color="#2c3e50")
        hs_box.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(hs_box, text="Trig:").pack(side="left", padx=2)
        self.hs_trig = ctk.CTkEntry(hs_box, width=70)
        self.hs_trig.insert(0, config['HOLD_SCROLL']['trigger_key'])
        self.hs_trig.pack(side="left", padx=5)
        self.hs_mode = ctk.CTkOptionMenu(hs_box, values=["hold", "scroll_up", "scroll_down"], width=100)
        self.hs_mode.set(config['HOLD_SCROLL']['mode'])
        self.hs_mode.pack(side="left", padx=5)
        self.hs_target = ctk.CTkEntry(hs_box, width=40)
        self.hs_target.insert(0, config['HOLD_SCROLL']['target_key'])
        self.hs_target.pack(side="left", padx=5)
        ctk.CTkButton(hs_box, text="Ok", width=30, command=self.save_hs).pack(side="left", padx=5)

        # --- 4. RANDOM CLICKER (Target + Interval) ---
        rnd_frame = ctk.CTkFrame(self)
        rnd_frame.grid(row=4, column=0, pady=10, padx=20, sticky="ew")
        ctk.CTkLabel(rnd_frame, text="Random Clicker", font=("Roboto", 14, "bold")).pack(pady=5)
        
        rnd_sett = ctk.CTkFrame(rnd_frame, fg_color="transparent")
        rnd_sett.pack(pady=5)
        ctk.CTkLabel(rnd_sett, text="Tgt:").pack(side="left", padx=2)
        self.rnd_target = ctk.CTkEntry(rnd_sett, width=60)
        self.rnd_target.insert(0, config['RANDOM_CLICKER']['target_key'])
        self.rnd_target.pack(side="left", padx=5)
        ctk.CTkLabel(rnd_sett, text="Max Int:").pack(side="left", padx=2)
        self.rnd_int = ctk.CTkEntry(rnd_sett, width=50)
        self.rnd_int.insert(0, config['RANDOM_CLICKER']['max_interval'])
        self.rnd_int.pack(side="left", padx=5)
        ctk.CTkButton(rnd_sett, text="Ok", width=30, command=self.save_rnd).pack(side="left", padx=5)
        
        self.rnd_btn = ctk.CTkButton(rnd_frame, text="Random Clicker: KAPALI", fg_color="gray", command=self.toggle_random)
        self.rnd_btn.pack(pady=10, padx=20, fill="x")

        # --- LOG ---
        self.log = ctk.CTkTextbox(self, height=100)
        self.log.grid(row=5, column=0, pady=20, padx=20, sticky="nsew")
        self.log.insert("0.0", "Ayarları güncelleyip 'Ok/Kaydet' butonuna basın.")

        self.update_loop()

    # --- SAVE ---
    def save_sprint(self):
        self.save_config_value('SETTINGS', 'key_to_press', self.sprint_key.get())
        self.save_config_value('SETTINGS', 'hold_duration', self.sprint_hold.get())
        self.save_config_value('SETTINGS', 'wait_duration', self.sprint_wait.get())
        self.log.insert("end", f"\n[Sprint] Güncellendi: {self.sprint_key.get()} (H:{self.sprint_hold.get()} W:{self.sprint_wait.get()})")

    def save_ac(self, num):
        sec = f"CLICKER_{num}"
        trig = self.c1_trig.get() if num == 1 else self.c2_trig.get()
        target = self.c1_target.get() if num == 1 else self.c2_target.get()
        delay = self.c1_delay.get() if num == 1 else self.c2_delay.get()
        self.save_config_value(sec, "trigger_key", trig); self.save_config_value(sec, "target_key", target)
        self.save_config_value(sec, "delay", delay)
        self.log.insert("end", f"\n[{sec}] Kaydedildi: {trig}->{target} (D:{delay})")

    def save_hs(self):
        self.save_config_value("HOLD_SCROLL", "trigger_key", self.hs_trig.get())
        self.save_config_value("HOLD_SCROLL", "mode", self.hs_mode.get())
        self.save_config_value("HOLD_SCROLL", "target_key", self.hs_target.get())
        self.log.insert("end", f"\n[Hold] Kaydedildi: {self.hs_trig.get()} Mod:{self.hs_mode.get()}")

    def save_rnd(self):
        self.save_config_value("RANDOM_CLICKER", "target_key", self.rnd_target.get())
        self.save_config_value("RANDOM_CLICKER", "max_interval", self.rnd_int.get())
        self.log.insert("end", f"\n[Random] Kaydedildi: {self.rnd_target.get()} (Int:{self.rnd_int.get()})")

    # --- TOGGLE ---
    def toggle_sprint(self):
        if self.sprint.running: self.sprint.stop()
        else: self.sprint.start()

    def toggle_ac_master(self):
        self.autoclicker_enabled = self.ac_switch.get()
        if not self.autoclicker_enabled: self.c1.stop(); self.c2.stop()

    def toggle_hs_master(self):
        self.holdscroll_enabled = self.hs_switch.get()
        if not self.holdscroll_enabled: self.hold_scroll.stop()

    def toggle_random(self):
        if self.rnd.running: self.rnd.stop()
        else: self.rnd.start()

    def update_loop(self):
        if self.sprint.running:
            color = "#f39c12" if self.sprint.cooldown_remaining > 0 else "#27ae60"
            text = f"Getting Ready: {self.sprint.cooldown_remaining}s" if self.sprint.cooldown_remaining > 0 else "SPRINT: AKTİF"
            self.sprint_btn.configure(text=text, fg_color=color)
        else:
            self.sprint_btn.configure(text="Toggle: RUN", fg_color="#e74c3c")
        if self.rnd.running: self.rnd_btn.configure(text="Random Clicker: Active", fg_color="#27ae60")
        else: self.rnd_btn.configure(text="Random Clicker: Closed", fg_color="gray")
        self.after(200, self.update_loop)

    def start_listeners(self):
        def handle_trigger(trigger_name):
            config = configparser.ConfigParser()
            config.read('config.ini')
            if self.autoclicker_enabled:
                if trigger_name == config['CLICKER_1']['trigger_key']: self.c1.stop() if self.c1.running else self.c1.start()
                elif trigger_name == config['CLICKER_2']['trigger_key']: self.c2.stop() if self.c2.running else self.c2.start()
            if self.holdscroll_enabled:
                if trigger_name == config['HOLD_SCROLL']['trigger_key']: self.hold_scroll.toggle()
        def on_press(key):
            try:
                char = hasattr(key, 'char') and key.char or str(key).replace("Key.", "")
                handle_trigger(char.lower())
            except: pass
        def on_click(x, y, button, pressed):
            if not pressed: return
            btn_name = "mouse4" if button == Button.x1 else "mouse5" if button == Button.x2 else None
            if btn_name: handle_trigger(btn_name)
        Listener(on_press=on_press).start()
        MouseListener(on_click=on_click).start()

if __name__ == "__main__":
    app = GameBotUI()
    app.mainloop()