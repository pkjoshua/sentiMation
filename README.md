# sentiMation

sentiMation contains several generators that produce short videos using the Automatic1111 API. Each generator under `generators/` implements a particular style of content. The project now runs in a Docker container and exposes a small web UI for scheduling jobs using cron.

## Features

- Python scripts for interacting with the Automatic1111 txt2img and img2img endpoints.
- Optional Pushover notifications using the `PUSHOVER_API` and `PUSHOVER_USER` environment variables.
- Simple Flask web application to schedule generator jobs.
- Docker container with cron so jobs run even when the UI is not open.

## Usage

1. Build and start the container:
   ```bash
   docker compose up --build
   ```
   Add `--gpus all` if running on a system with NVIDIA GPUs.
2. Open `http://localhost:5000` to access the scheduler UI.
3. Create a job by choosing a generator, entering a cron expression and optionally enabling Pushover notifications.
4. Jobs are stored in `jobs.json` and executed by cron inside the container.

Manual execution is still possible via:
```bash
python job_runner.py <generator> [--notify]
```

## Notes

Default paths and user names have been replaced with placeholders. Replace any `C:\path\to\...` entries with values appropriate for your environment before running.
