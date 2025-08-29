# Host Service Integration Summary

This document summarizes the changes made to integrate the SentiMation webapp with the Windows host service for job scheduling and execution.

## Changes Made

### 1. Updated Host Service Script (`scripts/win/host_service.ps1`)

**Added `/run-now` endpoint:**
- New function `Execute-JobImmediately` for immediate job execution
- Creates temporary PowerShell scripts for immediate execution
- Returns log file path and exit code
- Enhanced error handling with proper JSON responses

**Enhanced error handling:**
- Better error messages in JSON format
- Proper HTTP status codes
- Graceful error handling for all endpoints

### 2. New Host Scheduler Client (`webapp/host_scheduler_client.py`)

**Core Classes:**
- `JobStep`: Represents individual job steps with Docker arguments, timeouts, and retry logic
- `JobSpec`: Complete job specification including task name, steps, environment variables, and scheduling time
- `HostSchedulerClient`: Main client for communicating with the host service

**Key Features:**
- Automatic fallback to local execution if host service is unavailable
- Comprehensive error handling and logging
- Support for both scheduled and immediate job execution
- Factory function for creating generator-specific job steps

**Methods:**
- `schedule_job()`: Schedule jobs with Windows Task Scheduler
- `run_job_now()`: Execute jobs immediately
- `is_available()`: Check host service connectivity

### 3. Updated Web Application (`webapp/app.py`)

**Enhanced GenerationTask class:**
- Added host service integration fields: `host_script_path`, `host_log_path`, `host_exit_code`

**Updated job scheduling:**
- All new jobs now go through the host service first
- Automatic fallback to local scheduling if host service is unavailable
- Enhanced logging for host service operations

**Updated immediate execution:**
- `run_now` endpoint now uses host service for immediate execution
- Fallback to local execution if host service fails
- Returns host service log path and exit code

**New API endpoint:**
- `GET /host-service/status`: Check host service availability and configuration

### 4. Configuration Updates (`webapp/config.py`)

**Added host service configuration:**
- `HOST_SERVICE_URL`: Configurable host service endpoint (default: `http://host.docker.internal:7070`)
- Environment variable support for customization

### 5. Dependencies and Testing

**New requirements:**
- `requests` library for HTTP communication with host service
- Updated `requirements.txt` with all necessary dependencies

**Testing:**
- `test_host_service.py`: Comprehensive test script for host service integration
- Tests connection, job creation, scheduling, and immediate execution

**Startup script:**
- `start_webapp.sh`: Automated startup script with dependency installation

## Integration Flow

### Job Scheduling
1. User creates scheduled job in webapp
2. Webapp creates `JobSpec` with appropriate steps
3. Webapp calls host service `/schedule` endpoint
4. Host service generates PowerShell script and registers with Windows Task Scheduler
5. Webapp stores host service response (script path) for tracking
6. If host service fails, webapp falls back to local scheduling

### Immediate Execution
1. User clicks "Run Now" for a task
2. Webapp creates `JobSpec` without time parameter
3. Webapp calls host service `/run-now` endpoint
4. Host service executes job immediately and returns log path
5. Webapp updates task status and stores log path
6. If host service fails, webapp falls back to local execution

### Fallback Behavior
- **Host service unavailable**: Automatic fallback to local execution
- **Host service errors**: Logged and fallback to local execution
- **Network issues**: Graceful degradation with clear error messages

## Benefits

1. **Centralized Job Management**: All jobs go through Windows host service
2. **Better Resource Management**: Host service handles Docker and Windows integration
3. **Improved Reliability**: Automatic fallback ensures webapp continues working
4. **Enhanced Monitoring**: Host service provides detailed logging and execution tracking
5. **Windows Integration**: Proper integration with Windows Task Scheduler
6. **Scalability**: Host service can handle multiple concurrent jobs

## Usage

### Starting the System
1. **Windows**: Run `scripts/win/host_service.ps1` as Administrator
2. **Webapp**: Run `./start_webapp.sh` or `python app.py`

### Testing Integration
```bash
cd webapp
python test_host_service.py
```

### Checking Status
```bash
curl http://localhost:5000/host-service/status
```

## Troubleshooting

### Common Issues
1. **Host service not available**: Check if PowerShell script is running as Administrator
2. **Connection refused**: Verify host service is listening on port 7070
3. **Docker not found**: Ensure Docker Desktop is running on Windows
4. **Permission denied**: Run host service as Administrator

### Debug Steps
1. Check host service logs in PowerShell
2. Verify webapp logs in `webapp.log`
3. Test host service connectivity manually
4. Check Windows Task Scheduler for registered tasks

## Future Enhancements

1. **Job Status Monitoring**: Real-time status updates from host service
2. **Log Streaming**: Live log viewing for running jobs
3. **Job Cancellation**: Cancel running jobs through host service
4. **Resource Management**: Monitor and limit concurrent job execution
5. **Advanced Scheduling**: Support for cron-like expressions and dependencies
