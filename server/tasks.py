from flask import Flask, render_template
import subprocess

app = Flask(__name__)

# Tasks for green buttons
green_tasks = ["music_generator", "rave_generator", "dogshow_generator", "environments_generator"]

# Tasks for blue buttons
blue_tasks = ["mirror_to_post","sleep"]

@app.route('/run_task/<task_name>')
def run_task(task_name):
    if task_name in green_tasks or task_name in blue_tasks:
        subprocess.Popen(['schtasks', '/run', '/tn', task_name])
        return f"Task {task_name} Started!"
    else:
        return "Task not found", 404

@app.route('/')
def home():
    return render_template('index.html', green_tasks=green_tasks, blue_tasks=blue_tasks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
