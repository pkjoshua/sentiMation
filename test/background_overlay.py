import cv2
import os
from PIL import Image

# Function to extract frames from a video
def extract_frames(video_path, output_dir):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(output_dir, f"frame{count}.png")
        cv2.imwrite(frame_path, image)     
        success, image = vidcap.read()
        count += 1

# Function to overlay frames on a background image
def overlay_frames_on_background(frames_dir, background_path, mask_path, output_dir):
    background = Image.open(background_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")

    for frame_filename in os.listdir(frames_dir):
        frame_path = os.path.join(frames_dir, frame_filename)
        with Image.open(frame_path).convert("RGBA") as frame:
            bg_resized = background.resize(frame.size)
            combined = Image.composite(frame, bg_resized, mask)
            combined.save(os.path.join(output_dir, frame_filename))

# Function to recompile frames into a video
def recompile_video(frames_dir, output_video_path, fps=8):
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')],
                         key=lambda x: int(x.replace('frame', '').replace('.png', '')))

    first_frame = cv2.imread(os.path.join(frames_dir, frame_files[0]))
    height, width, layers = first_frame.shape
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(frames_dir, frame_file))
        video.write(frame)

    video.release()

# Paths
video_path = "gen.mp4"  # Path to the generated video
background_path = "background.png"  # Path to the background image
mask_path = "bulbasaur_mask.png"  # Path to the mask image
frames_dir = "frames"
overlayed_frames_dir = "overlayed_frames"
output_video_path = "final_output.mp4"

# Ensure directories exist
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(overlayed_frames_dir, exist_ok=True)

# Process the video
extract_frames(video_path, frames_dir)
overlay_frames_on_background(frames_dir, background_path, mask_path, overlayed_frames_dir)
recompile_video(overlayed_frames_dir, output_video_path)

print("Video processing complete. Final video saved as:", output_video_path)
