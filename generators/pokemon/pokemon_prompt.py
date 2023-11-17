import random
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='pokemon_log.log', level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to generate a psychedelic prompt
def generate_psychedelic_prompt():
    prompts = [
        textwrap.dedent("""\
         Psychedelic landscape in Alex Grey's style, vibrant and transcendent, ultra-detailed, luminous colors, 8k resolution
        0: (purple:1.5), (mellow:1.8)
        1: (orange:1.5), (vibrant:1.8)
        3: (turquoise:1.5), (calm:1.8)
        5: (magenta:1.5), (energetic:1.8)
        10:(lime:1.5), (mellow:1.8)
        13:(black:1.5), (slow:1.8)"""),
        textwrap.dedent("""\
        Surreal visuals in the style of Salvador Dali, transformed into psychedelic art, ultra-sharp, dreamlike, 8k
        0: (purple:1.5), (mellow:1.8)
        1: (orange:1.5), (vibrant:1.8)
        4: (turquoise:1.5), (calm:1.8)
        8: (magenta:1.5), (energetic:1.8)
        12:(lime:1.5), (mellow:1.8)
        14:(black:1.5), (slow:1.8)"""),
        textwrap.dedent("""\
        (human eye:1.3), Psychedelic patterns in Amanda Sage's visionary style, full of symbolism, deep colors, high contrast, 8k
        0: (purple:1.5), (mellow:1.8)
        1: (orange:1.5), (vibrant:1.8)
        4: (turquoise:1.5), (calm:1.8)
        8: (magenta:1.5), (energetic:1.8)
        12:(lime:1.5), (mellow:1.8)
        14:(black:1.5), (slow:1.8)"""),
        textwrap.dedent("""\
         Abstract hallucinatory art in the style of James R. Eads, fluid and morphing, vibrant, 8k, high dynamic range
        0: (purple:1.5), (mellow:1.8)
        1: (orange:1.5), (vibrant:1.8)
        4: (turquoise:1.5), (calm:1.8)
        8: (magenta:1.5), (energetic:1.8)
        12:(lime:1.5), (mellow:1.8)
        14:(black:1.5), (slow:1.8)"""),
        textwrap.dedent("""\
        Phantasmagoric scenes in the style of Zdzisław Beksiński, psychedelic twist, dark yet vibrant, ultra HD
        0: (purple:1.5), (mellow:1.8)
        1: (orange:1.5), (vibrant:1.8)
        4: (turquoise:1.5), (calm:1.8)
        8: (magenta:1.5), (energetic:1.8)
        12:(lime:1.5), (mellow:1.8)
        14:(black:1.5), (slow:1.8)""")
    ]
    chosen_prompt = random.choice(prompts)
    logging.info(f"Chosen prompt: {chosen_prompt}")
    return chosen_prompt


# Generate the chosen prompt
chosen_prompt = generate_psychedelic_prompt()

# Write the chosen prompt to a file
with open("chosen_prompt.txt", "w") as file:
    file.write(chosen_prompt)
