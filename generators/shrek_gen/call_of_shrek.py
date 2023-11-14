import subprocess

# Function to run the scripts
def run_scripts():
    # Call the first script
    result = subprocess.run(['python', 'shrek_CN_image_gen.py'], capture_output=True, text=True)

    # Check if the first script was successful
    if result.returncode == 0:
        print("First script finished successfully.")
        print("Output:", result.stdout)
        # Call the second script
        result2 = subprocess.run(['python', 'shrek_generator.py'], capture_output=True, text=True)
        if result2.returncode == 0:
            print("Second script finished successfully.")
            print("Output:", result2.stdout)
        else:
            print("Second script failed.")
            print("Error:", result2.stderr)
    else:
        print("First script failed.")
        print("Error:", result.stderr)

# Run the scripts four times
for i in range(4):
    print(f"Running iteration {i + 1}")
    run_scripts()
    print("\n")
