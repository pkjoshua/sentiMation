import subprocess
import logging

# Set up logging
logging.basicConfig(filename='pokemon_cards_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Call the pokemon_prompt.py script
result = subprocess.run(['python', 'pokemon_cards_prompt.py'], capture_output=True, text=True)

# Check if pokemon_prompt.py was successful
if result.returncode == 0:
    logging.info("pokemon_cards_prompt.py finished successfully.")
    logging.info("Output: %s", result.stdout)

    # Call the pokemon_generator.py script
    result2 = subprocess.run(['python', 'pokemon_cards_generator.py'], capture_output=True, text=True)
    if result2.returncode == 0:
        logging.info("pokemon_cards_generator.py finished successfully.")
        logging.info("Output: %s", result2.stdout)
    else:
        logging.error("pokemon_cards_generator.py failed.")
        logging.error("Error: %s", result2.stderr)
else:
    logging.error("pokemon_cards_prompt.py failed.")
    logging.error("Error: %s", result.stderr)
