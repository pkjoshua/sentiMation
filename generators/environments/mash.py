import cv2
import os
import datetime
import logging
import re

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def extract_artist_name(file_path):
    """Extracts artist name from the given text file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            match = re.search(r"style of (.*?),", content)
            if match:
                return match.group(1).replace(" ", "_")
            return ""  # Return empty string if no match
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
        return ""
    except Exception as e:
        logging.warning(f"Error extracting artist name: {e}")
        return ""

def create_video_from_frames(frame_folder, output_folder, fps, artist_name):
    """
    Creates a video from image frames in the specified folder.

    :param frame_folder: Path to the folder containing the frames.
    :param output_folder: Path to the folder where the output video will be saved.
    :param fps: Frames per second for the output video.
    :param artist_name: Name of the artist to be used in the file name.
    :return: Path to the created video.
    """
    images = [img for img in os.listdir(frame_folder) if img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('generation_')[1].split('.jpg')[0]))

    if not images:
        logging.warning("No images found in the folder.")
        return

    frame = cv2.imread(os.path.join(frame_folder, images[0]))
    height, width, layers = frame.shape
    size = (width, height)

    current_datetime = datetime.datetime.now()
    # Naming the file based on artist name if available
    if artist_name:
        output_video_name = f"{artist_name}_final_{current_datetime.strftime('%m%d%Y%H%M')}.mp4"
    else:
        output_video_name = f"final_output_{current_datetime.strftime('%m%d%Y%H%M')}.mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for image in images:
        video.write(cv2.imread(os.path.join(frame_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    logging.info(f"Video creation complete: {output_video_path}")
    return output_video_path

# Read the artist name from the text file
artist_name = extract_artist_name("chosen_prompt.txt")

# Specify the directories
frame_folder = 'assets\\upscale'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video and get the path
output_video_path = create_video_from_frames(frame_folder, output_folder, fps=30, artist_name=artist_name)

logging.info("Video creation from upscaled frames is complete.")
