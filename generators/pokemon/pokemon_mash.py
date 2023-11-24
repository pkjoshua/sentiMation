import os
import moviepy.editor as mp
from datetime import datetime

# Set paths and constants
VIDEO_PATH = "upscale.mp4"
POKEMON_SELECTED_FILE = "pokemon_selected.txt"
SOUNDS_FOLDER = "assets/sound"
OUTPUT_FOLDER = "output"
WHOS_THAT_POKEMON_START_TIME = 0  # Start time for 'whos_that_pokemon.mp3'
POKEMON_AUDIO_START_TIME = 10  # Start time for Pokémon specific audio

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to append audio to a video
def append_audio(video_path, audio_path, start_time, final_audio_path):
    video = mp.VideoFileClip(video_path)
    audio = mp.AudioFileClip(audio_path)

    if start_time + audio.duration > video.duration:
        audio = audio.set_duration(video.duration - start_time).loop(duration=video.duration - start_time)

    new_audio = audio.set_start(start_time)

    if video.audio:
        new_audio = mp.CompositeAudioClip([video.audio, new_audio])

    video_with_audio = video.set_audio(new_audio)
    video_with_audio.write_videofile(final_audio_path, codec='libx264', audio_codec='aac')
    video.close()

# Read the selected Pokemon name
with open(POKEMON_SELECTED_FILE, "r") as file:
    pokemon_name = file.read().strip()

# Create filenames for intermediate and final videos
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
intermediate_audio_path = os.path.join(OUTPUT_FOLDER, f"intermediate_{pokemon_name}_{current_datetime}.mp4")
final_audio_path = os.path.join(OUTPUT_FOLDER, f"final_{pokemon_name}_{current_datetime}.mp4")

# Append 'whos_that_pokemon.mp3' first
whos_that_pokemon_path = os.path.join(SOUNDS_FOLDER, "whos_that_pokemon.mp3")
if os.path.exists(VIDEO_PATH) and os.path.exists(whos_that_pokemon_path):
    append_audio(VIDEO_PATH, whos_that_pokemon_path, start_time=WHOS_THAT_POKEMON_START_TIME, final_audio_path=intermediate_audio_path)

# Append Pokémon specific audio second
pokemon_audio_path = os.path.join(SOUNDS_FOLDER, f"{pokemon_name}.mp3")
if os.path.exists(intermediate_audio_path) and os.path.exists(pokemon_audio_path):
    append_audio(intermediate_audio_path, pokemon_audio_path, start_time=POKEMON_AUDIO_START_TIME, final_audio_path=final_audio_path)

# Clean up intermediate file
if os.path.exists(intermediate_audio_path):
    os.remove(intermediate_audio_path)
