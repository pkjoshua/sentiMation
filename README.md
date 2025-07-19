# SentiMation



An AI-powered animation generation tool that creates short animations of characters in various scenarios using Stable Diffusion and AnimateDiff. This can be run on the windows system or from a container. 

## Overview

SentiMation allows you to generate short animations of your favorite characters playing instruments, cooking, reading, painting, and more. The tool uses Stable Diffusion WebUI with AnimateDiff to create high-quality animated content.

## Prerequisites

### 1. Stable Diffusion WebUI
You need to have [AUTOMATIC1111's Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) installed and running.

### 2. AnimateDiff Extension
Install the [AnimateDiff extension](https://github.com/continue-revolution/sd-webui-animatediff) for Stable Diffusion WebUI. This is required for animation generation.

### 3. API Access
Enable the API in Stable Diffusion WebUI by adding `--api` to your launch parameters. See the [API documentation](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API/06c7b7e499e8b2345272d09cd565c21f937ebc6b) for more details.

## Setup Instructions

### 1. Model Installation

#### Stable Diffusion Models
- Download models from [CivitAI](https://civitai.com/)
- Place models in: `.\stable-diffusion-webui\models\Stable-diffusion\`
- **⚠️ Warning**: CivitAI contains many NSFW models. Be careful when browsing and downloading.

#### LoRA Models
- Download the LoRA models referenced in your character Excel files
- Place LoRA models in: `.\stable-diffusion-webui\models\Lora\`

#### AnimateDiff Models
- Download AnimateDiff models and place them in the AnimateDiff models directory
- `animatediffMotion_v15V2.ckpt` is the default model used by this tool

### 2. Directory Structure
```
sentiMation/
├── generators/
│   ├── music/          # Music generator (characters playing instruments)
│   └── scenario/       # Scenario generator (cooking, reading, painting, etc.)
├── scripts/
│   └── win/           # Windows task scheduler scripts
└── old/               # Legacy generators (terminal-based)
```

## Available Generators

### Music Generator
Creates animations of characters playing various instruments:
- Guitar, Piano, Violin, Drums, Bass
- Flute, Saxophone, Trumpet, Harp
- Accordion, Ukulele, Cello, Clarinet
- Harmonica, Banjo

**Environments**: Concert halls, music studios, jazz clubs, outdoor stages, etc.

### Scenario Generator
Creates animations of characters in various activities:
- Cooking, Reading, Painting, Gardening
- Exercising, Studying, Dancing, Photography
- Writing, Meditation

**Environments**: Kitchens, libraries, studios, gardens, gyms, etc.

## Usage

### 1. Prepare Your Data
- Update character information in `assets/devices/characters.xlsx`
- Add controlnet images to `assets/init/` directory
- Add character quotes to `assets/quotes/[Series_Name]/` directories

### 2. Run the Generator
```bash
# Navigate to your chosen generator
cd generators/music  # or generators/scenario

# Generate prompts and quotes
python selector.py

# Create animations
python generator.py
```

### 3. Windows Automation
Use the task scheduler scripts in `scripts/win/` to automate generation on Windows.

## Web Interface (Optional)

### Current Status
The project includes a `webapp/` directory for future web interface development. Currently, the main functionality is accessed through the command-line generators.

### Planned UI Features
- Web-based interface for generator selection
- Real-time generation status monitoring
- Batch generation management
- Result preview and download
- Character and prompt management

### Running the Web Interface (When Available)
```bash
# Navigate to the webapp directory
cd webapp

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the web server
python app.py

# Access the interface at http://localhost:5000
```

### Alternative: Gradio Interface
For users who prefer a graphical interface, there's a Gradio-based script available in `scripts/test/multi_frame_josh.py` that integrates with Stable Diffusion WebUI.

## File Structure

### Character Data Format
The `characters.xlsx` file should contain:
- **Character**: Character name
- **Series**: Anime/manga series
- **Lora**: LoRA model name
- **Activator**: LoRA activator token

### Prompt Format
Prompts use placeholders that get replaced:
- `[CHARACTER]`: Character name from Excel
- `[ENVIRONMENT]`: Random environment from environments.txt
- `[LORA]`: Character's LoRA model
- `[ACTIVATOR]`: Character's activator token

### Quote Format
Quotes are stored in text files with format:
```
Quote text
Character name
```

## Configuration

### Generator Settings
- **Video Length**: 150 frames (7.5 seconds at 20fps)
- **Resolution**: 360x640 (portrait)
- **Model**: animatediffMotion_v15V2.ckpt (default)
- **Sampler**: DPM++ 2M Karras
- **Steps**: 20
- **CFG Scale**: 10

### API Configuration
- **URL**: http://127.0.0.1:7860/sdapi/v1/img2img
- **Batch Size**: 1
- **Denoising Strength**: 0.9

## Troubleshooting

### Common Issues
1. **API Connection Failed**: Ensure Stable Diffusion WebUI is running with `--api` flag
2. **Model Not Found**: Check that AnimateDiff models are in the correct directory
3. **LoRA Errors**: Verify LoRA models are downloaded and placed in the Lora folder
4. **Memory Issues**: Reduce batch size or video length for lower VRAM usage

### Performance Tips
- Use smaller models for faster generation
- Reduce video length for quicker results
- Close other applications to free up VRAM
- Use SSD storage for faster file operations

## Legacy Generators

The `old/` directory contains previous versions of generators that were managed via terminal. These require manual input of MP4 videos and images but perform the same functions as the current generators.

## Contributing

Feel free to:
- Add new scenarios and prompts
- Improve character data
- Create new environment lists
- Optimize generation parameters

## License

This project uses the same license as the underlying Stable Diffusion and AnimateDiff components.

## Acknowledgments

- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for Stable Diffusion WebUI
- [continue-revolution](https://github.com/continue-revolution/sd-webui-animatediff) for the AnimateDiff extension
- [CivitAI](https://civitai.com/) for model hosting
- The Stable Diffusion and AnimateDiff communities for their contributions

