import subprocess
import logging
import time

# Set up logging
logging.basicConfig(filename='gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Additional logger for gentime.log
gentime_logger = logging.getLogger('gentime_logger')
gentime_logger.setLevel(logging.INFO)
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)

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
    run_script('CN_image_gen.py')
    run_script('generator.py')
    run_script('upscale.py')
    run_script('mash.py')
    end_time = time.time()  # End timing
    total_time = end_time - start_time
    gentime_logger.info(f"Total time for sequence: {total_time:.2f} seconds")

# Run the sequence four times
for i in range(4):
    logging.info(f"Running iteration {i + 1}")
    run_scripts_sequence()
