from flask import Flask, render_template, request, url_for, redirect
import textLine
from textLine import TextLine
import json

app = Flask(__name__)

text_line = TextLine("test_text.txt")

default_message = "Press ENTER to start, SHIFT to pause"

displayed_text_line = default_message

stats_visible = False


@app.route('/', methods=('GET', 'POST'))
def index():
    global displayed_text_line
    displayed_text_line = default_message
    if request.method == 'POST':
        if "restart" in request.form.keys():
            pass
        elif "stats" in request.form.keys():
            global stats_visible
            stats_visible = not stats_visible
        else:
            text_line.play()
            return redirect(url_for('running'))
    return render_template('index.html', displayed_text_line=displayed_text_line,
                           current_text_line_color=textLine.current_text_line_color,
                           visible=stats_visible, session_cpm=textLine.session_cpm,
                           session_perc=textLine.session_perc)


@app.route('/running', methods=('GET', 'POST'))
def running():
    global displayed_text_line
    displayed_text_line = text_line.update_text()
    if request.method == 'POST':
        if "restart" in request.form.keys():
            text_line.terminate_run()
            return redirect(url_for('index'))
        elif "stats" in request.form.keys():
            global stats_visible
            stats_visible = not stats_visible
        else:
            text_line.handle_user_click(list(request.form.keys())[0])
            displayed_text_line = text_line.update_text()
            if displayed_text_line == '':
                text_line.terminate_run()
                return redirect(url_for('index'))
    return render_template('running.html', displayed_text_line=displayed_text_line,
                           current_text_line_color=textLine.current_text_line_color,
                           visible=stats_visible, session_cpm=textLine.session_cpm,
                           session_perc=textLine.session_perc)


@app.before_first_request
def upload_stats():
    try:
        with open('stats.json', 'r') as f:
            [textLine.session_correct, textLine.session_mistakes, textLine.session_time] = json.load(f)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    app.run()
