import subprocess
import logging
import time
import os
import shutil
import socket

# Set up main logging
logging.basicConfig(filename='pokemon_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Set up generation time logging
gentime_logger = logging.getLogger('gentime_logger')
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)
gentime_logger.setLevel(logging.INFO)

# Function to check if server is running
def is_server_running(host="127.0.0.1", port=7860):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

# Function to start the server
def start_server():
    command = "%windir%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -ExecutionPolicy ByPass -NoExit -Command \"& 'C:\\Users\\Josh\\miniconda3\\shell\\condabin\\conda-hook.ps1' ; conda activate 'C:\\Users\\Josh\\miniconda3' ; conda activate sd ; python 'D:\\stable-diffusion-webui\\launch.py'"
    subprocess.Popen(command, shell=True)
    time.sleep(30)  # Wait for the server to start

# Function to clear the contents of a directory
def clear_directory(directory):
    for item in os.listdir(directory):
        file_path = os.path.join(directory, item)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')

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

# Function to run all scripts and track total execution time
def run_all_scripts():
    start_time = time.time()
    run_script('pokemon_prompt.py')  # Create prompt
    run_script('pokemon_generator.py')  # Generate Animation and mask
    run_script('pokemon_upscale.py')  # Upscale frames and create mp4
    run_script('pokemon_background_overlay.py')  # Overlay background
    run_script('pokemon_mash.py')
    run_script('notify.py')  # Append audio
    total_time = time.time() - start_time
    gentime_logger.info(f"Total time for all scripts: {total_time:.2f} seconds")

# Main execution
if __name__ == "__main__":
    # Check if server is running, and start if not
    if not is_server_running():
        logging.info("Server is not running. Starting server...")
        start_server()
        if not is_server_running():
            logging.error("Failed to start server. Exiting.")
            exit(1)
        else:
            logging.info("Server started successfully.")

# Clear contents of specific directories before running scripts
directories_to_clear = ['lowscale', 'upscale', 'upscale_process','upscale_overlay']
for directory in directories_to_clear:
    clear_directory(directory)

# Run the sequence of scripts
run_all_scripts()

print("Script sequence complete.")
