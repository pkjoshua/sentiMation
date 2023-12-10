import subprocess
import logging
import time

# Set up main logging
logging.basicConfig(filename='skl_gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Set up generation time logging
gentime_logger = logging.getLogger('gentime_logger')
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)
gentime_logger.setLevel(logging.INFO)

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

# Run the sequence of scripts five times
for i in range(5):
    start_time = time.time()
    logging.info(f"Starting sequence {i + 1}")

    run_script('skl_CN_image_gen.py')
    run_script('skl_generator.py')
    run_script('skl_upscale.py')
    run_script('skl_mash.py')

    end_time = time.time()
    total_time = end_time - start_time
    gentime_logger.info(f"Sequence {i + 1} completed in {total_time:.2f} seconds")

logging.info("All sequences complete.")
