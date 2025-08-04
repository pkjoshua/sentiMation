from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import json
import logging
import requests
import base64
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

# Import configuration
from config import SD_API_URL

class GenerationTask:
    def __init__(self, task_id, generator_type, prompt, scheduled_time, status="pending", is_recurring=False, recurring_days=None, recurring_time=None):
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

def encode_image_to_base64(image_path):
    """Encode image to base64 for API calls"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

def call_stable_diffusion_api(prompt, controlnet_image_path=None):
    """Make API call to Stable Diffusion"""
    try:
        # Encode controlnet image if provided
        encoded_image = None
        if controlnet_image_path and os.path.exists(controlnet_image_path):
            encoded_image = encode_image_to_base64(controlnet_image_path)
        
        if not encoded_image:
            # Use a default image or create one
            logger.warning("No controlnet image provided, using default")
            return None

        animate_diff_args = {
            "model": "animatediffMotion_v15V2.ckpt",
            "format": ['MP4'],
            "enable": True,
            "video_length": 150,
            "fps": 20,
            "loop_number": 0,
            "closed_loop": "N",
            "batch_size": 16,
            "stride": 1,
            "overlap": -1,
            "interp": "NO",
            "interp_x": 10,
            "latent_power": 0.5,
            "latent_scale": 32,
            "last_frame": encoded_image,
            "latent_power_last": 0.5,
            "latent_scale_last": 32
        }

        json_payload = {
            "init_images": [encoded_image],
            "denoising_strength": 0.9,
            "prompt": prompt,
            "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
            "batch_size": 1,
            "sampler_name": "DPM++ 2M Karras",
            "steps": 20,
            "cfg_scale": 10,
            "width": 360,
            "height": 640,
            "alwayson_scripts": {
                "AnimateDiff": {"args": [animate_diff_args]}
            }
        }

        logger.info(f"Making API call with prompt: {prompt}")
        response = requests.post(SD_API_URL, headers={"Content-Type": "application/json"}, json=json_payload)

        if response.status_code == 200:
            r = response.json()
            if 'images' in r and r['images']:
                base64_data = r['images'][0]
                mp4_data = base64.b64decode(base64_data)
                
                # Save the generated video
                output_dir = Path("webapp/static/generated")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"generation_{timestamp}.mp4"
                
                with open(output_path, 'wb') as file:
                    file.write(mp4_data)
                
                logger.info(f"MP4 file saved as {output_path}")
                return str(output_path)
            else:
                logger.error("No image data found in the response")
                return None
        else:
            logger.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error in API call: {e}")
        return None

def execute_scheduled_task(task_id):
    """Execute a scheduled generation task"""
    global scheduled_tasks
    
    if task_id not in scheduled_tasks:
        logger.error(f"Task {task_id} not found")
        return
    
    task = scheduled_tasks[task_id]
    task.status = "running"
    
    try:
        logger.info(f"Executing task {task_id}: {task.generator_type} - {task.prompt}")
        
        # Handle random activity selection
        if task.prompt == "RANDOM_ACTIVITY":
            # Select a random prompt from the generator's prompt directory
            prompts_dir = Path(f"../generators/{task.generator_type}/assets/prompts")
            if prompts_dir.exists():
                prompt_files = list(prompts_dir.glob("*.txt"))
                if prompt_files:
                    selected_prompt_file = random.choice(prompt_files)
                    with open(selected_prompt_file, 'r', encoding='utf-8') as f:
                        task.prompt = f.read().strip()
                    logger.info(f"Selected random prompt: {selected_prompt_file.name}")
                else:
                    task.status = "failed"
                    task.error_message = "No prompt files found for random selection"
                    logger.error(f"Task {task_id} failed: No prompt files found")
                    return
            else:
                task.status = "failed"
                task.error_message = f"Prompt directory not found: {prompts_dir}"
                logger.error(f"Task {task_id} failed: Prompt directory not found")
                return
        
        # Get a controlnet image from the appropriate generator
        controlnet_dir = f"../generators/{task.generator_type}/assets/init"
        if os.path.exists(controlnet_dir):
            controlnet_images = sorted(os.listdir(controlnet_dir))
            if controlnet_images:
                controlnet_image_path = os.path.join(controlnet_dir, controlnet_images[0])
                result_path = call_stable_diffusion_api(task.prompt, controlnet_image_path)
                
                if result_path:
                    task.result_path = result_path
                    task.status = "completed"
                    logger.info(f"Task {task_id} completed successfully")
                else:
                    task.status = "failed"
                    task.error_message = "API call failed"
                    logger.error(f"Task {task_id} failed")
            else:
                task.status = "failed"
                task.error_message = "No controlnet images found"
                logger.error(f"Task {task_id} failed: No controlnet images")
        else:
            task.status = "failed"
            task.error_message = f"Controlnet directory not found: {controlnet_dir}"
            logger.error(f"Task {task_id} failed: Controlnet directory not found")
            
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        logger.error(f"Task {task_id} failed with exception: {e}")

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
            
            task = GenerationTask(
                task_id=task_id,
                generator_type=generator_type,
                prompt=prompt,
                scheduled_time=scheduled_time,
                is_recurring=is_recurring,
                recurring_days=recurring_days,
                recurring_time=recurring_time_str
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
        tasks_data.append({
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
        })
    
    return jsonify(tasks_data)

@app.route('/task/<task_id>')
def get_task(task_id):
    """Get specific task details"""
    if task_id not in scheduled_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = scheduled_tasks[task_id]
    return jsonify({
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
    })

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