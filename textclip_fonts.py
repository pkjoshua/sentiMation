from moviepy.editor import TextClip, concatenate_videoclips
import matplotlib.font_manager

# Fetching the list of font names
fonts_list = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

# Limit the number of fonts to a reasonable number to keep the video short
max_fonts = 50
selected_fonts = fonts_list[:max_fonts]

clips = []

for font in selected_fonts:
    try:
        # Create a text clip for each font
        clip = TextClip(f"Font: {font.split('/')[-1].split('.')[0]}", font=font, fontsize=24, color='white', bg_color='black', size=(640, 480))
        clip = clip.set_duration(2)  # Set duration for each clip
        clips.append(clip)
    except Exception as e:
        print(f"Error with font {font}: {e}")

# Concatenate all clips into one video
final_clip = concatenate_videoclips(clips, method="compose")

# Write the video to a file
final_clip.write_videofile("fonts_showcase.mp4", fps=24)
