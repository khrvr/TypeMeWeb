import string
import time
import threading
import json

allowed_chars = list(string.ascii_lowercase)

space_representor = "_"

chars = 70

session_time = 0
session_mistakes = 0
session_correct = 0
session_cpm = 0
session_perc = 0


text_line_color = "#eee7e4"
frozen_color = "#8f8a89"
current_text_line_color = text_line_color


def cpm_perc_update():
    global session_cpm
    if not session_time == 0:
        session_cpm = (str(round(session_correct / (session_time / 60))) + "CPM")
    else:
        session_cpm = "0 CPM"
    global session_perc
    if not session_correct + session_mistakes == 0:
        session_perc = (str(round((session_correct / (session_correct + session_mistakes)) * 100)) + "%")
    else:
        session_perc = "0"


class TextLine:
    def __init__(self, filename):
        global current_text_line_color
        current_text_line_color = text_line_color
        self.filename = filename
        self.state = "initial"
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

    def freeze(self):
        if self.state == "frozen":
            return
        self.state = "frozen"
        global current_text_line_color
        current_text_line_color = frozen_color

    def terminate_run(self):
        self.save_stats()
        with open('stats.json', 'w') as f:
            json.dump([session_correct, session_mistakes, session_time], f)
        global current_text_line_color
        current_text_line_color = text_line_color
        self.text_point = 0
        self.state = "initial"

    def update_text(self):
        if self.text_point < len(self.text):
            newchars = min(chars, len(self.text) - self.text_point)
            newtext = ''.join(self.text[self.text_point:self.text_point + newchars])
            return newtext
        else:
            self.terminate_run()
            return ''

    def handle_user_click(self, key):
        if key == "ent":
            self.state = "ready to play"
            self.play()
        elif self.state == "frozen":
            pass
        elif key == "shf":
            self.freeze()
        else:
            nextchar = self.text[self.text_point]
            if key == " ":
                key = "_"
            if key == nextchar:
                self.correct += 1
                self.text_point += 1
            else:
                self.mistakes += 1

    def play(self):
        if self.state == "initial" or self.state == "ready to play":
            self.get_text()
            self.state = "playing"
            global current_text_line_color
            current_text_line_color = text_line_color
            self.reset_stats()
            self.stats_auto_save()
