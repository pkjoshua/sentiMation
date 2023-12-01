import os
import cv2
import logging
from PIL import Image, ImageOps

# Set up logging
logging.basicConfig(filename="pokemon_log.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Constants
FPS = 30
NUM_EXTRA_FRAMES = 115

# Function to extract frames from a video
def extract_frames(video_path, output_dir, file_prefix=""):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(output_dir, f"{file_prefix}frame_{count:04d}.png")
        cv2.imwrite(frame_path, image)     
        success, image = vidcap.read()
        count += 1
    return count

# Function to overlay frames with a static background image
def overlay_frames_with_background(frames_dir, background_path, mask_path, output_dir):
    background = Image.open(background_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")

    frame_files = sorted(os.listdir(frames_dir), key=lambda x: int(x.split('_')[2].split('.png')[0]))
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = Image.open(frame_path).convert("RGBA")
        
        # Resize background image to match frame size
        bg_resized = background.resize(frame.size)
        
        # Overlay frame on resized background using the mask
        combined = Image.composite(frame, bg_resized, mask)
        combined_path = os.path.join(output_dir, f"overlay_{frame_file}")
        combined.save(combined_path, format="PNG")

# Function to compile all frames into a video
def create_video_from_frames(frames_dir, output_video_path, fps):
    
    frame_files = sorted(
        [os.path.join(frames_dir, file) for file in os.listdir(frames_dir) if file.endswith('.png')],
        key=lambda x: int(x.split('_')[4].split('.png')[0])
    )

    if not frame_files:
        logging.error("No frames found in the folder.")
        return

    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape
    size = (width, height)

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        out.write(frame)
    out.release()

# Paths and directories
upscale_video_path = "upscale.mp4"
background_path = "background.png"
pokemon_image_path = "current_pokemon_upscale.png"
mask_path = "current_mask_upscale.png"  # Path to the mask image
upscale_dir = "upscale_process"
output_dir = "upscale_overlay"
os.makedirs(upscale_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Extract and process frames
extract_frames(upscale_video_path, upscale_dir, "upscale_")
num_frames = extract_frames(upscale_video_path, upscale_dir, "upscale_") # Number of frames in upscale.mp4

# Append copies of current_pokemon_upscale.png
pokemon_img = cv2.imread(pokemon_image_path)
for i in range(NUM_EXTRA_FRAMES):
    cv2.imwrite(os.path.join(upscale_dir, f"upscale_frame_{num_frames + i:04d}.png"), pokemon_img)

# Overlay frames with background
overlay_frames_with_background(upscale_dir, background_path, mask_path, output_dir)

# Compile all overlay frames into a video
create_video_from_frames(output_dir, "upscale_overlay.mp4", FPS)

logging.info("Background overlay and video compilation complete.")
