import os
import requests


def send_pushover_notification(message: str, image_path: str | None = None) -> None:
    """Send a pushover notification if credentials are configured."""
    token = os.getenv("PUSHOVER_API")
    user = os.getenv("PUSHOVER_USER")
    if not (token and user):
        # Notification is optional; just log to stdout
        print("Pushover credentials not configured. Skipping notification.")
        return

    data = {"token": token, "user": user, "message": message}
    files = None

    if image_path and os.path.isfile(image_path):
        files = {"attachment": (os.path.basename(image_path), open(image_path, "rb"), "image/png")}

    try:
        resp = requests.post("https://api.pushover.net/1/messages.json", data=data, files=files)
        print(f"Pushover response: {resp.text}")
    finally:
        if files:
            files["attachment"][1].close()
