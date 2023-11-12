import subprocess
import logging

# Set up logging
logging.basicConfig(filename='hypnotic_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Call the hypnotic_prompt.py script
result = subprocess.run(['python', 'hypnotic_prompt.py'], capture_output=True, text=True)

# Check if hypnotic_prompt.py was successful
if result.returncode == 0:
    logging.info("hypnotic_prompt.py finished successfully.")
    logging.info("Output: %s", result.stdout)

    # Call the hypnotic_generator.py script
    result2 = subprocess.run(['python', 'hypnotic_generator.py'], capture_output=True, text=True)
    if result2.returncode == 0:
        logging.info("hypnotic_generator.py finished successfully.")
        logging.info("Output: %s", result2.stdout)
    else:
        logging.error("hypnotic_generator.py failed.")
        logging.error("Error: %s", result2.stderr)
else:
    logging.error("hypnotic_prompt.py failed.")
    logging.error("Error: %s", result.stderr)
