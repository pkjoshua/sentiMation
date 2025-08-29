# SentiMation Web Application

A modern web interface for scheduling and managing AI-powered animation generation tasks using Stable Diffusion and AnimateDiff.

## Features

### 🎯 **Dashboard**
- Real-time task monitoring with status indicators
- Task statistics (Total, Pending, Completed, Failed)
- Interactive task table with sorting and filtering
- Auto-refresh every 30 seconds

### 📅 **Task Scheduling**
- Schedule generation tasks for future execution
- **🚀 Run Now** - Execute tasks immediately from schedule page or dashboard
- **Recurring tasks** with weekly schedule support
- Support for both Music and Scenario generators
- **Specific activity selection** from available prompts
- **🎲 Random activity selection** for variety
- DateTime picker for precise scheduling

### 🎬 **Generation Management**
- View detailed task information
- Cancel pending tasks
- Download generated videos
- Real-time status updates

### 🎨 **Modern UI**
- Responsive Bootstrap 5 design
- Font Awesome icons
- Smooth animations and transitions
- Mobile-friendly interface

## Quick Start

### 1. Start the Host Service (Windows)
```bash
# Run as Administrator in PowerShell
cd scripts/win
.\host_service.ps1
```

The host service will start listening on `http://+:7070/` for job requests.

### 2. Start the Web Application

```bash
# From the project root directory
./start_webapp.sh

# Or manually
cd webapp
python app.py
```

### 2. Access the Interface

Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Schedule Your First Generation

1. Click "Schedule New Generation" on the dashboard
2. Select a generator type (Music or Scenario)
3. Choose an activity from the available prompts:
   - **🎲 Random Activity**: A random activity will be selected when the task runs
   - **Specific Activities**: Choose a particular activity (e.g., "Guitar", "Cooking", "Piano", "Dancing")
4. Choose between one-time or recurring schedule:
   - **One-time**: Set a specific date and time
   - **Recurring**: Select days of the week and time
5. **Run Options**:
   - **🚀 Run Now**: Click "Run Now" to execute immediately
   - **📅 Schedule**: Click "Schedule Task" to run at the specified time

## API Endpoints

### Task Management
- `GET /` - Dashboard page
- `GET /schedule` - Schedule generation form
- `POST /schedule` - Create new scheduled task
- `GET /tasks` - Get all tasks (JSON)
- `GET /task/<task_id>` - Get specific task details
- `GET /cancel/<task_id>` - Cancel a pending task
- `GET /run_now/<task_id>` - Run a pending task immediately

### Host Service
- `GET /host-service/status` - Check host service availability and configuration

### Generator Information
- `GET /generators` - Get available generators (JSON)

## Configuration

### Host Service Integration
The web app integrates with a Windows host service for job scheduling and execution:

- **Host Service URL**: `http://host.docker.internal:7070` (default)
- **Endpoints**:
  - `POST /schedule` - Schedule jobs with Windows Task Scheduler
  - `POST /run-now` - Execute jobs immediately

The host service handles:
- Docker container execution
- Windows Task Scheduler integration
- Job logging and monitoring
- Automatic retry logic

**Setup**: Run `scripts/win/host_service.ps1` as Administrator on Windows.

### Stable Diffusion API
The web app connects to Stable Diffusion WebUI at:
```
http://127.0.0.1:7860/sdapi/v1/img2img
```

Make sure Stable Diffusion WebUI is running with the `--api` flag.

### Generation Settings
- **Video Length**: 150 frames (7.5 seconds)
- **Resolution**: 360x640 (portrait)
- **FPS**: 20
- **Model**: animatediffMotion_v15V2.ckpt
- **Sampler**: DPM++ 2M Karras
- **Steps**: 20
- **CFG Scale**: 10

## File Structure

```
webapp/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard page
│   └── schedule.html     # Schedule form
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── app.js        # JavaScript functionality
│   └── generated/        # Generated videos (created automatically)
└── README.md            # This file
```

## Testing

### Host Service Integration
Test the host service integration using the provided test script:

```bash
cd webapp
python test_host_service.py
```

This will test:
- Connection to the host service
- Job creation and specification
- Job scheduling
- Immediate job execution

### Manual Testing
1. Start the host service on Windows
2. Start the web application
3. Check host service status: `GET /host-service/status`
4. Create a scheduled job
5. Test immediate execution with "Run Now"

## Development

### Prerequisites
- Python 3.8+
- Flask 2.3+
- Stable Diffusion WebUI with API enabled

### Installation
```bash
pip install flask
```

### Running in Development Mode
```bash
cd webapp
export FLASK_ENV=development
python app.py
```

### Logging
The application logs to `webapp.log` in the webapp directory.

## Troubleshooting

### Common Issues

1. **"API call failed" errors**
   - Ensure Stable Diffusion WebUI is running with `--api` flag
   - Check that the API URL is correct in `app.py`

2. **"No controlnet images found" errors**
   - Make sure you have images in `generators/[type]/assets/init/`
   - Check file permissions

3. **Web app won't start**
   - Check if port 5000 is available
   - Ensure Flask is installed: `pip install flask`

4. **Generated videos not showing**
   - Check that `webapp/static/generated/` directory exists
   - Verify file permissions

### Logs
Check the application logs:
```bash
tail -f webapp/webapp.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project uses the same license as the underlying SentiMation components. 