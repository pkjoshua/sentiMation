import tkinter as tk
from tkinter import filedialog
from PIL import Image, ExifTags
import threading
import subprocess
import time
from tkinter import ttk
import logging
import os 
import json
import shutil

# Set up main logging
logging.basicConfig(filename='gen.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Set up generation time logging
gentime_logger = logging.getLogger('gentime_logger')
gentime_handler = logging.FileHandler('gentime.log')
gentime_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
gentime_logger.addHandler(gentime_handler)
gentime_logger.setLevel(logging.INFO)

def reorient_image(input_path):
    try:
        img = Image.open(input_path)
        exif = img._getexif()

        if exif is not None:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)

        img.save(input_path)
        img.close()
    except (AttributeError, KeyError, IndexError, TypeError):
        logging.warning("Could not determine the orientation of the image or reorient it.")

# Function to clear contents of a directory
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {e}")

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

def execute_scripts():
    # Clear directories in assets folder
    for dir_name in ['generations', 'init', 'inputs', 'lowscale', 'upscale', 'upscale_generations']:
        clear_directory(os.path.join('assets/', dir_name))
    # Directory where input files will be stored
    input_dir = 'assets/inputs'
    os.makedirs(input_dir, exist_ok=True)

    # Retrieve input values
    user_integer = integer_entry.get()
    user_prompt = prompt_entry.get()
    user_negative_prompt = negative_prompt_entry.get()
    image_path = image_path_entry.get()

    # Save settings to a JSON file
    settings = {
        'user_integer': user_integer,
        'user_prompt': user_prompt,
        'user_negative_prompt': user_negative_prompt
    }
    with open(os.path.join(input_dir, 'settings.json'), 'w') as file:
        json.dump(settings, file, indent=4)

    # Copy the input image to assets/inputs directory and reorient it
    if os.path.isfile(image_path):
        copied_image_path = os.path.join(input_dir, 'input_image' + os.path.splitext(image_path)[1])
        shutil.copy(image_path, copied_image_path)
        reorient_image(copied_image_path)

    # Update progress and run scripts
    for i, script in enumerate(['CN_image_gen.py', 'generator.py', 'upscale.py', 'mash.py']):
        update_progress(i+1)
        run_script(script)
    update_progress(5)
    print("All scripts completed")

# Function to update progress bar
def update_progress(stage):
    progress_var.set(stage)
    window.update_idletasks()

# Create the main window
window = tk.Tk()
window.title("Script Runner")

# Set up input fields and labels
integer_entry = tk.Entry(window)
prompt_entry = tk.Entry(window)
negative_prompt_entry = tk.Entry(window)

integer_label = tk.Label(window, text="Enter an Integer:")
prompt_label = tk.Label(window, text="Enter a Prompt:")
negative_prompt_label = tk.Label(window, text="Enter a Negative Prompt:")

# File dialog for image selection
def open_file_dialog():
    file_path = filedialog.askopenfilename()
    image_path_entry.delete(0, tk.END)
    image_path_entry.insert(0, file_path)

image_path_entry = tk.Entry(window)
image_path_button = tk.Button(window, text="Select Image", command=open_file_dialog)

# Set up progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(window, length=200, variable=progress_var, maximum=5)

# Start button
start_button = tk.Button(window, text="Start", command=lambda: threading.Thread(target=execute_scripts).start())

# Layout
integer_label.pack()
integer_entry.pack()
prompt_label.pack()
prompt_entry.pack()
negative_prompt_label.pack()
negative_prompt_entry.pack()
image_path_entry.pack()
image_path_button.pack()
progress_bar.pack()
start_button.pack()

# Run the main loop
window.mainloop()