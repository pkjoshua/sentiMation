import http.client
import urllib.parse
import os

def send_pushover_notification(message):
    pushover_token = os.environ.get('PUSHOVER_API')
    pushover_user = os.environ.get('PUSHOVER_USER')

    if not pushover_token or not pushover_user:
        print("Pushover API token or user key not found in environment variables.")
        return

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": pushover_token,
                     "user": pushover_user,
                     "message": message,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    print(response.status, response.reason)

    conn.close()

# Example usage
send_pushover_notification("Generation process completed.")
