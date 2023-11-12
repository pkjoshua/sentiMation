import random
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='hypnotic_log.log', level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to generate a psychedelic prompt
def generate_psychedelic_prompt():
    prompts = [
        """Psychedelic landscape in Alex Grey's style, vibrant and transcendent, ultra-detailed, luminous colors, 8k resolution
        0: (purple:1.5), (mellow:1.2)
        30: (orange:1.5), (vibrant:1.2)
        60: (turquoise:1.5), (calm:1.2)
        90: (magenta:1.5), (energetic:1.2)
        120:(lime:1.5), (mellow:1.2)""",
        """Surreal visuals in the style of Salvador Dali, transformed into psychedelic art, ultra-sharp, dreamlike, 8k
        0: (indigo:1.4), (slow:1.6)
        30: (scarlet:1.4), (quick:1.6)
        60: (emerald:1.4), (steady:1.6)
        90: (gold:1.4), (rapid:2)
        120:(violet:1.4), (slow:2)""",
        """Psychedelic patterns in Amanda Sage's visionary style, full of symbolism, deep colors, high contrast, 8k
        0: (cyan:1.7), (intense:1.4)
        30: (ruby:1.7), (gentle:1.4)
        60: (jade:1.7), (dynamic:1.4)
        90: (amber:1.7), (subtle:1.4)
        120:(sapphire:1.7), (intense:1.4)""",
        """Abstract hallucinatory art in the style of James R. Eads, fluid and morphing, vibrant, 8k, high dynamic range
        0: (rose:1.3), (expanding:1.5)
        30: (azure:1.3), (contracting:1.5)
        60: (chartreuse:1.3), (swirling:1.5)
        90: (sienna:1.3), (flowing:1.5)
        120:(lavender:1.3), (expanding:1.5)""",
        """Phantasmagoric scenes in the style of Zdzisław Beksiński, psychedelic twist, dark yet vibrant, ultra HD
        0: (burgundy:1.2), (warping:1.6)
        30: (cerulean:1.2), (steady:1.6)
        60: (ochre:1.2), (twisting:1.6)
        90: (veridian:1.2), (calming:1.6)
        120:(plum:1.2), (warping:1.6)"""
    ]
    chosen_prompt = random.choice(prompts)
    logging.info(f"Chosen prompt: {chosen_prompt}")
    return chosen_prompt

# Generate the chosen prompt
chosen_prompt = generate_psychedelic_prompt()

# Write the chosen prompt to a file
with open("chosen_prompt.txt", "w") as file:
    file.write(chosen_prompt)
