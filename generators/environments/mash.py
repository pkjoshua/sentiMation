import cv2
import os
import datetime
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def create_video_from_frames(frame_folder, output_folder, fps):
    """
    Creates a video from image frames in the specified folder.

    :param frame_folder: Path to the folder containing the frames.
    :param output_folder: Path to the folder where the output video will be saved.
    :param fps: Frames per second for the output video.
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
    output_video_name = f"output_{current_datetime.strftime('%d%m%Y%H%M')}.mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for image in images:
        video.write(cv2.imread(os.path.join(frame_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    logging.info(f"Video creation complete: {output_video_path}")
    return output_video_path

# Specify the directories
frame_folder = 'assets\\upscale'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video and get the path
output_video_path = create_video_from_frames(frame_folder, output_folder, fps=30)

logging.info("Video creation from upscaled frames is complete.")
