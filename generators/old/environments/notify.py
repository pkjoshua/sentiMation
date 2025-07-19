import requests
import os

def send_pushover_notification(message):
    pushover_token = os.environ.get('PUSHOVER_API')
    pushover_user = os.environ.get('PUSHOVER_USER')

    if not pushover_token or not pushover_user:
        print("Pushover API token or user key not found in environment variables.")
        return

    image_path = "assets/frames/frame_0000.png"

    # Check if the image file exists
    if not os.path.isfile(image_path):
        print("Image file not found.")
        return

    # Prepare the data and files payload for the request
    data = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }
    files = {
        "attachment": ("frame_0000.png", open(image_path, "rb"), "image/png")
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
send_pushover_notification("Environments generation process completed.")
