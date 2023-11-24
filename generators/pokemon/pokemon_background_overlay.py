import cv2
import os
from PIL import Image

# Function to extract frames from a video
def extract_frames(video_path, output_dir):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(output_dir, f"frame_{count:04d}.png")
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

def create_additional_frames(background_path, pokemon_path, mask_path, output_dir, start_count, num_frames=115):
    background = Image.open(background_path).convert("RGBA")
    pokemon = Image.open(pokemon_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    bg_resized = background.resize(pokemon.size)

    for i in range(num_frames):
        combined = Image.composite(pokemon, bg_resized, mask)
        frame_filename = f"frame_{start_count + i:04d}.png"
        combined.save(os.path.join(output_dir, frame_filename))

# Function to recompile frames into a video
def recompile_video(frames_dir, output_video_path, fps=30):
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')],
                         key=lambda x: int(x.split('_')[1].split('.png')[0]))

    first_frame = cv2.imread(os.path.join(frames_dir, frame_files[0]))
    height, width, layers = first_frame.shape
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(frames_dir, frame_file))
        video.write(frame)

    video.release()

# Paths and directories
video_path = "lowscale.mp4"
background_path = "background.png"
mask_path = "current_mask.png"
pokemon_path = "current_pokemon.png"
frames_dir = "frames"
overlayed_frames_dir = "overlayed_frames"
output_video_path = "lowscale_overlay.mp4"

# Ensure directories exist
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(overlayed_frames_dir, exist_ok=True)

# Extract and overlay frames
extract_frames(video_path, frames_dir)
overlay_frames_on_background(frames_dir, background_path, mask_path, overlayed_frames_dir)

# Determine the starting frame number for additional frames
start_frame_count = len(os.listdir(overlayed_frames_dir))

# Create and append additional frames
create_additional_frames(background_path, pokemon_path, mask_path, overlayed_frames_dir, start_frame_count)

# Recompile the video
recompile_video(overlayed_frames_dir, output_video_path)

print("Video processing complete. Final video saved as:", output_video_path)