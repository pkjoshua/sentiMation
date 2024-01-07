import subprocess
import logging
import time
import os
import socket
import shutil

# Set up logging
logging.basicConfig(filename='gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Additional logger for gentime.log
gentime_logger = logging.getLogger('gentime_logger')
gentime_logger.setLevel(logging.INFO)
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)

# Add a flag to indicate whether this script started the server
server_started_by_script = False

# Function to check if server is running
def is_server_running(host="127.0.0.1", port=7860):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

# Function to start the server
def start_server():
    global server_started_by_script
    command = "%windir%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -ExecutionPolicy ByPass -NoExit -Command \"& 'C:\\Users\\Josh\\miniconda3\\shell\\condabin\\conda-hook.ps1' ; conda activate 'C:\\Users\\Josh\\miniconda3' ; conda activate sd ; python 'D:\\stable-diffusion-webui\\launch.py'"
    subprocess.Popen(command, shell=True)
    time.sleep(30)  # Wait for the server to start
    server_started_by_script = True

# Function to stop the server
def stop_server():
    # Replace the following command with the appropriate one to stop your server
    stop_command = "COMMAND_TO_STOP_SERVER"
    subprocess.Popen(stop_command, shell=True)

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
    time.sleep(5)  # 5-second pause between each script

# Run scripts in sequence
def run_scripts_sequence():
    start_time = time.time()  # Start timing
    run_script('media_select.py')
    run_script('generator.py')
    run_script('upscale.py')
    run_script('mash.py')
    run_script('notify.py')
    end_time = time.time()  # End timing
    total_time = end_time - start_time
    gentime_logger.info(f"Total time for sequence: {total_time:.2f} seconds")

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
    directories_to_clear = ['assets\\lowscale', 'assets\\frames', 'assets\\upscale']
    for directory in directories_to_clear:
        clear_directory(directory)

    # Run the script sequence
    run_scripts_sequence()

        # Stop the server if it was started by this script
    if server_started_by_script:
        logging.info("Stopping the server started by the script...")
        stop_server()
        logging.info("Server stopped.")

    print("Script sequence complete.")
