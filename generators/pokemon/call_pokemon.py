import subprocess
import logging

# Set up logging
logging.basicConfig(filename='pokemon_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Call the pokemon_prompt.py script
result = subprocess.run(['python', 'pokemon_prompt.py'], capture_output=True, text=True)

# Check if pokemon_prompt.py was successful
if result.returncode == 0:
    logging.info("pokemon_prompt.py finished successfully.")
    logging.info("Output: %s", result.stdout)

    # Call the pokemon_generator.py script
    result2 = subprocess.run(['python', 'pokemon_generator.py'], capture_output=True, text=True)
    if result2.returncode == 0:
        logging.info("pokemon_generator.py finished successfully.")
        logging.info("Output: %s", result2.stdout)
    else:
        logging.error("pokemon_generator.py failed.")
        logging.error("Error: %s", result2.stderr)
else:
    logging.error("pokemon_prompt.py failed.")
    logging.error("Error: %s", result.stderr)
