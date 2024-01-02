import os
import random
import logging
import pandas as pd

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define file paths
excel_file_path = "assets/devices/characters.xlsx"
environments_file_path = "assets/devices/environments.txt"
prompt_dir_path = "assets/prompts"  # Update this path as per your directory structure

def read_file_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def select_random_character_and_series(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    selected_row = df.sample().iloc[0]
    character_name = selected_row['Character']
    lore = selected_row['Lora']
    activator = selected_row['Activator']
    series_name = selected_row['Series']
    logging.info(f"Selected character: {character_name}, Series: {series_name}")
    return character_name, lore, activator, series_name

def select_random_word(file_path):
    words = read_file_lines(file_path)
    word_info = random.choice(words)
    word_parts = word_info.split(',')
    selected_word = word_parts[0].strip()
    word_lora = word_parts[1].strip() if len(word_parts) > 1 else ''
    return selected_word, word_lora

def select_random_quote_from_series(series_name, quotes_dir):
    series_dir = os.path.join(quotes_dir, series_name)
    if not os.path.exists(series_dir):
        raise FileNotFoundError(f"No quote directory found for series: {series_name}")

    quote_files = [os.path.join(series_dir, f) for f in os.listdir(series_dir) if f.endswith('.txt')]
    selected_quote_file = random.choice(quote_files)
    quote_lines = read_file_lines(selected_quote_file)
    logging.info(f"Selected quote from series '{series_name}': {quote_lines[0]}")
    return "\n".join(quote_lines[:2]) 

def select_random_prompt_and_replace(prompt_dir, character_name, character_lora, character_activator, environments_file, output_file):
    prompt_files = [f for f in os.listdir(prompt_dir) if f.endswith('.txt')]
    selected_prompt_file = random.choice(prompt_files)
    prompt_file_path = os.path.join(prompt_dir, selected_prompt_file)

    selected_environment = select_random_word(environments_file)[0]
    prompt_lines = read_file_lines(prompt_file_path)

    with open(output_file, 'w', encoding='utf-8') as file:
        for prompt in prompt_lines:
            modified_prompt = prompt.replace("[CHARACTER]", character_name)
            modified_prompt = modified_prompt.replace("[ENVIRONMENT]", selected_environment)
            modified_prompt = modified_prompt.replace("[LORA]", character_lora) if character_lora else modified_prompt.replace("[LORA]", '')
            modified_prompt = modified_prompt.replace("[ACTIVATOR]", character_activator) if character_activator else modified_prompt.replace("[ACTIVATOR]", '')
            file.write(f"{modified_prompt}\n\n")


def save_quote(quote, output_file='selected_quote.txt'):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(quote)

# Main execution
try:
    output_file = "prompt.txt"
    character_name, lore, activator, series_name = select_random_character_and_series(excel_file_path)

    # Select a random quote from the series-specific directory
    quote = select_random_quote_from_series(series_name, 'assets/quotes')

    # Split the quote into lines and format it
    quote_lines = quote.split('\n')
    formatted_quote = f'"{quote_lines[0]}"\n{quote_lines[1]}' if len(quote_lines) > 1 else f'"{quote}"'
    
    # Save the formatted quote
    save_quote(formatted_quote)

    # Select a random prompt, replace placeholders, and save it
    select_random_prompt_and_replace(prompt_dir_path, character_name, lore, activator, environments_file_path, output_file)
    
    # Confirmation message
    print(f"Modified prompt and quote saved to {output_file} and selected_quote.txt respectively.")
except Exception as e:
    print(e)



