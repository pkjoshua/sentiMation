import requests
import json

# Replace 'your_json_file.json' with the path to your JSON file
json_file_path = 'workflow.json'

# Read JSON data from the file
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# API URL
api_url = "http://127.0.0.1:8188/prompt"

# Making a POST request to the API with the JSON data
response = requests.post(api_url, json=json_data)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful.")
    print("Response:", response.json())
else:
    print("Request failed.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
