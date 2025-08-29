# Scenario Generator

This generator creates short animations of characters in various scenarios (cooking, reading, painting, gardening, exercising, studying, dancing, photography, writing, meditation).

## Setup

1. **Controlnet Images**: Place your controlnet images in `assets/init/` directory
2. **Characters**: Update `assets/devices/characters.xlsx` with your character data
3. **Environments**: The `assets/devices/environments.txt` file contains various environments
4. **Prompts**: Various scenario prompts are available in `assets/prompts/`
5. **Quotes**: Add character quotes in `assets/quotes/[Series_Name]/` directories

## Usage

1. Run the selector to generate prompts:
   ```bash
   python selector.py
   ```

2. Run the generator to create animations:
   ```bash
   python generator.py
   ```

## File Structure

```
scenario/
├── assets/
│   ├── devices/
│   │   ├── characters.xlsx
│   │   └── environments.txt
│   ├── prompts/
│   │   ├── cooking.txt
│   │   ├── reading.txt
│   │   ├── painting.txt
│   │   ├── gardening.txt
│   │   ├── exercising.txt
│   │   ├── studying.txt
│   │   ├── dancing.txt
│   │   ├── photography.txt
│   │   ├── writing.txt
│   │   └── meditation.txt
│   ├── quotes/
│   │   ├── Naruto/
│   │   ├── One_Piece/
│   │   └── Dragon_Ball/
│   ├── init/
│   └── generations/
├── generator.py
├── selector.py
└── README.md
```

## Prompt Format

Each prompt file contains placeholders:
- `[CHARACTER]`: Character name from characters.xlsx
- `[ENVIRONMENT]`: Random environment from environments.txt
- `[LORA]`: Character's LoRA from characters.xlsx
- `[ACTIVATOR]`: Character's activator from characters.xlsx

## Adding New Scenarios

1. Create a new prompt file in `assets/prompts/`
2. Use the placeholder format: `[CHARACTER] [action] in a [ENVIRONMENT], [LORA], [ACTIVATOR], [additional keywords]`
3. Add relevant keywords for the scenario

## Adding New Environments

Edit `assets/devices/environments.txt` and add new environments in the format:
```
Environment Name,environment_lora
``` 