import os
import datetime
import logging
import textwrap
import random
import shutil
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

# Constants for easy adjustments
TXT_FONTSIZE = 80
TXT_COLOR = 'white'
TXT_OUTLINE_COLOR = 'black'
STROKE_COLOR = 'black'
TXT_WRAP_WIDTH = 40
MARGIN = 80
POSITION_FROM_BOTTOM = 1000
OUTLINE_OFFSET = 2
FADEIN_DURATION = 1.0  # Duration of the fade-in effect in seconds
TXT_FONT = 'Georgia-Bold'  # Preferred font name; will fall back if not available
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
    """Overlay text on a given video clip with fade-in effect, without ImageMagick."""
    # Wrap text into multiple lines (character-based; simple and robust)
    wrapped_lines = textwrap.wrap(text, width=TXT_WRAP_WIDTH)
    wrapped_text = "\n".join(wrapped_lines)

    max_text_width_px = max(10, clip.size[0] - MARGIN)

    # Try to load preferred font; fall back gracefully
    def load_font(preferred_name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        # Common Linux font fallback
        common_fallback_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        # If a direct path was provided, try it first
        if os.path.isfile(preferred_name):
            try:
                return ImageFont.truetype(preferred_name, size=size)
            except Exception:
                pass
        # Try preferred name as a TTF in common locations
        possible_names = [
            preferred_name,
            f"{preferred_name}.ttf",
            f"{preferred_name}.otf",
        ]
        for name in possible_names:
            if os.path.isfile(name):
                try:
                    return ImageFont.truetype(name, size=size)
                except Exception:
                    continue
        for path in common_fallback_paths:
            if os.path.isfile(path):
                try:
                    return ImageFont.truetype(path, size=size)
                except Exception:
                    continue
        # Final fallback: bitmap default font
        return ImageFont.load_default()

    font = load_font(TXT_FONT, TXT_FONTSIZE)

    # Measure text to determine required image size
    # Use multiline_textbbox for accurate metrics where available
    dummy_img = Image.new("RGBA", (max_text_width_px, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    try:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="left", stroke_width=STROKE_WIDTH)
        text_width = min(max_text_width_px, bbox[2] - bbox[0])
        text_height = bbox[3] - bbox[1]
    except Exception:
        # Fallback approximation if PIL is older
        line_heights = []
        max_line_width = 0
        for line in wrapped_lines:
            w, h = draw.textsize(line, font=font)
            max_line_width = max(max_line_width, w)
            line_heights.append(h)
        text_width = min(max_text_width_px, max_line_width)
        # Add 20% line spacing
        text_height = int(sum(line_heights) * 1.2 if line_heights else TXT_FONTSIZE)

    # Create transparent image for the text
    text_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)

    # Draw the text with stroke/outline for readability
    try:
        draw.multiline_text(
            (0, 0),
            wrapped_text,
            font=font,
            fill=TXT_COLOR,
            align="left",
            stroke_width=STROKE_WIDTH,
            stroke_fill=TXT_OUTLINE_COLOR,
            spacing=int(TXT_FONTSIZE * 0.2),
        )
    except TypeError:
        # Older PIL without stroke support: draw crude outline manually
        offsets = [(-OUTLINE_OFFSET, 0), (OUTLINE_OFFSET, 0), (0, -OUTLINE_OFFSET), (0, OUTLINE_OFFSET)]
        for dx, dy in offsets:
            draw.multiline_text((dx, dy), wrapped_text, font=font, fill=TXT_OUTLINE_COLOR, align="left")
        draw.multiline_text((0, 0), wrapped_text, font=font, fill=TXT_COLOR, align="left")

    # Convert to numpy array for MoviePy and build an ImageClip
    text_array = np.array(text_img)
    txt_clip = ImageClip(text_array)

    # Positioning similar to previous logic
    x_position = 'center'
    y_position = clip.size[1] - txt_clip.size[1] - POSITION_FROM_BOTTOM
    txt_position = (x_position, y_position)

    txt_clip = txt_clip.set_position(txt_position).set_duration(clip.duration)

    # Apply fade-in effect to the text clip
    txt_clip = txt_clip.crossfadein(FADEIN_DURATION)

    # Overlay text clip on video clip
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

# Specify the directories (robust to current working directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
generations_folder = os.path.join(BASE_DIR, 'assets', 'upscale_generations')
output_folder = os.path.join(BASE_DIR, 'output')

# Main execution
selected_quote_file = os.path.join(BASE_DIR, 'selected_quote.txt')  # Path to the selected quote file

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Concatenate the videos
concatenate_videos(generations_folder, output_folder, selected_quote_file)
