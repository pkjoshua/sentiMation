import subprocess
import logging
import time
import os
import shutil

# Set up main logging
logging.basicConfig(filename='pokemon_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Set up generation time logging
gentime_logger = logging.getLogger('gentime_logger')
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)
gentime_logger.setLevel(logging.INFO)

# Function to clear the contents of a directory
def clear_directory(directory):
    for item in os.listdir(directory):
        file_path = os.path.join(directory, item)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')

# Function to run a script and log its output
def run_script(script_name):
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"{script_name} finished successfully.")
        logging.info("Output: %s", result.stdout)
    else:
        logging.error(f"{script_name} failed.")
        logging.error("Error: %s", result.stderr)
    time.sleep(10)  # 10-second pause between each script

# Function to run all scripts and track total execution time
def run_all_scripts():
    start_time = time.time()
    run_script('pokemon_prompt.py')  # Create prompt
    run_script('pokemon_generator.py')  # Generate Animation and mask
    run_script('pokemon_upscale.py')  # Upscale frames and create mp4
    run_script('pokemon_background_overlay.py')  # Overlay background
    run_script('pokemon_mash.py')  # Append audio
    total_time = time.time() - start_time
    gentime_logger.info(f"Total time for all scripts: {total_time:.2f} seconds")

# Clear contents of specific directories before running scripts
directories_to_clear = ['lowscale', 'upscale', 'upscale_process','upscale_overlay']
for directory in directories_to_clear:
    clear_directory(directory)

# Run the sequence of scripts
run_all_scripts()

print("Script sequence complete.")
