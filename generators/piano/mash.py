import os
import datetime
import logging
import textwrap
import random
import shutil
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

# Constants for easy adjustments
TXT_FONTSIZE = 60
TXT_COLOR = 'white'
TXT_OUTLINE_COLOR = 'black'
STROKE_COLOR = 'black'
TXT_WRAP_WIDTH = 40
MARGIN = 80
POSITION_FROM_BOTTOM = 200
OUTLINE_OFFSET = 2
FADEIN_DURATION = 1.0  # Duration of the fade-in effect in seconds
TXT_FONT = 'Georgia-Bold'  # or the exact name of the font as installed on your system
STROKE_WIDTH = 1

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def read_quote(quote_file):
    """Read the quote from the specified file."""
    with open(quote_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

    # Move the file to the used folder
    shutil.move(os.path.join(quotes_folder, random_file), os.path.join(used_folder, random_file))

    return quote

def overlay_text_on_clip(clip, text):
    """Overlay text on a given video clip with fade-in effect."""
    # Create a wrapped text
    wrapped_text = "\n".join(textwrap.wrap(text, width=TXT_WRAP_WIDTH))

    # Define text clip with wrapping and stroke
    txt_clip = TextClip(wrapped_text, fontsize=TXT_FONTSIZE, color=TXT_COLOR, font=TXT_FONT, align='West', method='label', size=(clip.size[0]-MARGIN, None), stroke_color=TXT_OUTLINE_COLOR, stroke_width=STROKE_WIDTH)

    # Positioning the text and outline
    x_position = 'center'
    y_position = clip.size[1] - txt_clip.size[1] - POSITION_FROM_BOTTOM
    txt_position = (x_position, y_position)

    txt_clip = txt_clip.set_position(txt_position).set_duration(clip.duration)

    # Apply fade-in effect to the text clips
    txt_clip = txt_clip.crossfadein(FADEIN_DURATION)

    # Overlay both text clips on video clip
    final_clip = CompositeVideoClip([clip, txt_clip])

    return final_clip.set_duration(clip.duration)

def concatenate_videos(video_folder, output_folder, quote_file):
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort()  # Sort to ensure they are in order

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    all_clips = [VideoFileClip(video_file) for video_file in video_files]

    # Duplicate each clip to double the final video length
    all_clips = all_clips + all_clips.copy()

    # Concatenate all clips
    final_clip = concatenate_videoclips(all_clips, method="compose")

    # Read the selected quote
    selected_quote = read_quote(quote_file)

    # Overlay text on the final clip
    final_clip = overlay_text_on_clip(final_clip, selected_quote)

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("final_output_%m%d%Y%H%M") + ".mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    final_clip.write_videofile(output_video_path, codec="libx264")

    logging.info(f"Final video created: {output_video_path}")

    # Close all clips to free memory
    for clip in all_clips:
        clip.close()

# Specify the directories
generations_folder = 'assets\\upscale_generations'
output_folder = 'output'

# Main execution
selected_quote_file = 'selected_quote.txt'  # Path to the selected quote file

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Concatenate the videos
concatenate_videos(generations_folder, output_folder, selected_quote_file)
