import os
import random
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def read_file_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def select_random_word(file_path):
    words = read_file_lines(file_path)
    word_info = random.choice(words)
    word_parts = word_info.split(',')
    selected_word = word_parts[0].strip()
    word_lora = word_parts[1].strip() if len(word_parts) > 1 else ''
    return selected_word, word_lora

def select_random_prompt_and_replace(prompt_dir, characters_file, environments_file, output_file):
    prompt_files = [f for f in os.listdir(prompt_dir) if f.endswith('.txt')]
    selected_prompt_file = random.choice(prompt_files)
    prompt_file_path = os.path.join(prompt_dir, selected_prompt_file)

    selected_character, character_lora = select_random_word(characters_file)
    selected_environment = select_random_word(environments_file)[0]

    prompt_lines = read_file_lines(prompt_file_path)

    with open(output_file, 'w', encoding='utf-8') as file:
        for prompt in prompt_lines:
            modified_prompt = prompt.replace("[CHARACTER]", selected_character).replace("[ENVIRONMENT]", selected_environment)
            modified_prompt = modified_prompt.replace("[LORA]", character_lora) if character_lora else modified_prompt.replace("[LORA]", '')
            file.write(f"{modified_prompt}\n\n")

# Define directories, character file, environment file, and output file
prompt_dir = "assets/prompts"
characters_file = "assets/devices/characters.txt"
environments_file = "assets/devices/environments.txt"
output_file = "selected_story.txt"

# Select random prompt and replace placeholders, then save to file
try:
    select_random_prompt_and_replace(prompt_dir, characters_file, environments_file, output_file)
    print(f"Modified prompt saved to {output_file}")
except FileNotFoundError as e:
    print(e)
