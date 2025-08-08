#!/usr/bin/env python3
"""
Custom selector that uses webapp-provided selections instead of random selection
"""
import os
import sys
import json
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def read_file_lines(file_path):
    """Read lines from a file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def get_character_by_name(character_name, characters_file="assets/devices/characters.txt"):
    """Get character details by name"""
    characters = read_file_lines(characters_file)
    for character_line in characters:
        character_parts = character_line.split(',')
        if len(character_parts) >= 4 and character_parts[0].strip() == character_name:
            return {
                'name': character_parts[0].strip(),
                'lora': character_parts[1].strip(),
                'activator': character_parts[2].strip(),
                'quote_directory': character_parts[3].strip()
            }
    return None

def get_environment_by_name(environment_name, environments_file="assets/devices/environments.txt"):
    """Get environment details by name"""
    environments = read_file_lines(environments_file)
    for env_line in environments:
        env_parts = env_line.split(',')
        if len(env_parts) >= 1 and env_parts[0].strip() == environment_name:
            return {
                'name': env_parts[0].strip(),
                'lora': env_parts[1].strip() if len(env_parts) > 1 else ''
            }
    return None

def get_quote_from_character(character_quote_directory, quotes_dir="assets/quotes"):
    """Get a specific quote from a character's quote directory"""
    quote_dir = os.path.join(quotes_dir, character_quote_directory)
    if not os.path.exists(quote_dir):
        raise FileNotFoundError(f"No quote directory found for: {character_quote_directory}")

    quote_files = [os.path.join(quote_dir, f) for f in os.listdir(quote_dir) if f.endswith('.txt')]
    if not quote_files:
        raise FileNotFoundError(f"No quote files found in directory: {quote_dir}")
    
    # For now, take the first quote file. Could be enhanced to select specific quotes
    selected_quote_file = quote_files[0]
    quote_lines = read_file_lines(selected_quote_file)
    logging.info(f"Selected quote from directory '{character_quote_directory}': {quote_lines[0]}")
    return "\n".join(quote_lines[:2])

def get_prompt_content(prompt_name, prompt_dir="assets/prompts"):
    """Get prompt content by name"""
    prompt_file_path = os.path.join(prompt_dir, f"{prompt_name}.txt")
    if not os.path.exists(prompt_file_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
    
    return read_file_lines(prompt_file_path)

def create_custom_prompt(character_name, environment_name, prompt_name, output_file="prompt.txt"):
    """Create a custom prompt using user selections"""
    try:
        # Get character details
        character = get_character_by_name(character_name)
        if not character:
            raise ValueError(f"Character not found: {character_name}")
        
        # Get environment details
        environment = get_environment_by_name(environment_name)
        if not environment:
            raise ValueError(f"Environment not found: {environment_name}")
        
        # Get prompt content
        prompt_lines = get_prompt_content(prompt_name)
        
        # Get quote for the character
        quote = get_quote_from_character(character['quote_directory'])
        quote_lines = quote.split('\n')
        formatted_quote = f'"{quote_lines[0]}"\n-{quote_lines[1]}' if len(quote_lines) > 1 else f'"{quote}"'
        
        # Save the formatted quote
        with open('selected_quote.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_quote)
        
        # Replace placeholders in prompt
        with open(output_file, 'w', encoding='utf-8') as file:
            for prompt in prompt_lines:
                modified_prompt = prompt.replace("[CHARACTER]", character['name'])
                modified_prompt = modified_prompt.replace("[ENVIRONMENT]", environment['name'])
                modified_prompt = modified_prompt.replace("[LORA]", character['lora']) if character['lora'] else modified_prompt.replace("[LORA]", '')
                modified_prompt = modified_prompt.replace("[ACTIVATOR]", character['activator']) if character['activator'] else modified_prompt.replace("[ACTIVATOR]", '')
                file.write(f"{modified_prompt}\n\n")
        
        logging.info(f"Custom prompt created with Character: {character_name}, Environment: {environment_name}, Prompt: {prompt_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error creating custom prompt: {e}")
        return False

def main():
    """Main execution - reads parameters from command line or config file"""
    # Check if parameters are provided via command line
    if len(sys.argv) >= 4:
        character_name = sys.argv[1]
        environment_name = sys.argv[2]
        prompt_name = sys.argv[3]
    else:
        # Check for parameters file (created by webapp)
        params_file = "custom_params.json"
        if os.path.exists(params_file):
            with open(params_file, 'r') as f:
                params = json.load(f)
            character_name = params.get('character')
            environment_name = params.get('environment')
            prompt_name = params.get('prompt')
        else:
            logging.error("No parameters provided. Use: python selector.py <character> <environment> <prompt>")
            print("Error: No parameters provided")
            return False
    
    success = create_custom_prompt(character_name, environment_name, prompt_name)
    if success:
        print(f"Custom prompt created successfully with {character_name}, {environment_name}, {prompt_name}")
    else:
        print("Failed to create custom prompt")
    
    return success

if __name__ == "__main__":
    main()