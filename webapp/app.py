from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import json
import logging
import subprocess
import random
from datetime import datetime, timedelta
import threading
import time
from pathlib import Path

# Add the parent directory to the path to import generators
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Global variables for scheduled tasks
scheduled_tasks = {}
task_counter = 0



class GenerationTask:
    def __init__(self, task_id, generator_type, prompt, scheduled_time, status="pending", is_recurring=False, recurring_days=None, recurring_time=None, character=None, environment=None):
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
            
            # For custom generator, pass specific parameters
            if task.generator_type == "custom" and hasattr(task, 'character') and hasattr(task, 'environment'):
                if task.character and task.environment and task.prompt and task.prompt != "RANDOM_ACTIVITY":
                    logger.info(f"Running custom generator with: character={task.character}, environment={task.environment}, prompt={task.prompt}")
                    result = subprocess.run(
                        ['python', 'call.py', task.character, task.environment, task.prompt],
                        capture_output=True,
                        text=True,
                        timeout=3600  # 1 hour timeout
                    )
                else:
                    logger.info("Running custom generator with random selection")
                    result = subprocess.run(
                        ['python', 'call.py'],
                        capture_output=True,
                        text=True,
                        timeout=3600  # 1 hour timeout
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
            else:
                if not scheduled_time_str:
                    return jsonify({'error': 'Scheduled time is required for one-time tasks'}), 400
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('T', ' '))
            
            # Create new task
            task_counter += 1
            task_id = f"task_{task_counter}"
            
            # Get custom generator parameters if applicable
            character = None
            environment = None
            if generator_type == "custom":
                character = request.form.get('character')
                environment = request.form.get('environment')
            
            task = GenerationTask(
                task_id=task_id,
                generator_type=generator_type,
                prompt=prompt,
                scheduled_time=scheduled_time,
                is_recurring=is_recurring,
                recurring_days=recurring_days,
                recurring_time=recurring_time_str,
                character=character,
                environment=environment
            )
            
            scheduled_tasks[task_id] = task
            
            # Schedule the task
            schedule_task_execution(task_id, scheduled_time, is_recurring, recurring_days, recurring_time_str)
            
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
        
    return jsonify(task_data)

@app.route('/cancel/<task_id>')
def cancel_task(task_id):
    """Cancel a scheduled task"""
    global scheduled_tasks
    
    if task_id not in scheduled_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = scheduled_tasks[task_id]
    if task.status == "pending":
        task.status = "cancelled"
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
        # Execute the task immediately
        task.status = "running"
        task.started_at = datetime.now()
        
        # Start execution in a separate thread
        execution_thread = threading.Thread(
            target=execute_scheduled_task,
            args=(task_id,),
            daemon=True
        )
        execution_thread.start()
        
        logger.info(f"Task {task_id} started immediately")
        return jsonify({'message': 'Task started successfully'})
    else:
        return jsonify({'error': 'Can only run pending tasks'}), 400

@app.route('/generators')
def get_generators():
    """Get available generators"""
    generators = []
    generators_dir = Path("../generators")
    
    if generators_dir.exists():
        for generator_dir in generators_dir.iterdir():
            if generator_dir.is_dir() and generator_dir.name not in ['__pycache__', 'old']:
                generators.append(generator_dir.name)
    
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

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('webapp/static/generated', exist_ok=True)
    
    logger.info("Starting SentiMation web application")
    app.run(host='0.0.0.0', port=5000, debug=True) 