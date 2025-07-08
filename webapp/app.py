from flask import Flask, render_template, request, redirect, url_for
from crontab import CronTab
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
JOBS_FILE = APP_ROOT / 'jobs.json'

app = Flask(__name__)


def load_jobs():
    if JOBS_FILE.exists():
        return json.loads(JOBS_FILE.read_text())
    return []


def save_jobs(jobs):
    JOBS_FILE.write_text(json.dumps(jobs, indent=2))


def list_generators():
    gens = []
    for p in (APP_ROOT / 'generators').iterdir():
        if (p / 'call.py').is_file():
            gens.append(p.name)
    return gens


@app.route('/')
def index():
    return render_template('index.html', jobs=load_jobs())


@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        gen = request.form['generator']
        schedule = request.form['schedule']
        notify = bool(request.form.get('notify'))

        cron = CronTab(user=True)
        command = f'python3 {APP_ROOT}/job_runner.py {gen}'
        if notify:
            command += ' --notify'
        job = cron.new(command=command)
        job.setall(schedule)
        cron.write()

        jobs = load_jobs()
        jobs.append({'generator': gen, 'schedule': schedule, 'notify': notify})
        save_jobs(jobs)
        return redirect(url_for('index'))

    gens = list_generators()
    return render_template('add_job.html', generators=gens)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
