// SentiMation Web Application JavaScript

// Global variables
let refreshInterval;

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
}

function formatRelativeTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge bg-warning"><i class="fas fa-clock me-1"></i>Pending</span>',
        'running': '<span class="badge bg-info"><i class="fas fa-spinner fa-spin me-1"></i>Running</span>',
        'completed': '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Completed</span>',
        'failed': '<span class="badge bg-danger"><i class="fas fa-exclamation-triangle me-1"></i>Failed</span>',
        'cancelled': '<span class="badge bg-secondary"><i class="fas fa-ban me-1"></i>Cancelled</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

// API functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Task management functions
async function loadTasks() {
    try {
        const tasks = await apiCall('/tasks');
        updateDashboardStats(tasks);
        updateTasksTable(tasks);
        return tasks;
    } catch (error) {
        showNotification('Failed to load tasks', 'danger');
        console.error('Error loading tasks:', error);
    }
}

function updateDashboardStats(tasks) {
    const total = tasks.length;
    const pending = tasks.filter(t => t.status === 'pending').length;
    const completed = tasks.filter(t => t.status === 'completed').length;
    const failed = tasks.filter(t => t.status === 'failed').length;
    const running = tasks.filter(t => t.status === 'running').length;
    
    const elements = {
        'total-tasks': total,
        'pending-tasks': pending,
        'completed-tasks': completed,
        'failed-tasks': failed
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    // Add running tasks indicator if there are any
    const runningIndicator = document.getElementById('running-tasks');
    if (runningIndicator) {
        runningIndicator.textContent = running;
        runningIndicator.style.display = running > 0 ? 'block' : 'none';
    }
}

function updateTasksTable(tasks) {
    const tbody = document.getElementById('tasks-tbody');
    const noTasks = document.getElementById('no-tasks');
    
    if (!tbody) return;
    
    if (tasks.length === 0) {
        tbody.innerHTML = '';
        if (noTasks) {
            noTasks.style.display = 'block';
        }
        return;
    }
    
    if (noTasks) {
        noTasks.style.display = 'none';
    }
    
    tbody.innerHTML = tasks.map(task => `
        <tr class="fade-in">
            <td><code>${task.id}</code></td>
            <td>
                <span class="badge bg-info">
                    <i class="fas fa-cog me-1"></i>
                    ${task.generator_type}
                </span>
            </td>
            <td>
                <div class="text-truncate" style="max-width: 200px;" title="${task.prompt}">
                    ${task.prompt}
                </div>
            </td>
            <td>
                <div title="${formatDateTime(task.scheduled_time)}">
                    ${formatRelativeTime(task.scheduled_time)}
                </div>
            </td>
            <td>${getStatusBadge(task.status)}</td>
            <td>
                <div title="${formatDateTime(task.created_at)}">
                    ${formatRelativeTime(task.created_at)}
                </div>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewTask('${task.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${task.status === 'pending' ? `
                        <button class="btn btn-outline-danger" onclick="cancelTask('${task.id}')" title="Cancel Task">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                    ${task.status === 'completed' && task.result_path ? `
                        <button class="btn btn-outline-success" onclick="downloadVideo('${task.result_path}')" title="Download Video">
                            <i class="fas fa-download"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

async function viewTask(taskId) {
    try {
        const task = await apiCall(`/task/${taskId}`);
        showTaskModal(task);
    } catch (error) {
        showNotification('Failed to load task details', 'danger');
        console.error('Error loading task details:', error);
    }
}

function showTaskModal(task) {
    const modalBody = document.getElementById('task-modal-body');
    if (!modalBody) return;
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Task Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>ID:</strong></td><td><code>${task.id}</code></td></tr>
                    <tr><td><strong>Generator:</strong></td><td>${task.generator_type}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>${getStatusBadge(task.status)}</td></tr>
                    <tr><td><strong>Scheduled:</strong></td><td>${formatDateTime(task.scheduled_time)}</td></tr>
                    <tr><td><strong>Created:</strong></td><td>${formatDateTime(task.created_at)}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Prompt</h6>
                <div class="alert alert-light">
                    ${task.prompt}
                </div>
                ${task.error_message ? `
                    <h6>Error Message</h6>
                    <div class="alert alert-danger">
                        ${task.error_message}
                    </div>
                ` : ''}
            </div>
        </div>
        ${task.result_path ? `
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Generated Video</h6>
                    <video controls class="w-100" style="max-height: 400px;">
                        <source src="/static/generated/${task.result_path.split('/').pop()}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="downloadVideo('${task.result_path}')">
                            <i class="fas fa-download me-1"></i>
                            Download Video
                        </button>
                    </div>
                </div>
            </div>
        ` : ''}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

async function cancelTask(taskId) {
    if (!confirm('Are you sure you want to cancel this task?')) {
        return;
    }
    
    try {
        const result = await apiCall(`/cancel/${taskId}`);
        showNotification('Task cancelled successfully', 'success');
        await loadTasks();
    } catch (error) {
        showNotification('Failed to cancel task', 'danger');
        console.error('Error cancelling task:', error);
    }
}

function downloadVideo(resultPath) {
    const fileName = resultPath.split('/').pop();
    const link = document.createElement('a');
    link.href = `/static/generated/${fileName}`;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showNotification('Download started', 'success');
}

// Form validation
function validateScheduleForm() {
    const form = document.getElementById('schedule-form');
    if (!form) return true;
    
    const generatorType = form.querySelector('[name="generator_type"]').value;
    const prompt = form.querySelector('[name="prompt"]').value;
    const scheduledTime = form.querySelector('[name="scheduled_time"]').value;
    
    if (!generatorType || !prompt || !scheduledTime) {
        showNotification('Please fill in all required fields', 'warning');
        return false;
    }
    
    const scheduledDateTime = new Date(scheduledTime);
    const now = new Date();
    if (scheduledDateTime <= now) {
        showNotification('Scheduled time must be in the future', 'warning');
        return false;
    }
    
    return true;
}

// Auto-refresh functionality
function startAutoRefresh(interval = 30000) {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(() => {
        loadTasks();
    }, interval);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Page initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Start auto-refresh on dashboard
    if (window.location.pathname === '/') {
        startAutoRefresh();
    }
    
    // Form validation
    const scheduleForm = document.getElementById('schedule-form');
    if (scheduleForm) {
        scheduleForm.addEventListener('submit', function(event) {
            if (!validateScheduleForm()) {
                event.preventDefault();
            }
        });
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopAutoRefresh();
    });
});

// Export functions for global use
window.SentiMation = {
    showNotification,
    formatDateTime,
    formatRelativeTime,
    getStatusBadge,
    loadTasks,
    viewTask,
    cancelTask,
    downloadVideo,
    startAutoRefresh,
    stopAutoRefresh
}; 