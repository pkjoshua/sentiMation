import cv2
import json
import os
import base64
import tempfile

def video_to_frames(video_filename, vids_dir='D:\\sentiMation\\generators\\dogshow\\assets\\vids', frames_dir='D:\\sentiMation\\generators\\dogshow\\assets\\frames'):
    # Construct full paths for video and frames directory
    video_path = os.path.join(vids_dir, video_filename)
    output_dir = os.path.join(frames_dir, video_filename.split('.')[0])  # Separate directory for each video

    # Create the frames directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    frame_paths = []
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Save frame as JPEG file
        frame_path = os.path.join(output_dir, f"frame_{frame_count:05}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        frame_count += 1

    cap.release()
    return frame_paths

def construct_payload(frame_paths, script_name):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    script_args = [None] * 10  # Adjust the length as needed

    script_args[0] = "None"

    frame_list = []
    for path in frame_paths:
        # Read and base64 encode the frame
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        frame_arg = {
            "_closer": {
                "delete": False,
                "file": {"data": encoded_string},
                "name": temp_dir
            },
            "delete": False,
            "file": {"data": encoded_string},
            "name": path,
            "orig_name": path
        }
        frame_list.append(frame_arg)
    script_args[1] = frame_list

        # Assign other script_args elements as necessary
    script_args[2] = 0.8
    script_args[3] = "GuideImg"
    script_args[4] = True
    script_args[5] = False
    script_args[6] = False
    script_args[7] = 1
    script_args[8] = 1
    script_args[9] = "FirstGen"

    return {
        "script_name": script_name,
        "script_args": script_args
    }

# Example usage
video_filename = 'test.mp4'  # Replace with your video file name
script_name = "multi-frame video - v0.72-beta (fine version)"

frame_paths = video_to_frames(video_filename)
payload = construct_payload(frame_paths, script_name)

# Convert payload to JSON
json_payload = json.dumps(payload, indent=4)

# Save the JSON payload to scriptargs.txt
with open('scriptargs.txt', 'w') as file:
    file.write(json_payload)

print("Payload saved to scriptargs.txt")
