import subprocess
import logging
import time

# Set up logging
logging.basicConfig(filename='skl_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

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

# Run scripts in sequence
run_script('skl_prompt.py')
run_script('pokemon_generator.py')
run_script('pokemon_background_overlay.py')  # New step added
run_script('pokemon_upscale.py')
run_script('pokemon_mash.py')

print("Script sequence complete.")
