import os
import moviepy.editor as mp
import logging

# Initialize logging
logging.basicConfig(filename="pokemon_log.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Set paths and constants
VIDEO_PATH = "upscale.mp4"
POKEMON_SELECTED_FILE = "pokemon_selected.txt"
SOUNDS_FOLDER = "assets/sound"
FINAL_AUDIO_PATH = "final_video_with_audio.mp4"
INTERMEDIATE_AUDIO_PATH = "intermediate_video_with_audio.mp4"

# Read the selected Pokemon name
with open(POKEMON_SELECTED_FILE, "r") as file:
    pokemon_name = file.read().strip()
pokemon_audio_path = os.path.join(SOUNDS_FOLDER, f"{pokemon_name}.mp3")
whos_that_pokemon_path = os.path.join(SOUNDS_FOLDER, "whos_that_pokemon.mp3")

# Function to append audio to a video
def append_audio(video_path, audio_path, start_time, final_audio_path):
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(audio_path)

        if start_time + audio.duration > video.duration:
            # If the audio duration extends beyond the video's duration, loop the audio
            audio = audio.set_duration(video.duration - start_time).loop(duration=video.duration - start_time)

        new_audio = audio.set_start(start_time)

        if video.audio:
            # If the video already has an audio track, combine the two
            new_audio = mp.CompositeAudioClip([video.audio, new_audio])

        video_with_audio = video.set_audio(new_audio)
        video_with_audio.write_videofile(final_audio_path, codec='libx264', audio_codec='aac')
        logging.info(f"Audio appended successfully to {final_audio_path}")
    except Exception as e:
        logging.error(f"Error processing video: {e}")
    finally:
        video.close()

try:
    # Append 'whos_that_pokemon.mp3' first
    if os.path.exists(VIDEO_PATH) and os.path.exists(whos_that_pokemon_path):
        append_audio(VIDEO_PATH, whos_that_pokemon_path, start_time=0, final_audio_path=INTERMEDIATE_AUDIO_PATH)
    else:
        logging.error("Video or 'whos_that_pokemon.mp3' not found for the first appending process.")

    # Read the selected Pokemon name
    with open(POKEMON_SELECTED_FILE, "r") as file:
        pokemon_name = file.read().strip()
    pokemon_audio_path = os.path.join(SOUNDS_FOLDER, f"{pokemon_name}.mp3")

    # Append Pokémon specific audio second at the 9-second mark
    if os.path.exists(INTERMEDIATE_AUDIO_PATH) and os.path.exists(pokemon_audio_path):
        append_audio(INTERMEDIATE_AUDIO_PATH, pokemon_audio_path, start_time=8, final_audio_path=FINAL_AUDIO_PATH)
    else:
        logging.error("Intermediate video or audio file for the Pokémon not found for the second appending process.")

    # Clear intermediate file
    if os.path.exists(INTERMEDIATE_AUDIO_PATH):
        os.remove(INTERMEDIATE_AUDIO_PATH)
        logging.info("Intermediate audio file removed.")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
