import customtkinter as ctk
import configparser
import uuid
from pynput.keyboard import Listener, Key
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
        self.title("Wichelberg Ultimate Pro Logic")
        self.geometry("850x1000")
        
        self.sprint = SprintManager()
        self.rnd = RandomClicker()
        self.hold_scroll = HoldScrollManager()
        self.active_clickers = {}
        self.indicators = {}
        self.autoclicker_enabled = False
        self.holdscroll_enabled = False

        self.setup_ui()
        self.load_from_config()
        self.start_listeners()
        self.update_loop()

    def log_msg(self, msg):
        self.terminal.insert("end", f"\n>> {msg}")
        self.terminal.see("end")

    def create_indicator(self, parent):
        canvas = ctk.CTkCanvas(parent, width=15, height=15, highlightthickness=0, bg="#2b2b2b")
        canvas.pack(side="right", padx=10)
        circle = canvas.create_oval(2, 2, 13, 13, fill="red")
        return canvas, circle

    def update_indicator(self, key, is_active):
        if key in self.indicators:
            canvas, circle = self.indicators[key]
            canvas.itemconfig(circle, fill="green" if is_active else "red")

    def add_input(self, p, l, d, w):
        ctk.CTkLabel(p, text=l).pack(side="left", padx=2)
        e = ctk.CTkEntry(p, width=w); e.insert(0, d); e.pack(side="left", padx=5)
        return e

    def setup_ui(self):
        config = configparser.ConfigParser(); config.read('config.ini')

        # --- SPRINT ---
        s_frame = ctk.CTkFrame(self)
        s_frame.pack(pady=5, padx=20, fill="x")
        h1 = ctk.CTkFrame(s_frame, fg_color="transparent"); h1.pack(fill="x")
        ctk.CTkLabel(h1, text="Sprint (Toggle)", font=("Roboto", 16, "bold")).pack(side="left", padx=10)
        self.indicators['sprint'] = self.create_indicator(h1)
        s_box = ctk.CTkFrame(s_frame, fg_color="transparent"); s_box.pack(pady=5)
        self.s_trig = self.add_input(s_box, "Trig:", config['SETTINGS'].get('trigger_key','t'), 50)
        self.s_tgt = self.add_input(s_box, "Target:", config['SETTINGS'].get('key_to_press','w'), 50)
        self.s_h = self.add_input(s_box, "Hold:", config['SETTINGS'].get('hold_duration','5'), 40)
        self.s_w = self.add_input(s_box, "Wait:", config['SETTINGS'].get('wait_duration','10'), 40)
        ctk.CTkButton(s_box, text="Save", width=40, command=self.save_sprint).pack(side="left", padx=5)

        # --- AUTO CLICKER ---
        ac_frame = ctk.CTkFrame(self)
        ac_frame.pack(pady=5, padx=20, fill="x")
        h2 = ctk.CTkFrame(ac_frame, fg_color="transparent"); h2.pack(fill="x")
        self.ac_sw = ctk.CTkSwitch(h2, text="Auto Clicker Master", command=self.toggle_ac_master)
        self.ac_sw.pack(side="left", padx=10)
        ctk.CTkButton(h2, text="+ Add Bot", width=80, fg_color="green", command=self.add_new_clicker).pack(side="right", padx=10)
        self.ac_container = ctk.CTkScrollableFrame(ac_frame, height=200); self.ac_container.pack(fill="x", padx=10, pady=5)

        # --- RANDOM CLICKER ---
        r_frame = ctk.CTkFrame(self)
        r_frame.pack(pady=5, padx=20, fill="x")
        h3 = ctk.CTkFrame(r_frame, fg_color="transparent"); h3.pack(fill="x")
        ctk.CTkLabel(h3, text="Random Clicker", font=("Roboto", 16, "bold")).pack(side="left", padx=10)
        self.indicators['random'] = self.create_indicator(h3)
        r_box = ctk.CTkFrame(r_frame, fg_color="transparent"); r_box.pack(pady=5)
        self.r_trig = self.add_input(r_box, "Trig:", config['RANDOM_CLICKER'].get('trigger_key','r'), 50)
        self.r_tgt = self.add_input(r_box, "Tgt:", config['RANDOM_CLICKER'].get('target_key','f'), 50)
        self.r_min = self.add_input(r_box, "Min:", config['RANDOM_CLICKER'].get('min_interval','1'), 40)
        self.r_max = self.add_input(r_box, "Max:", config['RANDOM_CLICKER'].get('max_interval','5'), 40)
        ctk.CTkButton(r_box, text="Save", width=40, command=self.save_random).pack(side="left", padx=5)

        # --- HOLD & SCROLL ---
        hs_frame = ctk.CTkFrame(self)
        hs_frame.pack(pady=5, padx=20, fill="x")
        h4 = ctk.CTkFrame(hs_frame, fg_color="transparent"); h4.pack(fill="x")
        self.hs_sw = ctk.CTkSwitch(h4, text="Hold & Scroll Master", command=self.toggle_hs_master)
        self.hs_sw.pack(side="left", padx=10)
        self.indicators['hold'] = self.create_indicator(h4)
        hs_box = ctk.CTkFrame(hs_frame, fg_color="transparent"); hs_box.pack(pady=5)
        self.hs_trig = self.add_input(hs_box, "Trig:", config['HOLD_SCROLL'].get('trigger_key','h'), 60)
        self.hs_mode = ctk.CTkOptionMenu(hs_box, values=["hold", "scroll_up", "scroll_down"], width=100)
        self.hs_mode.set(config['HOLD_SCROLL'].get('mode','hold'))
        self.hs_mode.pack(side="left", padx=5)
        self.hs_tgt = self.add_input(hs_box, "Tgt:", config['HOLD_SCROLL'].get('target_key','mouse1'), 50)
        ctk.CTkButton(hs_box, text="Save", width=40, command=self.save_hs).pack(side="left", padx=5)

        # --- TERMINAL / LOG ---
        ctk.CTkLabel(self, text="Terminal Output", font=("Roboto", 12, "italic")).pack(pady=(10,0))
        self.terminal = ctk.CTkTextbox(self, height=150, fg_color="#1a1a1a", text_color="#00ff00")
        self.terminal.pack(fill="both", padx=20, pady=10)
        self.log_msg("Sistem başlatıldı. Yapılandırma yüklendi.")

    def load_from_config(self):
        config = configparser.ConfigParser(); config.read('config.ini')
        for sec in config.sections():
            if sec.startswith("CLICKER_"): self.render_clicker_row(sec, config[sec])

    def add_new_clicker(self):
        new_id = f"CLICKER_{uuid.uuid4().hex[:4].upper()}"
        data = {'trigger_key': 'k', 'target_key': 'q', 'delay': '1.0'}
        for k, v in data.items(): self.save_val(new_id, k, v)
        self.render_clicker_row(new_id, data)
        self.log_msg(f"Yeni bot eklendi: {new_id}")

    def render_clicker_row(self, sid, data):
        f = ctk.CTkFrame(self.ac_container, fg_color="#34495e"); f.pack(fill="x", pady=2)
        self.indicators[sid] = self.create_indicator(f)
        t = ctk.CTkEntry(f, width=60); t.insert(0, data.get('trigger_key','x')); t.pack(side="left", padx=2)
        tg = ctk.CTkEntry(f, width=40); tg.insert(0, data.get('target_key','y')); tg.pack(side="left", padx=2)
        d = ctk.CTkEntry(f, width=40); d.insert(0, data.get('delay','1.0')); d.pack(side="left", padx=2)
        ctk.CTkButton(f, text="Ok", width=30, command=lambda: [self.save_val(sid, 'trigger_key', t.get()), self.save_val(sid, 'target_key', tg.get()), self.save_val(sid, 'delay', d.get()), self.log_msg(f"{sid} güncellendi.")]).pack(side="left", padx=2)
        ctk.CTkButton(f, text="X", width=30, fg_color="red", command=lambda: self.remove_bot(sid, f)).pack(side="right", padx=5)
        self.active_clickers[sid] = AutoClicker(sid)

    def remove_bot(self, sid, f):
        if sid in self.active_clickers: self.active_clickers[sid].stop(); del self.active_clickers[sid]
        config = configparser.ConfigParser(); config.read('config.ini')
        if config.has_section(sid): 
            config.remove_section(sid); 
            with open('config.ini', 'w') as cf: config.write(cf)
        f.destroy()
        self.log_msg(f"Bot silindi: {sid}")

    def save_val(self, s, k, v):
        config = configparser.ConfigParser(); config.read('config.ini')
        if s not in config: config.add_section(s)
        config.set(s, k, str(v))
        with open('config.ini', 'w') as cf: config.write(cf)

    def save_sprint(self):
        for k,v in {'trigger_key':self.s_trig.get(), 'key_to_press':self.s_tgt.get(), 'hold_duration':self.s_h.get(), 'wait_duration':self.s_w.get()}.items():
            self.save_val('SETTINGS', k, v)
        self.log_msg("Sprint ayarları kaydedildi.")

    def save_random(self):
        for k,v in {'trigger_key':self.r_trig.get(), 'target_key':self.r_tgt.get(), 'min_interval':self.r_min.get(), 'max_interval':self.r_max.get()}.items():
            self.save_val('RANDOM_CLICKER', k, v)
        self.log_msg("Random clicker ayarları kaydedildi.")

    def save_hs(self):
        for k,v in {'trigger_key':self.hs_trig.get(), 'mode':self.hs_mode.get(), 'target_key':self.hs_tgt.get()}.items():
            self.save_val('HOLD_SCROLL', k, v)
        self.log_msg("Hold & Scroll ayarları kaydedildi.")

    def toggle_ac_master(self): 
        self.autoclicker_enabled = self.ac_sw.get()
        if not self.autoclicker_enabled:
            for ac in self.active_clickers.values(): ac.stop()
        self.log_msg(f"Auto Clicker Master: {'AÇIK' if self.autoclicker_enabled else 'KAPALI'}")

    def toggle_hs_master(self): 
        self.holdscroll_enabled = self.hs_sw.get()
        if not self.holdscroll_enabled: self.hold_scroll.stop()
        self.log_msg(f"Hold & Scroll Master: {'AÇIK' if self.holdscroll_enabled else 'KAPALI'}")

    def update_loop(self):
        self.update_indicator('sprint', self.sprint.running)
        self.update_indicator('random', self.rnd.running)
        self.update_indicator('hold', self.hold_scroll.running)
        for sid, ac in self.active_clickers.items(): self.update_indicator(sid, ac.running)
        self.after(300, self.update_loop)

    def start_listeners(self):
        def handle(key):
            config = configparser.ConfigParser(); config.read('config.ini')
            if key == config['SETTINGS'].get('trigger_key'): 
                self.sprint.stop() if self.sprint.running else self.sprint.start()
                self.log_msg(f"Sprint tetiklendi (T: {key})")
            if key == config['RANDOM_CLICKER'].get('trigger_key'): 
                self.rnd.stop() if self.rnd.running else self.rnd.start()
                self.log_msg(f"Random tetiklendi (T: {key})")
            if self.autoclicker_enabled:
                for sid, ac in self.active_clickers.items():
                    if key == config[sid].get('trigger_key'): 
                        ac.stop() if ac.running else ac.start()
                        self.log_msg(f"Bot {sid} tetiklendi (T: {key})")
            if self.holdscroll_enabled:
                if key == config['HOLD_SCROLL'].get('trigger_key'): 
                    self.hold_scroll.stop() if self.hold_scroll.running else self.hold_scroll.start()
                    self.log_msg(f"Hold tetiklendi (T: {key})")
        
        def on_p(k):
            try: handle((hasattr(k, 'char') and k.char or str(k).replace("Key.","")).lower())
            except: pass
        def on_c(x,y,b,p):
            if p:
                m_map = {Button.left:"mouse1", Button.right:"mouse2", Button.middle:"mouse3", Button.x1:"mouse4", Button.x2:"mouse5"}
                handle(m_map.get(b, f"mouse_{b.name}"))
        
        Listener(on_press=on_p, daemon=True).start()
        MouseListener(on_click=on_c, daemon=True).start()

if __name__ == "__main__":
    GameBotUI().mainloop()