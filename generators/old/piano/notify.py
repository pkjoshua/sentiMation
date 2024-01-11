import requests
import os
import random

def send_pushover_notification(message, directory_path):
    pushover_token = os.environ.get('PUSHOVER_API')
    pushover_user = os.environ.get('PUSHOVER_USER')

    if not pushover_token or not pushover_user:
        print("Pushover API token or user key not found in environment variables.")
        return

    # List all files in the directory and choose one randomly
    try:
        files = os.listdir(directory_path)
        image_filename = random.choice([f for f in files if os.path.isfile(os.path.join(directory_path, f))])
        image_path = os.path.join(directory_path, image_filename)
    except Exception as e:
        print(f"Error selecting image: {e}")
        return

    # Prepare the data and files payload for the request
    data = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }
    files = {
        "attachment": (image_filename, open(image_path, "rb"), "image/jpeg")
    }

    # Send the request
    try:
        response = requests.post("https://api.pushover.net/1/messages.json", data=data, files=files)
        print(response.text)
    except Exception as e:
        print(f"Error sending notification: {e}")
    finally:
        if 'attachment' in files:
            files['attachment'][1].close()

# Example usage
send_pushover_notification("Piano generation process completed.", "assets/init/")
