import subprocess
import logging

# Set up logging
logging.basicConfig(filename='minds_eye_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Call the minds_eye_prompt.py script
result = subprocess.run(['python', 'minds_eye_prompt.py'], capture_output=True, text=True)

# Check if minds_eye_prompt.py was successful
if result.returncode == 0:
    logging.info("minds_eye_prompt.py finished successfully.")
    logging.info("Output: %s", result.stdout)

    # Call the minds_eye_generator.py script
    result2 = subprocess.run(['python', 'minds_eye_generator.py'], capture_output=True, text=True)
    if result2.returncode == 0:
        logging.info("minds_eye_generator.py finished successfully.")
        logging.info("Output: %s", result2.stdout)
    else:
        logging.error("minds_eye_generator.py failed.")
        logging.error("Error: %s", result2.stderr)
else:
    logging.error("minds_eye_prompt.py failed.")
    logging.error("Error: %s", result.stderr)
