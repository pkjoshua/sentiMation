from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import json
import logging
import subprocess
import random
from datetime import datetime, timedelta
import uuid
import threading
import time
from pathlib import Path

# Add the parent directory to the path to import generators
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our host scheduler client
from host_scheduler_client import HostSchedulerClient, JobSpec, create_generator_job_steps
import config

# DB
from db import get_connection, init_db, create_job, update_job_status, get_job_by_id, create_job_run, complete_job_run

import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentiMation-secret-key-2024'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize host scheduler client
host_scheduler = HostSchedulerClient(config.HOST_SERVICE_URL)

# Initialize DB
db_conn = get_connection()
init_db(db_conn)

# Health cache
health_state = {
    'host_service': False,
    'auto1111': False,
}

def health_monitor():
    while True:
        # Host service
        try:
            health_state['host_service'] = host_scheduler.is_available()
        except Exception:
            health_state['host_service'] = False
        # AUTO1111
        try:
            r = requests.get(f"{config.AUTO1111_BASE_URL}/sdapi/v1/options", timeout=5)
            health_state['auto1111'] = (r.status_code == 200)
        except Exception:
            health_state['auto1111'] = False
        time.sleep(config.HEALTHCHECK_INTERVAL_SEC)

threading.Thread(target=health_monitor, daemon=True).start()

# Global variables for scheduled tasks (kept for backwards compatibility / in-memory view)
scheduled_tasks = {}
task_counter = 0



class GenerationTask:
    def __init__(self, task_id, generator_type, prompt, scheduled_time, status="pending", is_recurring=False, recurring_days=None, recurring_time=None, character=None, environment=None, video_length=None, fps=None, width=None, height=None):
        self.task_id = task_id
        self.generator_type = generator_type
        self.prompt = prompt
        self.scheduled_time = scheduled_time
        self.status = status
        self.result_path = None
        self.error_message = None
        self.created_at = datetime.now()
        self.is_recurring = is_recurring
        self.recurring_days = recurring_days or []
        self.recurring_time = recurring_time
        # Custom generator specific fields
        self.character = character
        self.environment = environment
        # Generation parameters
        self.video_length = video_length
        self.fps = fps
        self.width = width
        self.height = height
        # Host service integration fields
        self.host_script_path = None
        self.host_log_path = None
        self.host_exit_code = None



