// Workflow Runs JavaScript

// Global variables
let currentRunId = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeRunsPage();
    setupEventListeners();
    setupAutoRefresh();
});

function initializeRunsPage() {
    // Update page title with current filters
    updatePageTitle();

    // Highlight today's date in date inputs
    highlightTodayInDateInputs();

    // Setup tooltips
    setupTooltips();
}

function setupEventListeners() {
    // Filter form submission
    const filterForm = document.getElementById('runs-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', handleFilterSubmit);
    }

    // Modal close events
    const modal = document.getElementById('run-detail-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeRunDetail();
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function setupAutoRefresh() {
    // Auto-refresh running jobs every 30 seconds
    setInterval(function() {
        const runningRows = document.querySelectorAll('.run-row.status-running');
        if (runningRows.length > 0) {
            refreshRunningStatuses();
        }
    }, 30000);
}

function handleFilterSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const params = new URLSearchParams();

    for (let [key, value] of formData.entries()) {
        if (value.trim()) {
            params.append(key, value);
        }
    }

    const url = '/workflow/runs' + (params.toString() ? '?' + params.toString() : '');
    window.location.href = url;
}

function refreshRuns() {
    const loadingIndicator = createLoadingIndicator();
    document.body.appendChild(loadingIndicator);

    setTimeout(() => {
        window.location.reload();
    }, 500);
}

function refreshRunningStatuses() {
    const runningRows = document.querySelectorAll('.run-row.status-running');

    runningRows.forEach(async (row) => {
        const runId = row.querySelector('.btn[onclick*="viewRunDetail"]')
            ?.getAttribute('onclick')
            ?.match(/viewRunDetail\('(\d+)'\)/)?.[1];

        if (runId) {
            try {
                const response = await fetch(`/api/v1/workflow/run/${runId}/status`);
                if (response.ok) {
                    const data = await response.json();
                    updateRunRowStatus(row, data);
                }
            } catch (error) {
                console.error('Failed to refresh run status:', error);
            }
        }
    });
}

function updateRunRowStatus(row, statusData) {
    const statusCell = row.querySelector('.status-cell .status-badge');
    const durationCell = row.querySelector('.duration-cell');
    const actionsCell = row.querySelector('.actions-cell');

    // Update status badge
    if (statusCell) {
        statusCell.className = `status-badge status-${statusData.status}`;
        statusCell.innerHTML = getStatusIcon(statusData.status) + statusData.status.charAt(0).toUpperCase() + statusData.status.slice(1);
    }

    // Update duration
    if (durationCell && statusData.duration) {
        durationCell.textContent = `${statusData.duration}s`;
    }

    // Update row class
    row.className = `run-row status-${statusData.status}`;

    // Update action buttons
    if (actionsCell && statusData.status !== 'running') {
        updateActionButtons(actionsCell, statusData.status, statusData.id);
    }
}

function getStatusIcon(status) {
    const icons = {
        'running': '<i class="bx bx-loader-alt bx-spin"></i>',
        'success': '<i class="bx bx-check-circle"></i>',
        'failed': '<i class="bx bx-x-circle"></i>',
        'pending': '<i class="bx bx-time"></i>',
        'cancelled': '<i class="bx bx-stop-circle"></i>'
    };
    return icons[status] || '';
}

function updateActionButtons(actionsCell, status, runId) {
    const buttons = [];

    // View details button (always present)
    buttons.push(`
        <button class="btn btn-sm" onclick="viewRunDetail('${runId}')" title="View run details">
            <i class="bx bx-info-circle"></i>
        </button>
    `);

    // Status-specific buttons
    if (status === 'running') {
        buttons.push(`
            <button class="btn btn-sm btn-warning" onclick="cancelRun('${runId}')" title="Cancel run">
                <i class="bx bx-stop"></i>
            </button>
        `);
    } else if (status === 'failed' || status === 'cancelled') {
        buttons.push(`
            <button class="btn btn-sm btn-primary" onclick="retryRun('${runId}')" title="Retry run">
                <i class="bx bx-refresh"></i>
            </button>
        `);
    }

    actionsCell.innerHTML = buttons.join('');
}

