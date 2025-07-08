# sentiMation

sentiMation contains a set of generators that produce short videos using the Automatic1111 API. Each generator under the `generators` folder is tailored to a specific style of content. Windows PowerShell scripts are provided to schedule runs via Task Scheduler.

## Features

- Python scripts for interacting with the Automatic1111 txt2img and img2img endpoints.
- Optional notifications through Pushover using `PUSHOVER_API` and `PUSHOVER_USER` environment variables.
- Example test utilities for experimenting with ControlNet and video generation.
- Windows scripts in `scripts/win` to automate content creation.

## Usage

1. Clone the repository and install dependencies.
2. Ensure the Automatic1111 API is running.
3. Run a generator manually:

```bash
python generators/dogshow/call.py
```

4. Set environment variables for notifications if desired:

```bash
PUSHOVER_API=<your api token>
PUSHOVER_USER=<your user key>
```

5. On Windows, edit the `$repoPath` variable in any `.ps1` script to point to your local clone. These scripts can be scheduled via Task Scheduler to automate generation.

## Notes

Default paths and user names have been replaced with placeholders. Replace any `C:\path\to\...` entries with values appropriate for your environment before running.
