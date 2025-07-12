from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from crontab import CronTab
import json
from pathlib import Path
from datetime import datetime, timedelta
import os

APP_ROOT = Path(__file__).resolve().parent.parent
JOBS_FILE = APP_ROOT / 'jobs.json'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

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

def human_schedule_to_cron(schedule_type, schedule_data):
    """Convert human-readable schedule to cron format"""
    if schedule_type == "daily":
        hour, minute = schedule_data["time"].split(":")
        return f"{minute} {hour} * * *"
    elif schedule_type == "weekly":
        hour, minute = schedule_data["time"].split(":")
        days = ",".join(str(day) for day in schedule_data["days"])
        return f"{minute} {hour} * * {days}"
    elif schedule_type == "monthly":
        hour, minute = schedule_data["time"].split(":")
        day = schedule_data["day"]
        return f"{minute} {hour} {day} * *"
    elif schedule_type == "interval":
        minutes = schedule_data["minutes"]
        return f"*/{minutes} * * * *"
    else:
        return schedule_data.get("custom", "0 0 * * *")

def cron_to_human_readable(cron_expr):
    """Convert cron expression to human-readable format"""
    parts = cron_expr.split()
    if len(parts) != 5:
        return cron_expr
    
    minute, hour, day, month, weekday = parts
    
    if minute == "*" and hour == "*":
        return "Every minute"
    elif minute != "*" and hour == "*":
        return f"Every {minute} minutes"
    elif minute != "*" and hour != "*" and day == "*" and month == "*" and weekday == "*":
        return f"Daily at {hour}:{minute.zfill(2)}"
    elif minute != "*" and hour != "*" and day == "*" and month == "*" and weekday != "*":
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        selected_days = [days[int(d)-1] for d in weekday.split(",") if d.isdigit()]
        return f"Weekly on {', '.join(selected_days)} at {hour}:{minute.zfill(2)}"
    else:
        return cron_expr

def get_job_status(job):
    """Get the status of a job based on its last run and schedule"""
    # This is a simplified status check - in a real app you'd track actual execution
    return "Active"

@app.route('/')
def index():
    jobs = load_jobs()
    # Convert cron to human-readable for display
    for job in jobs:
        job['human_schedule'] = cron_to_human_readable(job['schedule'])
        job['status'] = get_job_status(job)
    return render_template('index.html', jobs=jobs)

@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        try:
            gen = request.form['generator']
            schedule_type = request.form['schedule_type']
            notify = bool(request.form.get('notify'))
            
            # Build schedule data based on type
            schedule_data = {}
            if schedule_type == "daily":
                schedule_data = {"time": request.form['daily_time']}
            elif schedule_type == "weekly":
                schedule_data = {
                    "time": request.form['weekly_time'],
                    "days": request.form.getlist('weekly_days')
                }
            elif schedule_type == "monthly":
                schedule_data = {
                    "time": request.form['monthly_time'],
                    "day": request.form['monthly_day']
                }
            elif schedule_type == "interval":
                schedule_data = {"minutes": request.form['interval_minutes']}
            else:  # custom
                schedule_data = {"custom": request.form['custom_cron']}
            
            # Convert to cron format
            cron_schedule = human_schedule_to_cron(schedule_type, schedule_data)
            
            # Add to cron tab
            cron = CronTab(user=True)
            command = f'python3 {APP_ROOT}/job_runner.py {gen}'
            if notify:
                command += ' --notify'
            job = cron.new(command=command)
            job.setall(cron_schedule)
            cron.write()

            # Save to jobs file
            jobs = load_jobs()
            jobs.append({
                'generator': gen, 
                'schedule': cron_schedule, 
                'schedule_type': schedule_type,
                'schedule_data': schedule_data,
                'notify': notify,
                'created_at': datetime.now().isoformat()
            })
            save_jobs(jobs)
            
            flash(f'Job "{gen}" scheduled successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error creating job: {str(e)}', 'error')
            return redirect(url_for('add_job'))

    gens = list_generators()
    return render_template('add_job.html', generators=gens)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    print(f"DEBUG: Attempting to delete job_id: {job_id}")
    try:
        jobs = load_jobs()
        print(f"DEBUG: Current jobs count: {len(jobs)}")
        
        if 0 <= job_id < len(jobs):
            job_name = jobs[job_id]["generator"]
            print(f"DEBUG: Deleting job: {job_name}")
            
            # Remove from cron tab
            try:
                cron = CronTab(user=True)
                command = f'python3 {APP_ROOT}/job_runner.py {jobs[job_id]["generator"]}'
                print(f"DEBUG: Looking for cron command: {command}")
                cron_jobs = list(cron.find_command(command))
                print(f"DEBUG: Found {len(cron_jobs)} cron jobs to remove")
                for job in cron_jobs:
                    cron.remove(job)
                cron.write()
                print("DEBUG: Cron jobs removed successfully")
            except Exception as cron_error:
                # Log the error but don't fail the deletion
                print(f"Warning: Could not remove from cron: {cron_error}")
            
            # Remove from jobs list
            jobs.pop(job_id)
            save_jobs(jobs)
            print(f"DEBUG: Job removed from jobs list. New count: {len(jobs)}")
            
            flash(f'Job "{job_name}" deleted successfully!', 'success')
        else:
            print(f"DEBUG: Job not found! job_id: {job_id}, jobs count: {len(jobs)}")
            flash('Job not found!', 'error')
    except Exception as e:
        print(f"DEBUG: Error deleting job: {str(e)}")
        flash(f'Error deleting job: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/jobs')
def api_jobs():
    """API endpoint to get jobs data"""
    jobs = load_jobs()
    for job in jobs:
        job['human_schedule'] = cron_to_human_readable(job['schedule'])
        job['status'] = get_job_status(job)
    return jsonify(jobs)

@app.route('/api/generators')
def api_generators():
    """API endpoint to get available generators"""
    return jsonify(list_generators())

@app.route('/api/status')
def api_status():
    """API endpoint to get system status"""
    jobs = load_jobs()
    return jsonify({
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if get_job_status(j) == 'Active']),
        'notifications_enabled': len([j for j in jobs if j.get('notify', False)]),
        'unique_generators': len(set(j['generator'] for j in jobs)),
        'system_status': 'Ready'
    })

@app.route('/test')
def test():
    """Test endpoint to verify the app is working"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask app is running',
        'jobs_count': len(load_jobs())
    })

@app.route('/test-delete/<int:job_id>', methods=['POST'])
def test_delete(job_id):
    """Simple test delete endpoint"""
    print(f"TEST DELETE: Received request to delete job {job_id}")
    return jsonify({
        'status': 'success',
        'message': f'Test delete for job {job_id}',
        'job_id': job_id
    })

@app.route('/test-form')
def test_form():
    """Test form page"""
    return render_template('test_form.html')

@app.route('/debug-form')
def debug_form():
    """Debug form page"""
    return render_template('debug_form.html')

@app.route('/debug-jobs')
def debug_jobs():
    """Debug endpoint to show current jobs"""
    jobs = load_jobs()
    return jsonify({
        'jobs_count': len(jobs),
        'jobs': jobs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
