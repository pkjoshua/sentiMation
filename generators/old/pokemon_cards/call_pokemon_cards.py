import subprocess
import logging
import time  # Import the time module

# Set up logging
logging.basicConfig(filename='pokemon_cards_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Call the pokemon_prompt.py script
result = subprocess.run(['python', 'pokemon_cards_prompt.py'], capture_output=True, text=True)

# Check if pokemon_prompt.py was successful
if result.returncode == 0:
    logging.info("pokemon_cards_prompt.py finished successfully.")
    logging.info("Output: %s", result.stdout)
else:
    logging.error("pokemon_cards_prompt.py failed.")
    logging.error("Error: %s", result.stderr)

time.sleep(10)  # 10-second pause

# Call the pokemon_cards_generator.py script
result2 = subprocess.run(['python', 'pokemon_cards_generator.py'], capture_output=True, text=True)

# Check if pokemon_generator.py was successful
if result2.returncode == 0:
    logging.info("pokemon_cards_generator.py finished successfully.")
    logging.info("Output: %s", result2.stdout)
else:
    logging.error("pokemon_cards_generator.py failed.")
    logging.error("Error: %s", result2.stderr)

time.sleep(10)  # 10-second pause

# Call the pokemon_cards_upscale.py script
result3 = subprocess.run(['python', 'pokemon_cards_upscale.py'], capture_output=True, text=True)

# Check if pokemon_cards_upscale.py was successful
if result3.returncode == 0:
    logging.info("pokemon_cards_upscale.py finished successfully.")
    logging.info("Output: %s", result3.stdout)
else:
    logging.error("pokemon_cards_upscale.py failed.")
    logging.error("Error: %s", result3.stderr)

time.sleep(10)  # 10-second pause

# Call the pokemon_cards_mash.py script
result4 = subprocess.run(['python', 'pokemon_cards_mash.py'], capture_output=True, text=True)

# Check if pokemon_cards_mash.py was successful
if result4.returncode == 0:
    logging.info("pokemon_cards_mash.py finished successfully.")
    logging.info("Output: %s", result4.stdout)
else:
    logging.error("pokemon_cards_mash.py failed.")
    logging.error("Error: %s", result4.stderr)
