import os
import datetime
import logging
import textwrap
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def overlay_text_on_clip(clip, text):
    """Overlay text on a given video clip."""
    # Define text properties
    txt_fontsize = 36  # Adjust fontsize as needed
    txt_color = 'white'
    txt_wrap_width = 40  # Adjust wrap width as needed

    # Create a wrapped text
    wrapped_text = "\n".join(textwrap.wrap(text, width=txt_wrap_width))

    # Define text clip with wrapping
    txt_clip = TextClip(wrapped_text, fontsize=txt_fontsize, color=txt_color, align='West', method='label', size=(clip.size[0]-40, None))

    # Position of the text: slightly above the bottom
    x_position = 'center'
    y_position = clip.size[1] - txt_clip.size[1] - 100  # 20 pixels above the bottom
    txt_position = (x_position, y_position)

    txt_clip = txt_clip.set_position(txt_position).set_duration(clip.duration)

    # Overlay text clip on video clip
    return CompositeVideoClip([clip, txt_clip])

def concatenate_videos(video_folder, output_folder, prompts):
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort()  # Sort to ensure they are in order

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    all_clips = []
    for idx, video_file in enumerate(video_files):
        clip = VideoFileClip(video_file)
        if idx < len(prompts):
            clip_with_text = overlay_text_on_clip(clip, prompts[idx])
            all_clips.extend([clip_with_text, clip_with_text.copy(), clip_with_text.copy()])
        else:
            logging.warning(f"No prompt for video {idx}, adding without text.")
            all_clips.extend([clip, clip.copy(), clip.copy()])

    # Concatenate all clips including the copies
    final_clip = concatenate_videoclips(all_clips, method="compose")

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("final_output_%m%d%Y%H%M") + ".mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    final_clip.write_videofile(output_video_path, codec="libx264")

    logging.info(f"Final video created: {output_video_path}")

    # Close all clips to free memory
    for clip in all_clips:
        clip.close()

# Function to read prompts from selected_story.txt
def read_prompts(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    prompts = [line.strip().replace("Story: ", "") for line in lines if line.startswith("Story:")]
    return prompts

# Specify the directories
generations_folder = 'assets\\upscale_generations'
output_folder = 'output'
selected_story_path = 'selected_story.txt'

# Read prompts from the selected story
prompts = read_prompts(selected_story_path)

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Concatenate the videos
concatenate_videos(generations_folder, output_folder, prompts)
