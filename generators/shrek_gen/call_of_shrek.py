import subprocess
import logging
import time

# Set up logging
logging.basicConfig(filename='shrek_gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

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
    run_script('shrek_CN_image_gen.py')
    run_script('shrek_generator.py')
    run_script('shrek_upscale.py')
    run_script('shrek_mash.py')

# Run the sequence four times
for i in range(4):
    logging.info(f"Running iteration {i + 1}")
    run_scripts_sequence()
