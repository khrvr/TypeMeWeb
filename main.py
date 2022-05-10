import tkinter as tk
import time
import string
import threading
import json

window_color = "#cac9cd"
frame_color = "#eee7e4"
button_color = "#f2eceb"
text_line_color = frame_color
frozen_color = "#8f8a89"
label_color = text_line_color
label_font = "Modern 50"
button_font = "Modern 7"
text_line_font = "Modern 15 bold"
wdth = 700
hght = 350

allowed_chars = list(string.ascii_lowercase)

space_representor = "_"

chars = 50

session_time = 0
session_mistakes = 0
session_correct = 0
session_cpm = 0
session_perc = 0


class CustomFrame(tk.Frame):
    def __init__(self, window, side, width, height):
        super().__init__(master=window, width=width, height=height, bg=frame_color)
        self.pack(fill=tk.BOTH, side=side)


class CustomButton(tk.Button):
    def __init__(self, frame, side, text, command):
        super().__init__(master=frame, text=text, command=command, font=button_font, bg=button_color)
        self.pack(side=side, padx=5, pady=5)


class CustomLabel(tk.Label):
    def __init__(self, frame, side, textvar):
        super().__init__(master=frame, textvariable=textvar, font=label_font, bg=label_color)
        self.custom_side = side

    def pack(self):
        super().pack(side=self.custom_side)


def cpm_perc_update():
    global session_cpm
    if not session_time == 0:
        session_cpm.set(str(round(session_correct / (session_time / 60))) + "CPM")
    else:
        session_cpm.set("0 CPM")
    global session_perc
    if not session_correct + session_mistakes == 0:
        session_perc.set(str(round((session_correct / (session_correct + session_mistakes)) * 100)) + "%")
    else:
        session_perc.set("0")


class TextLine(tk.Label):
    def __init__(self, frame, filename):
        super().__init__(master=frame, bg=text_line_color, width=40, height=5, font=text_line_font)
        self.filename = filename
        self.pack(fill=tk.BOTH)
        self.focus_set()
        self.state = "initial"
        self.config(text="Press enter to start, esc to pause")
        self.bind("<Return>", self.play)
        self.bind("<Escape>", self.freeze)
        self.text = []
        self.text_point = 0
        self.start_time = 0
        self.mistakes = 0
        self.correct = 0

    def get_text(self):
        self.text = []
        with open(self.filename) as f:
            while True:
                c = f.read(1)
                if not c:
                    break
                if c.lower() in allowed_chars:
                    self.text.append(c.lower())
                elif c == "\t" or c == " ":
                    self.text.append(space_representor)

    def reset_stats(self):
        self.start_time = time.time()
        self.mistakes = 0
        self.correct = 0

    def save_stats(self):
        global session_time
        session_time += time.time() - self.start_time
        global session_mistakes
        session_mistakes += self.mistakes
        global session_correct
        session_correct += self.correct
        cpm_perc_update()
        self.reset_stats()

    def stats_auto_save(self):
        if self.state == "playing":
            threading.Timer(3.0, self.stats_auto_save).start()
            if self.state == "playing":
                self.save_stats()

    def freeze(self, event):
        if self.state == "frozen" or self.state == "initial":
            return
        self.state = "frozen"
        self.config(bg=frozen_color)
        self.custom_unbind()

    def custom_bind(self, custom_bind=True):
        def smart_unbind(event, *args, **kwargs):
            self.unbind(event)
        if custom_bind:
            current_binding = self.bind
        else:
            current_binding = smart_unbind
        current_binding("<space>", self.handle_user_click)
        for letter in allowed_chars:
            current_binding(letter, self.handle_user_click)

    def custom_unbind(self):
        self.custom_bind(custom_bind=False)

    def terminate_run(self):
        self.configure(text="Press enter to start, esc to pause")
        self.text_point = 0
        self.custom_unbind()
        if self.state == "frozen":
            self.config(bg=text_line_color)
        self.state = "initial"

    def show_text(self):
        if self.text_point < len(self.text):
            newchars = min(chars, len(self.text) - self.text_point)
            newtext = ''.join(self.text[self.text_point:self.text_point + newchars])
            self.config(text=newtext)
        else:
            self.terminate_run()

    def handle_user_click(self, event):
        nextchar = self.text[self.text_point]
        key = event.keysym
        if key == "space":
            key = "_"
        if key == nextchar:
            self.correct += 1
            self.text_point += 1
            self.show_text()
        else:
            self.mistakes += 1

    def play(self, event):
        if self.state == "playing":
            return
        if self.state == "frozen":
            self.config(bg=text_line_color)
        self.get_text()
        self.state = "playing"
        self.custom_bind()
        self.show_text()
        self.reset_stats()
        self.stats_auto_save()


class CustomWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TypeMe")
        self.geometry("{v0}x{v1}+100+100".format(v0=wdth, v1=hght))
        self.resizable(False, False)
        self.configure(bg=window_color)
        self.protocol("WM_DELETE_WINDOW", self.dump_data_and_quit)
        try:
            with open('stats.json', 'r') as f:
                global session_mistakes, session_correct, session_time
                [session_correct, session_mistakes, session_time] = json.load(f)
        except FileNotFoundError:
            pass
        self.bottom_frame = CustomFrame(self, tk.BOTTOM, wdth, hght//3)
        self.main_frame = CustomFrame(self, tk.TOP, wdth, hght - hght//3)
        self.text_line = TextLine(self.main_frame, 'test_text.txt')
        self.restart_button = CustomButton(self.bottom_frame, tk.LEFT, "RESTART", self.text_line.terminate_run)
        self.stats_button = CustomButton(self.bottom_frame, tk.LEFT, "STATS", self.show_stats)
        global session_perc, session_cpm
        session_perc = tk.StringVar()
        session_cpm = tk.StringVar()
        cpm_perc_update()
        self.stats_speed_label = CustomLabel(self.main_frame, tk.LEFT, session_cpm)
        self.stats_perc_label = CustomLabel(self.main_frame, tk.RIGHT, session_perc)
        self.showing = False
        self.selecting = False

    def dump_data_and_quit(self):
        with open('stats.json', 'w') as f:
            json.dump([session_correct, session_mistakes, session_time], f)
        self.quit()
        self.destroy()

    def show_stats(self):
        if not self.showing:
            self.showing = True
            self.stats_speed_label.pack()
            self.stats_perc_label.pack()
        else:
            self.showing = False
            self.stats_speed_label.pack_forget()
            self.stats_perc_label.pack_forget()


mainWindow = CustomWindow()

mainWindow.mainloop()
