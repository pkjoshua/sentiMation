import os
import random
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def read_file_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def select_random_character(characters_file):
    characters = read_file_lines(characters_file)
    return random.choice(characters)

def select_random_story_and_prompt(story_dir, prompt_dir, characters_file, output_file):
    story_files = [f for f in os.listdir(story_dir) if f.endswith('.txt')]
    selected_story_file = random.choice(story_files)
    base_filename = os.path.splitext(selected_story_file)[0]

    story_file_path = os.path.join(story_dir, selected_story_file)
    prompt_file_path = os.path.join(prompt_dir, f"{base_filename}_prompt.txt")

    if not os.path.exists(prompt_file_path):
        raise FileNotFoundError(f"No corresponding prompt file found for {selected_story_file}")

    selected_character = select_random_character(characters_file)
    story_lines = read_file_lines(story_file_path)
    prompt_lines = read_file_lines(prompt_file_path)

    with open(output_file, 'w', encoding='utf-8') as file:
        for story, prompt in zip(story_lines, prompt_lines):
            modified_story = story.replace("[CHARACTER]", selected_character)
            modified_prompt = prompt.replace("[CHARACTER]", selected_character)
            file.write(f"Story: {modified_story}\nPrompt: {modified_prompt}\n\n")

# Define directories, character file, and output file
story_dir = "assets/stories"
prompt_dir = "assets/prompts"
characters_file = "assets/devices/characters.txt"
output_file = "selected_story.txt"

# Select random story and corresponding prompts, then save to file
try:
    select_random_story_and_prompt(story_dir, prompt_dir, characters_file, output_file)
    print(f"Selected story and prompts saved to {output_file}")
except FileNotFoundError as e:
    print(e)