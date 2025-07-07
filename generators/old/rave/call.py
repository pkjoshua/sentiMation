import subprocess
import logging
import time
import os
import shutil

# Determine the directory of the current script to make paths relative to it
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set up logging with paths relative to the script directory
logging.basicConfig(filename=os.path.join(script_dir, 'gen.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Additional logger for gentime.log with path relative to the script directory
gentime_logger = logging.getLogger('gentime_logger')
gentime_logger.setLevel(logging.INFO)
gentime_handler = logging.FileHandler(os.path.join(script_dir, 'gentime.log'))
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)

# Function to clear the contents of a directory
def clear_directory(directory):
    full_dir = os.path.join(script_dir, directory)  # Adjust directory path
    for item in os.listdir(full_dir):
        file_path = os.path.join(full_dir, item)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')

# Function to run a script and log its output
def run_script(script_name):
    script_path = os.path.join(script_dir, script_name)  # Adjust script path
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"{script_name} finished successfully.")
        logging.info("Output: %s", result.stdout)
    else:
        logging.error(f"{script_name} failed.")
        logging.error("Error: %s", result.stderr)
    time.sleep(5)  # 5-second pause between each script

# Run scripts in sequence
def run_scripts_sequence():
    start_time = time.time()  # Start timing
    run_script('media_select.py')
    run_script('generator.py')
    run_script('upscale.py')
    run_script('mash.py')
    end_time = time.time()  # End timing
    total_time = end_time - start_time
    gentime_logger.info(f"Total time for sequence: {total_time:.2f} seconds")

# Clear contents of specific directories before running scripts
directories_to_clear = ['assets/lowscale', 'assets/upscale','assets/generations','assets/audio']
for directory in directories_to_clear:
    clear_directory(directory)

run_scripts_sequence()

print("Script sequence complete.")
