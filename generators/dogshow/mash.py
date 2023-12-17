import cv2
import os
import datetime
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def create_video_from_frames(frame_folder, output_folder, fps):
    images = [img for img in os.listdir(frame_folder) if img.endswith(".jpg")]
    # Updated sorting: extracting the number after 'upscaled_generation_'
    images.sort(key=lambda x: int(x.split('generation_')[1].split('.jpg')[0]))


    if not images:
        logging.warning("No images found in the folder.")
        return

    # Determine the width and height from the first image
    frame = cv2.imread(os.path.join(frame_folder, images[0]))
    height, width, layers = frame.shape
    size = (width, height)

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("output_%m%d%Y%H%M") + ".mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    # Initialize video writer
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    # Add frames to the video
    for image in images:
        video.write(cv2.imread(os.path.join(frame_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    logging.info(f"Video creation complete: {output_video_path}")

# Specify the directories
frame_folder = 'assets\\upscale'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video
create_video_from_frames(frame_folder, output_folder, fps=30)

logging.info("Video creation from upscaled frames is complete.")
