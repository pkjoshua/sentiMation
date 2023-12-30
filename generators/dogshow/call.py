import subprocess
import logging
import time
import os

# Set up logging
logging.basicConfig(filename='gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Additional logger for gentime.log
gentime_logger = logging.getLogger('gentime_logger')
gentime_logger.setLevel(logging.INFO)
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)

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
    time.sleep(5)  # 5-second pause between each script

# Run scripts in sequence
def run_scripts_sequence():
    start_time = time.time()  # Start timing
    run_script('media_select.py')
    run_script('generator.py')
    run_script('upscale.py')
    run_script('mash.py')
    run_script('notify.py')
    end_time = time.time()  # End timing
    total_time = end_time - start_time
    gentime_logger.info(f"Total time for sequence: {total_time:.2f} seconds")

# Clear contents of specific directories before running scripts
directories_to_clear = ['assets\\lowscale', 'assets\\frames', 'assets\\upscale']
for directory in directories_to_clear:
    clear_directory(directory)

run_scripts_sequence()

print("Script sequence complete.")