async function viewRunDetail(runId) {
    currentRunId = runId;
    const modal = document.getElementById('run-detail-modal');
    const content = document.getElementById('run-detail-content');

    if (!modal || !content) return;

    // Show modal with loading state
    content.innerHTML = createLoadingContent();
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    try {
        const response = await fetch(`/workflow/run/${runId}`, {
            headers: {
                'HX-Request': 'true'
            }
        });

        if (response.ok) {
            const html = await response.text();
            content.innerHTML = html;
        } else {
            content.innerHTML = createErrorContent('Failed to load run details');
        }
    } catch (error) {
        console.error('Error loading run details:', error);
        content.innerHTML = createErrorContent('Network error occurred');
    }
}

function closeRunDetail() {
    const modal = document.getElementById('run-detail-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        currentRunId = null;
    }
}

async function cancelRun(runId) {
    if (!confirm('Are you sure you want to cancel this workflow run?')) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/workflow/run/${runId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showNotification('Workflow run cancelled successfully', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            const error = await response.json();
            showNotification(error.message || 'Failed to cancel run', 'error');
        }
    } catch (error) {
        console.error('Error cancelling run:', error);
        showNotification('Network error occurred', 'error');
    }
}

async function retryRun(runId) {
    if (!confirm('Are you sure you want to retry this workflow run?')) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/workflow/run/${runId}/retry`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            showNotification('Workflow run retried successfully', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            const error = await response.json();
            showNotification(error.message || 'Failed to retry run', 'error');
        }
    } catch (error) {
        console.error('Error retrying run:', error);
        showNotification('Network error occurred', 'error');
    }
}

function handleKeyboardShortcuts(e) {
    // ESC key to close modal
    if (e.key === 'Escape') {
        closeRunDetail();
    }

    // R key to refresh (when not in input)
    if (e.key === 'r' && !e.target.matches('input, textarea, select')) {
        e.preventDefault();
        refreshRuns();
    }
}

function updatePageTitle() {
    const workflowFilter = document.getElementById('workflow-filter');
    const statusFilter = document.getElementById('status-filter');

    let title = 'Workflow Runs';
    const filters = [];

    if (workflowFilter && workflowFilter.value) {
        filters.push(workflowFilter.value);
    }

    if (statusFilter && statusFilter.value) {
        filters.push(statusFilter.value);
    }

    if (filters.length > 0) {
        title += ` - ${filters.join(', ')}`;
    }

    document.title = title + ' - Observe';
}

function highlightTodayInDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');

    dateInputs.forEach(input => {
        if (input.value === today) {
            input.style.borderColor = 'var(--primary-color)';
            input.style.boxShadow = '0 0 0 2px rgba(var(--primary-rgb), 0.1)';
        }
    });
}

function setupTooltips() {
    // Simple tooltip implementation
    const tooltipElements = document.querySelectorAll('[title]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.title;
    tooltip.style.position = 'absolute';
    tooltip.style.background = 'var(--tooltip-bg)';
    tooltip.style.color = 'var(--tooltip-color)';
    tooltip.style.padding = '0.5rem';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '0.75rem';
    tooltip.style.zIndex = '9999';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.boxShadow = 'var(--shadow-md)';

    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';

    // Remove title to prevent browser tooltip
    e.target.dataset.originalTitle = e.target.title;
    e.target.removeAttribute('title');
}

function hideTooltip(e) {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }

    // Restore title
    if (e.target.dataset.originalTitle) {
        e.target.title = e.target.dataset.originalTitle;
        delete e.target.dataset.originalTitle;
    }
}

function createLoadingIndicator() {
    const loading = document.createElement('div');
    loading.className = 'loading-indicator';
    loading.innerHTML = `
        <div class="loading-overlay">
            <div class="loading-spinner">
                <div class="spinner"></div>
                <span>Loading...</span>
            </div>
        </div>
    `;
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    return loading;
}

function createLoadingContent() {
    return `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>Loading run details...</p>
        </div>
    `;
}

function createErrorContent(message) {
    return `
        <div class="error-content">
            <i class="bx bx-error-circle"></i>
            <h3>Error</h3>
            <p>${message}</p>
            <button class="btn btn-primary" onclick="closeRunDetail()">Close</button>
        </div>
    `;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="bx bx-${type === 'success' ? 'check' : type === 'error' ? 'x' : 'info'}-circle"></i>
        <span>${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        z-index: 10000;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}
