# AI Video Scheduler Web App

A beautiful, interactive web interface for scheduling AI video generation tasks on your GPU.

## Features

### 🎨 Modern Dark Rainbow Theme
- Beautiful gradient backgrounds with rainbow animations
- Glassmorphism design elements
- Responsive design that works on all devices
- Smooth animations and hover effects

### ⏰ Human-Readable Scheduling
Instead of confusing cron syntax, the app now offers intuitive scheduling options:
- **Daily**: Run every day at a specific time
- **Weekly**: Run on selected days of the week at a specific time
- **Monthly**: Run on a specific day each month
- **Interval**: Run every X minutes
- **Custom**: Advanced cron expressions for power users

### 🎮 GPU Management
- Visual indicators for GPU availability
- Space for displaying generated images/videos
- Status tracking for active jobs
- Easy job management with delete functionality

### 🔔 Interactive Features
- Real-time flash messages for user feedback
- Confirmation dialogs for destructive actions
- Loading states for better UX
- Auto-hiding notifications
- Hover effects and animations

### 📊 Dashboard Statistics
- Active job count
- Notification-enabled jobs
- Unique generator types
- GPU status indicator

## Usage

1. **View Jobs**: The main page shows all scheduled jobs with human-readable schedules
2. **Add Job**: Click "Add New Job" to create a new scheduled task
3. **Delete Job**: Click the delete button on any job card to remove it
4. **Monitor**: Watch the dashboard for real-time updates

## Technical Details

- **Backend**: Flask with Python
- **Frontend**: Modern HTML5, CSS3, and JavaScript
- **Scheduling**: Cron-based with human-readable conversion
- **Storage**: JSON-based job storage
- **API**: RESTful endpoints for future integrations

## API Endpoints

- `GET /api/jobs` - Get all jobs
- `GET /api/generators` - Get available generators
- `GET /api/status` - Get system status

## Development

To run the development server:

```bash
cd webapp
python app.py
```

The app will be available at `http://localhost:5000`

## Future Enhancements

- Real-time job execution monitoring
- Image/video preview galleries
- Advanced scheduling options
- Mobile app integration
- Webhook notifications
- Job templates and presets 