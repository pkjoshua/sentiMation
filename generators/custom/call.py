#!/usr/bin/env python3
"""
Custom generator call script that accepts specific parameters from webapp
"""
import subprocess
import logging
import time
import os
import sys
import json
import shutil

# Set up logging
logging.basicConfig(filename='gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Additional logger for gentime.log
gentime_logger = logging.getLogger('gentime_logger')
gentime_logger.setLevel(logging.INFO)
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)

def clear_directory(directory):
    """Clear the contents of a directory"""
    if not os.path.exists(directory):
        return
        
    for item in os.listdir(directory):
        file_path = os.path.join(directory, item)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')

def run_script(script_name):
    """Run a script and log its output"""
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"{script_name} finished successfully.")
        logging.info("Output: %s", result.stdout)
    else:
        logging.error(f"{script_name} failed.")
        logging.error("Error: %s", result.stderr)
        raise Exception(f"Script {script_name} failed: {result.stderr}")
    time.sleep(5)  # 5-second pause between each script

def create_params_file(character, environment, prompt):
    """Create parameters file for selector.py"""
    params = {
        'character': character,
        'environment': environment,
        'prompt': prompt
    }
    with open('custom_params.json', 'w') as f:
        json.dump(params, f)
    logging.info(f"Created parameters file with: {params}")

def run_custom_generation(character=None, environment=None, prompt=None):
    """Run the custom generation sequence with specified parameters"""
    start_time = time.time()
    
    try:
        # Clear output directories before running
        directories_to_clear = [
            'assets/lowscale', 
            'assets/generations', 
            'assets/upscale',
            'assets/upscale_generations'
        ]
        for directory in directories_to_clear:
            clear_directory(directory)
        
        # If parameters are provided, create the params file
        if character and environment and prompt:
            create_params_file(character, environment, prompt)
            logging.info(f"Running custom generation with: Character={character}, Environment={environment}, Prompt={prompt}")
        else:
            logging.info("Running with existing parameters or random selection")
        
        # Run the generation sequence
        run_script('selector.py')
        run_script('init_image_gen.py')
        run_script('generator.py')
        run_script('upscale.py')
        run_script('mash.py')
        
        end_time = time.time()
        total_time = end_time - start_time
        gentime_logger.info(f"Total time for custom generation: {total_time:.2f} seconds")
        
        logging.info("Custom generation sequence completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Custom generation failed: {e}")
        return False

def main():
    """Main execution"""
    # Check for command line arguments
    if len(sys.argv) >= 4:
        character = sys.argv[1]
        environment = sys.argv[2] 
        prompt = sys.argv[3]
        logging.info(f"Running with command line args: {character}, {environment}, {prompt}")
        success = run_custom_generation(character, environment, prompt)
    else:
        # Run without specific parameters (will use existing params file or fail gracefully)
        logging.info("Running without specific parameters")
        success = run_custom_generation()
    
    if success:
        print("Custom generation completed successfully.")
    else:
        print("Custom generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()