import os
import datetime
import logging
import textwrap
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# Constants for easy adjustments
TXT_FONTSIZE = 36
TXT_COLOR = 'white'
TXT_OUTLINE_COLOR = 'black'
TXT_WRAP_WIDTH = 40
MARGIN = 80
POSITION_FROM_BOTTOM = 50
OUTLINE_OFFSET = 2
FADEIN_DURATION = 1.0  # Duration of the fade-in effect in seconds

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def overlay_text_on_clip(clip, text):
    """Overlay text on a given video clip with fade-in effect."""
    # Create a wrapped text
    wrapped_text = "\n".join(textwrap.wrap(text, width=TXT_WRAP_WIDTH))

    # Define text clip with wrapping
    txt_clip = TextClip(wrapped_text, fontsize=TXT_FONTSIZE, color=TXT_COLOR, align='West', method='label', size=(clip.size[0]-MARGIN, None))

    # Define an outline text clip (black color) slightly larger size
    txt_clip_outline = TextClip(wrapped_text, fontsize=TXT_FONTSIZE, color=TXT_OUTLINE_COLOR, align='West', method='label', size=(clip.size[0]-MARGIN, None))

    # Position of the text: slightly below the top
    x_position = 'center'
    y_position_top_margin = 800  # You can adjust this value to change the distance from the top
    y_position = y_position_top_margin
    txt_position = (x_position, y_position)

    # Positioning the outline text slightly offset from the main text
    txt_outline_position = (x_position, y_position + OUTLINE_OFFSET)

    txt_clip = txt_clip.set_position(txt_position).set_duration(clip.duration)
    txt_clip_outline = txt_clip_outline.set_position(txt_outline_position).set_duration(clip.duration)

    # Apply fade-in effect to the text clips
    txt_clip = txt_clip.crossfadein(FADEIN_DURATION)
    txt_clip_outline = txt_clip_outline.crossfadein(FADEIN_DURATION)

    # Overlay both text clips on video clip
    final_clip = CompositeVideoClip([clip, txt_clip_outline, txt_clip])

    return final_clip.set_duration(clip.duration)


def concatenate_videos(video_folder, clips_folder, output_folder, prompts):
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort()  # Sort to ensure they are in order

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    final_clips = []

    for idx, video_file in enumerate(video_files):
        clip = VideoFileClip(video_file)
        # Creating a single clip with 3 copies
        combined_clip = concatenate_videoclips([clip, clip.copy(), clip.copy()], method="compose")
        combined_clip_path = os.path.join(clips_folder, f"combined_clip_{idx:04d}.mp4")
        if idx < len(prompts):
            combined_clip_with_text = overlay_text_on_clip(combined_clip, prompts[idx])
            combined_clip_with_text.write_videofile(combined_clip_path, codec="libx264")
        else:
            logging.warning(f"No prompt for video {idx}, adding without text.")
            combined_clip.write_videofile(combined_clip_path, codec="libx264")
        final_clips.append(VideoFileClip(combined_clip_path))

        # Close clips to free memory
        clip.close()
        combined_clip.close()
        if 'combined_clip_with_text' in locals():
            combined_clip_with_text.close()

    # Concatenate all final clips into one video
    final_video = concatenate_videoclips(final_clips, method="compose")
    current_datetime = datetime.datetime.now()
    final_video_name = current_datetime.strftime("final_output_%d%m%Y%H%M") + ".mp4"
    final_video_path = os.path.join(output_folder, final_video_name)
    final_video.write_videofile(final_video_path, codec="libx264")
    logging.info(f"Final video created: {final_video_path}")

    # Close final clips to free memory
    for clip in final_clips:
        clip.close()

# Function to read prompts from selected_story.txt
def read_prompts(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    prompts = [line.strip().replace("Story: ", "") for line in lines if line.startswith("Story:")]
    return prompts

# Specify the directories
generations_folder = 'assets\\upscale_generations'
clips_folder = 'assets\\clips'
output_folder = 'output'
selected_story_path = 'selected_story.txt'

# Ensure folders exist
os.makedirs(clips_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Read prompts from the selected story
prompts = read_prompts(selected_story_path)

# Concatenate the videos
concatenate_videos(generations_folder, clips_folder, output_folder, prompts)