def execute_scheduled_task(task_id):
    """Execute a scheduled generation task by calling the appropriate generator script"""
    global scheduled_tasks
    
    if task_id not in scheduled_tasks:
        logger.error(f"Task {task_id} not found")
        return
    
    task = scheduled_tasks[task_id]
    task.status = "running"
    logger.info(f"Starting task {task_id}: {task.generator_type} - {task.prompt}")
    
    try:
        # Determine the generator directory
        generator_dir = f"../generators/{task.generator_type}"
        
        if not os.path.exists(generator_dir):
            raise Exception(f"Generator directory not found: {generator_dir}")
        
        # Change to the generator directory
        original_cwd = os.getcwd()
        os.chdir(generator_dir)
        
        try:
            # Handle random activity selection
            if task.prompt == "RANDOM_ACTIVITY":
                logger.info(f"Using random activity for {task.generator_type}")
                # For random activity, we'll let the selector.py handle everything
                pass
            else:
                # For specific activities, we need to create a custom prompt file
                # This would require modifying the workflow to accept specific prompts
                logger.info(f"Specific activity selected: {task.prompt}")
                # For now, we'll use the random workflow and log the selected prompt
                pass
            
            # Run the generator call script
            logger.info(f"Running call.py in {generator_dir}")
            
            # For custom generator, pass specific parameters and env overrides
            if task.generator_type == "custom" and hasattr(task, 'character') and hasattr(task, 'environment'):
                env = os.environ.copy()
                # Apply overrides if present on the task
                if getattr(task, 'video_length', None):
                    env['GEN_VIDEO_LENGTH'] = str(task.video_length)
                if getattr(task, 'fps', None):
                    env['GEN_FPS'] = str(task.fps)
                if getattr(task, 'width', None):
                    env['GEN_WIDTH'] = str(task.width)
                if getattr(task, 'height', None):
                    env['GEN_HEIGHT'] = str(task.height)
                env['AUTO1111_API'] = f"{config.AUTO1111_BASE_URL}/sdapi/v1/img2img"

                if task.character and task.environment and task.prompt and task.prompt != "RANDOM_ACTIVITY":
                    logger.info(f"Running custom generator with: character={task.character}, environment={task.environment}, prompt={task.prompt}")
                    result = subprocess.run(
                        ['python', 'call.py', task.character, task.environment, task.prompt],
                        capture_output=True,
                        text=True,
                        timeout=3600,  # 1 hour timeout
                        env=env
                    )
                else:
                    logger.info("Running custom generator with random selection")
                    result = subprocess.run(
                        ['python', 'call.py'],
                        capture_output=True,
                        text=True,
                        timeout=3600,  # 1 hour timeout
                        env=env
                    )
            else:
                # Regular generator types (music, scenario)
                result = subprocess.run(
                    ['python', 'call.py'],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
            
            if result.returncode == 0:
                task.status = "completed"
                # Look for the generated video file
                output_dir = "assets/upscale_generations"
                if os.path.exists(output_dir):
                    video_files = [f for f in os.listdir(output_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
                    if video_files:
                        # Sort by modification time to get the most recent
                        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                        task.result_path = os.path.join(output_dir, video_files[0])
                        logger.info(f"Task {task_id} completed successfully: {task.result_path}")
                    else:
                        task.status = "failed"
                        task.error_message = "No video file generated"
                        logger.error(f"Task {task_id} failed: No video file found in {output_dir}")
                else:
                    task.status = "failed"
                    task.error_message = "Output directory not found"
                    logger.error(f"Task {task_id} failed: Output directory {output_dir} not found")
            else:
                task.status = "failed"
                task.error_message = f"Generator script failed: {result.stderr}"
                logger.error(f"Task {task_id} failed: {result.stderr}")
                
        finally:
            # Always restore the original working directory
            os.chdir(original_cwd)
            
    except subprocess.TimeoutExpired:
        task.status = "failed"
        task.error_message = "Task timed out after 1 hour"
        logger.error(f"Task {task_id} timed out")
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        logger.error(f"Task {task_id} failed with error: {e}")
    
    # Update task in global dict
    scheduled_tasks[task_id] = task

def schedule_task_execution(task_id, scheduled_time, is_recurring=False, recurring_days=None, recurring_time=None):
    """Schedule a task to execute at the specified time"""
    def run_task():
        if is_recurring and recurring_days and recurring_time:
            # For recurring tasks, run continuously
            while True:
                now = datetime.now()
                current_day = now.strftime('%A').lower()
                current_time = now.strftime('%H:%M')
                
                # Check if it's time to run
                if current_day in recurring_days and current_time == recurring_time:
                    execute_scheduled_task(task_id)
                    # Wait until next day to avoid multiple executions
                    time.sleep(60)  # Wait 1 minute
                else:
                    # Wait 30 seconds before checking again
                    time.sleep(30)
        else:
            # For one-time tasks, wait until scheduled time
            now = datetime.now()
            if scheduled_time > now:
                wait_seconds = (scheduled_time - now).total_seconds()
                time.sleep(wait_seconds)
            
            execute_scheduled_task(task_id)
    
    thread = threading.Thread(target=run_task)
    thread.daemon = True
    thread.start()

def run_custom_generation(job_row, run_id):
    """Execute the custom generation using existing generator path."""
    try:
        generator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generators', 'custom'))
        if not os.path.exists(generator_dir):
            raise Exception(f"Generator directory not found: {generator_dir}")

        original_cwd = os.getcwd()
        os.chdir(generator_dir)

        try:
            env = os.environ.copy()
            env['AUTO1111_API'] = f"{config.AUTO1111_BASE_URL}/sdapi/v1/img2img"
            if job_row['video_length']:
                env['GEN_VIDEO_LENGTH'] = str(job_row['video_length'])
            if job_row['fps']:
                env['GEN_FPS'] = str(job_row['fps'])
            if job_row['width']:
                env['GEN_WIDTH'] = str(job_row['width'])
            if job_row['height']:
                env['GEN_HEIGHT'] = str(job_row['height'])

            args = ['python', 'call.py']
            if job_row['character'] and job_row['environment'] and job_row['prompt'] and job_row['prompt'] != 'RANDOM_ACTIVITY':
                args = ['python', 'call.py', job_row['character'], job_row['environment'], job_row['prompt']]

            result = subprocess.run(args, capture_output=True, text=True, timeout=7200, env=env)
            if result.returncode != 0:
                raise Exception(f"Generator failed: {result.stderr}")

            # Find latest video in upscale_generations
            output_dir = os.path.join(generator_dir, 'assets', 'upscale_generations')
            output_path = None
            if os.path.exists(output_dir):
                video_files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
                if video_files:
                    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                    output_path = os.path.join(output_dir, video_files[0])

            # Copy/symlink output to webapp static (for simplicity, copy)
            final_output = None
            if output_path and os.path.exists(output_path):
                os.makedirs('webapp/static/generated', exist_ok=True)
                basename = f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(output_path)[1]}"
                final_output = os.path.join('webapp/static/generated', basename)
                try:
                    from shutil import copy2
                    copy2(output_path, final_output)
                except Exception as ce:
                    logger.warning(f"Copy output failed, using original path: {ce}")
                    final_output = output_path

            complete_job_run(db_conn, run_id=run_id, status='completed', output_path=final_output)
            return final_output
        finally:
            os.chdir(original_cwd)
    except Exception as e:
        logger.exception("run_custom_generation failed")
        complete_job_run(db_conn, run_id=run_id, status='failed', error_message=str(e))
        raise


def handle_host_run(job_id: int):
    job = get_job_by_id(db_conn, job_id)
    if not job:
        logger.error(f"host run: job {job_id} not found")
        return
    update_job_status(db_conn, job_id=job_id, status='running')
    run_id = create_job_run(db_conn, job_id=job_id, status='running')

    def _runner():
        try:
            if job['type'] == 'custom':
                run_custom_generation(job, run_id)
            else:
                complete_job_run(db_conn, run_id=run_id, status='failed', error_message=f"Unsupported type {job['type']}")
                update_job_status(db_conn, job_id=job_id, status='failed', last_error='unsupported type')
                return
            update_job_status(db_conn, job_id=job_id, status='completed')
        except Exception as e:
            update_job_status(db_conn, job_id=job_id, status='failed', last_error=str(e))

    t = threading.Thread(target=_runner, daemon=True)
    t.start()


@app.route('/api/host/run-job', methods=['POST'])
def api_host_run_job():
    """Endpoint the host service calls to trigger a job run."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'error': 'missing bearer token'}), 401
    token = auth.split(' ', 1)[1]
    if token != config.HOST_CALLBACK_TOKEN:
        return jsonify({'error': 'invalid token'}), 403

    try:
        payload = request.get_json(force=True) or {}
        # Allow either jobId or taskName
        job_id = payload.get('jobId')
        task_name = payload.get('taskName')
        if not job_id and not task_name:
            return jsonify({'error': 'jobId or taskName required'}), 400
        if not job_id and task_name:
            # We didn't add get_job_by_task_name import above, keep minimal: not used in MVP
            return jsonify({'error': 'lookup by taskName not implemented in MVP'}), 400
        handle_host_run(int(job_id))
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.exception("/api/host/run-job failed")
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    """Main page with title SentiMation"""
    return render_template('index.html', tasks=scheduled_tasks)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule_generation():
    """Schedule a new generation task"""
    global task_counter, scheduled_tasks
    
    if request.method == 'POST':
        try:
            generator_type = request.form.get('generator_type')
            prompt = request.form.get('prompt')
            scheduled_time_str = request.form.get('scheduled_time')
            is_recurring = request.form.get('is_recurring') == 'on'
            recurring_days = request.form.getlist('recurring_days')
            recurring_time_str = request.form.get('recurring_time')
            
            if not all([generator_type, prompt]):
                return jsonify({'error': 'Generator type and prompt are required'}), 400
            
            if is_recurring:
                if not recurring_days or not recurring_time_str:
                    return jsonify({'error': 'Recurring days and time are required for recurring tasks'}), 400
                scheduled_time = datetime.now()  # For recurring tasks, use current time as creation time
                schedule_time = recurring_time_str
            else:
                if not scheduled_time_str:
                    return jsonify({'error': 'Scheduled time is required for one-time tasks'}), 400
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('T', ' '))
                schedule_time = scheduled_time.strftime('%H:%M')
            
            # Create new task with globally unique name
            task_id = f"job_{uuid.uuid4().hex[:8]}"
            
            # Get custom generator parameters if applicable
            character = None
            environment = None
            if generator_type == "custom":
                character = request.form.get('character')
                environment = request.form.get('environment')
            
            # Parse optional generation parameters
            try:
                video_length_val = int(request.form.get('video_length') or 150)
                fps_val = int(request.form.get('fps') or 20)
                width_val = int(request.form.get('width') or 360)
                height_val = int(request.form.get('height') or 640)
            except Exception:
                video_length_val, fps_val, width_val, height_val = 150, 20, 360, 640

            task = GenerationTask(
                task_id=task_id,
                generator_type=generator_type,
                prompt=prompt,
                scheduled_time=scheduled_time,
                is_recurring=is_recurring,
                recurring_days=recurring_days,
                recurring_time=recurring_time_str,
                character=character,
                environment=environment,
                video_length=video_length_val,
                fps=fps_val,
                width=width_val,
                height=height_val
            )
            
            scheduled_tasks[task_id] = task
            
            # Persist job in DB
            schedule_kind = 'recurring' if is_recurring else 'one_time'
            schedule_dt_iso = None if is_recurring else scheduled_time.isoformat()
            recurring_days_csv = ','.join(recurring_days) if is_recurring else None
            job_db_id = create_job(
                db_conn,
                task_name=task_id,
                type=generator_type,
                prompt=prompt,
                character=character,
                environment=environment,
                video_length=video_length_val,
                fps=fps_val,
                width=width_val,
                height=height_val,
                schedule_kind=schedule_kind,
                schedule_dt=schedule_dt_iso,
                recurring_days=recurring_days_csv,
                recurring_time=recurring_time_str,
                status='pending'
            )
            
            # Create job steps for the host service
            try:
                job_steps = create_generator_job_steps(
                    generator_type=generator_type,
                    prompt=prompt,
                    character=character,
                    environment=environment,
                    webapp_public_url=config.WEBAPP_PUBLIC_URL,
                    host_callback_token=config.HOST_CALLBACK_TOKEN,
                    job_id=job_db_id,
                    task_name=task_id
                )
                
                # Create job specification
                days_pascal = None
                if is_recurring and recurring_days:
                    # Convert lowercase day names to PascalCase to match .NET DayOfWeek parsing on host
                    day_map = {
                        'monday':'Monday','tuesday':'Tuesday','wednesday':'Wednesday','thursday':'Thursday','friday':'Friday','saturday':'Saturday','sunday':'Sunday'
                    }
                    days_pascal = [day_map.get(d, d) for d in recurring_days]
                job_spec = JobSpec(
                    task_name=task_id,
                    steps=job_steps,
                    time=schedule_time,
                    days=days_pascal
                )
                
                # Schedule job with host service
                if host_scheduler.is_available():
                    host_result = host_scheduler.schedule_job(job_spec)
                    task.host_script_path = host_result.get('script')
                    update_job_status(db_conn, job_id=job_db_id, status='scheduled', host_script_path=task.host_script_path)
                    logger.info(f"Job scheduled with host service: {host_result}")
                else:
                    logger.warning("Host service not available; job saved but not scheduled")
                    update_job_status(db_conn, job_id=job_db_id, status='pending')
                
            except Exception as e:
                logger.error(f"Failed to schedule job with host service: {e}")
                update_job_status(db_conn, job_id=job_db_id, status='failed', last_error=str(e))
            
            if is_recurring:
                logger.info(f"Scheduled recurring task {task_id} for {', '.join(recurring_days)} at {recurring_time_str}")
            else:
                logger.info(f"Scheduled task {task_id} for {scheduled_time}")
            
            # Check if this is an AJAX request (for Run Now functionality)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'task_id': task_id, 'message': 'Task created successfully'})
            else:
                return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return jsonify({'error': str(e)}), 500
    
    return render_template('schedule.html')

@app.route('/tasks')
def get_tasks():
    """Get all scheduled tasks"""
    tasks_data = []
    for task_id, task in scheduled_tasks.items():
        task_data = {
            'id': task_id,
            'generator_type': task.generator_type,
            'prompt': task.prompt,
            'scheduled_time': task.scheduled_time.isoformat(),
            'status': task.status,
            'result_path': task.result_path,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),
            'is_recurring': task.is_recurring,
            'recurring_days': task.recurring_days,
            'recurring_time': task.recurring_time
        }
        
        # Add custom generator fields if they exist
        if hasattr(task, 'character') and task.character:
            task_data['character'] = task.character
        if hasattr(task, 'environment') and task.environment:
            task_data['environment'] = task.environment
            
        tasks_data.append(task_data)
    
    return jsonify(tasks_data)

@app.route('/task/<task_id>')
def get_task(task_id):
    """Get specific task details"""
    if task_id not in scheduled_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = scheduled_tasks[task_id]
    task_data = {
        'id': task_id,
        'generator_type': task.generator_type,
        'prompt': task.prompt,
        'scheduled_time': task.scheduled_time.isoformat(),
        'status': task.status,
        'result_path': task.result_path,
        'error_message': task.error_message,
        'created_at': task.created_at.isoformat(),
        'is_recurring': task.is_recurring,
        'recurring_days': task.recurring_days,
        'recurring_time': task.recurring_time
    }
    
    # Add custom generator fields if they exist
    if hasattr(task, 'character') and task.character:
        task_data['character'] = task.character
    if hasattr(task, 'environment') and task.environment:
        task_data['environment'] = task.environment
    
    # Add host service fields if they exist
    if hasattr(task, 'host_script_path') and task.host_script_path:
        task_data['host_script_path'] = task.host_script_path
    if hasattr(task, 'host_log_path') and task.host_log_path:
        task_data['host_log_path'] = task.host_log_path
    if hasattr(task, 'host_exit_code') and task.host_exit_code is not None:
        task_data['host_exit_code'] = task.host_exit_code
        
    return jsonify(task_data)

@app.route('/cancel/<task_id>')
def cancel_task(task_id):
    """Cancel a scheduled task"""
    global scheduled_tasks
    
    if task_id not in scheduled_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = scheduled_tasks[task_id]
    if task.status in ["pending", "scheduled"]:
        task.status = "cancelled"
        # Also request deletion from host scheduler
        try:
            if host_scheduler.is_available():
                host_scheduler.delete_task(task_id)
                logger.info(f"Task {task_id} deleted from host scheduler")
        except Exception as e:
            logger.warning(f"Failed to delete task {task_id} from host scheduler: {e}")
        logger.info(f"Task {task_id} cancelled")
        return jsonify({'message': 'Task cancelled successfully'})
    else:
        return jsonify({'error': 'Cannot cancel task that is already running or completed'}), 400

@app.route('/run_now/<task_id>')
def run_task_now(task_id):
    """Run a scheduled task immediately"""
    global scheduled_tasks
    
    if task_id not in scheduled_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = scheduled_tasks[task_id]
    if task.status == "pending":
        try:
            # Create job steps for the host service
            job_steps = create_generator_job_steps(
                generator_type=task.generator_type,
                prompt=task.prompt,
                character=task.character,
                environment=task.environment
            )
            
            # Create job specification (no time needed for immediate execution)
            job_spec = JobSpec(
                task_name=task_id,
                steps=job_steps
            )
            
            # Run job immediately with host service
            if host_scheduler.is_available():
                host_result = host_scheduler.run_job_now(job_spec)
                task.host_log_path = host_result.get('log')
                task.host_exit_code = host_result.get('exitCode')
                task.status = "running"
                task.started_at = datetime.now()
                
                logger.info(f"Task {task_id} started immediately with host service: {host_result}")
                return jsonify({'message': 'Task started successfully with host service', 'log_path': task.host_log_path})
            else:
                logger.warning("Host service not available, falling back to local execution")
                # Fall back to local execution
                task.status = "running"
                task.started_at = datetime.now()
                
                # Start execution in a separate thread
                execution_thread = threading.Thread(
                    target=execute_scheduled_task,
                    args=(task_id,),
                    daemon=True
                )
                execution_thread.start()
                
                logger.info(f"Task {task_id} started immediately with local execution")
                return jsonify({'message': 'Task started successfully with local execution'})
                
        except Exception as e:
            logger.error(f"Failed to run task {task_id} with host service: {e}")
            # Fall back to local execution
            task.status = "running"
            task.started_at = datetime.now()
            
            # Start execution in a separate thread
            execution_thread = threading.Thread(
                target=execute_scheduled_task,
            args=(task_id,),
                daemon=True
            )
            execution_thread.start()
            
            logger.info(f"Task {task_id} started immediately with local execution (fallback)")
            return jsonify({'message': 'Task started successfully with local execution (fallback)'})
    else:
        return jsonify({'error': 'Can only run pending tasks'}), 400

@app.route('/generators')
def get_generators():
    """Get available generators by detecting valid generator folders"""
    generators: list[str] = []
    generators_dir = Path("../generators")

    def is_valid_generator_dir(dir_path: Path) -> bool:
        # Must be a directory, not named __pycache__ or old, and contain a call.py
        if not dir_path.is_dir():
            return False
        if dir_path.name.lower() in ['__pycache__', 'old']:
            return False
        # Ignore any dir residing under an 'old' container path
        if 'old' in [p.name.lower() for p in dir_path.parents]:
            return False
        return (dir_path / 'call.py').exists()

    if generators_dir.exists():
        for generator_dir in generators_dir.iterdir():
            if is_valid_generator_dir(generator_dir):
                generators.append(generator_dir.name)

    # Sort for stability
    generators.sort()
    return jsonify(generators)

@app.route('/characters/<generator_type>')
def get_characters(generator_type):
    """Get available characters for a specific generator"""
    characters = []
    characters_file = Path(f"../generators/{generator_type}/assets/devices/characters.txt")
    
    if characters_file.exists():
        try:
            with open(characters_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            characters.append({
                                'name': parts[0].strip(),
                                'lora': parts[1].strip(),
                                'activator': parts[2].strip(),
                                'quote_directory': parts[3].strip()
                            })
        except Exception as e:
            logger.error(f"Error reading characters file: {e}")
    
    return jsonify(characters)

@app.route('/environments/<generator_type>')
def get_environments(generator_type):
    """Get available environments for a specific generator"""
    environments = []
    environments_file = Path(f"../generators/{generator_type}/assets/devices/environments.txt")
    
    if environments_file.exists():
        try:
            with open(environments_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 1:
                            environments.append({
                                'name': parts[0].strip(),
                                'lora': parts[1].strip() if len(parts) > 1 else ''
                            })
        except Exception as e:
            logger.error(f"Error reading environments file: {e}")
    
    return jsonify(environments)

@app.route('/prompts/<generator_type>')
def get_prompts(generator_type):
    """Get available prompts for a specific generator"""
    prompts = []
    prompts_dir = Path(f"../generators/{generator_type}/assets/prompts")
    
    # Add random activity option
    prompts.append({
        'name': 'Random Activity',
        'filename': 'random',
        'content': 'RANDOM_ACTIVITY',
        'is_random': True
    })
    
    if prompts_dir.exists():
        for prompt_file in prompts_dir.glob("*.txt"):
            # Read the prompt content
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read().strip()
                
                # Extract activity name from filename (remove .txt extension)
                activity_name = prompt_file.stem.replace('_', ' ').title()
                
                prompts.append({
                    'name': activity_name,
                    'filename': prompt_file.name,
                    'content': prompt_content,
                    'is_random': False
                })
            except Exception as e:
                logger.error(f"Error reading prompt file {prompt_file}: {e}")
    
    return jsonify(prompts)

@app.route('/host-service/status')
def host_service_status():
    """Check the status of the host service"""
    try:
        is_available = host_scheduler.is_available()
        return jsonify({
            'status': 'ok',
            'host_service_available': is_available,
            'host_service_url': config.HOST_SERVICE_URL
        })
    except Exception as e:
        logger.error(f"Error checking host service status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'host_service_url': config.HOST_SERVICE_URL
        }), 500

@app.route('/healthz')
def healthz():
    return jsonify({
        'host_service': health_state['host_service'],
        'auto1111': health_state['auto1111']
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('webapp/static/generated', exist_ok=True)
    
    logger.info("Starting SentiMation web application")
    app.run(host='0.0.0.0', port=5000, debug=True) 