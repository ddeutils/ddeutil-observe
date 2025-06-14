// Workflow Detail Page JavaScript

// Global variables
let currentTab = 'overview';
let workflowName = '';
let autoRefreshInterval = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeWorkflowDetail();
    setupEventListeners();
    startAutoRefresh();
});

function initializeWorkflowDetail() {
    // Get workflow name from URL or page
    const titleElement = document.getElementById('workflow-detail-title');
    if (titleElement) {
        workflowName = titleElement.textContent.trim();
    }

    // Load initial content for active tab
    loadTabContent(currentTab);
}

function setupEventListeners() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });

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

    // Filter events
    const statusFilter = document.getElementById('status-filter');
    const dateFilter = document.getElementById('date-filter');

    if (statusFilter) {
        statusFilter.addEventListener('change', filterRuns);
    }

    if (dateFilter) {
        dateFilter.addEventListener('change', filterRuns);
    }
}

function switchTab(tabName) {
    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.remove('active');
        button.setAttribute('aria-selected', 'false');
    });

    const activeTabButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeTabButton) {
        activeTabButton.classList.add('active');
        activeTabButton.setAttribute('aria-selected', 'true');
    }

    // Update tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    const activeTabContent = document.getElementById(`${tabName}-tab`);
    if (activeTabContent) {
        activeTabContent.classList.add('active');
    }

    currentTab = tabName;

    // Load content for the active tab
    loadTabContent(tabName);
}

function loadTabContent(tabName) {
    switch (tabName) {
        case 'logs':
            loadLogs();
            break;
        case 'runs':
            // Runs are already loaded in the template
            break;
        case 'overview':
            // Overview is already loaded in the template
            break;
        case 'config':
            // Config is already loaded in the template
            break;
    }
}

async function loadLogs() {
    const logsTerminal = document.getElementById('logs-terminal');
    if (!logsTerminal) return;

    try {
        logsTerminal.innerHTML = '<div class="log-loading"><i class="bx bx-loader-alt bx-spin"></i> Loading logs...</div>';

        const response = await fetch(`/api/v1/workflow/${workflowName}/logs`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const logs = await response.json();
            displayLogs(logs);
        } else {
            logsTerminal.innerHTML = '<div class="log-error">Failed to load logs</div>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        logsTerminal.innerHTML = '<div class="log-error">Network error occurred</div>';
    }
}

function displayLogs(logs) {
    const logsTerminal = document.getElementById('logs-terminal');
    if (!logsTerminal) return;

    if (!logs || logs.length === 0) {
        logsTerminal.innerHTML = '<div class="log-empty">No logs available</div>';
        return;
    }

    let logContent = '';
    logs.forEach(log => {
        const timestamp = new Date(log.timestamp).toLocaleString();
        const level = log.level || 'INFO';
        const message = log.message || '';

        logContent += `<div class="log-entry log-${level.toLowerCase()}">`;
        logContent += `<span class="log-timestamp">[${timestamp}]</span> `;
        logContent += `<span class="log-level">${level}</span> `;
        logContent += `<span class="log-message">${message}</span>`;
        logContent += `</div>\n`;
    });

    logsTerminal.innerHTML = logContent;

    // Auto-scroll to bottom
    logsTerminal.scrollTop = logsTerminal.scrollHeight;
}

function filterRuns() {
    const statusFilter = document.getElementById('status-filter');
    const dateFilter = document.getElementById('date-filter');
    const timelineItems = document.querySelectorAll('.timeline-item');

    const selectedStatus = statusFilter ? statusFilter.value : '';
    const selectedDate = dateFilter ? dateFilter.value : '';

    timelineItems.forEach(item => {
        const itemStatus = item.dataset.status || '';
        const itemDate = item.dataset.date || '';

        let showItem = true;

        // Filter by status
        if (selectedStatus && itemStatus !== selectedStatus) {
            showItem = false;
        }

        // Filter by date
        if (selectedDate && itemDate !== selectedDate) {
            showItem = false;
        }

        item.style.display = showItem ? 'flex' : 'none';
    });
}

async function viewRunDetail(runId) {
    const modal = document.getElementById('run-detail-modal');
    const content = document.getElementById('run-detail-content');
    const title = document.getElementById('run-detail-title');

    if (!modal || !content) return;

    // Update modal title
    if (title) {
        title.textContent = `Run Details - ${runId}`;
    }

    // Show modal with loading state
    content.innerHTML = createLoadingContent();
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    try {
        const response = await fetch(`/workflow/run/${runId}`, {
            headers: {
                'Accept': 'application/json',
                'HX-Request': 'true'
            }
        });

        if (response.ok) {
            const htmlContent = await response.text();
            content.innerHTML = htmlContent;
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
    }
}

async function runWorkflow(workflowName) {
    try {
        const response = await fetch(`/api/v1/workflow/${workflowName}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            showNotification('Workflow started successfully', 'success');

            // Refresh the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification('Failed to start workflow', 'error');
        }
    } catch (error) {
        console.error('Error running workflow:', error);
        showNotification('Network error occurred', 'error');
    }
}

function refreshWorkflowDetail() {
    const loadingIndicator = createLoadingIndicator();
    document.body.appendChild(loadingIndicator);

    setTimeout(() => {
        window.location.reload();
    }, 500);
}

async function refreshLogs() {
    if (currentTab === 'logs') {
        await loadLogs();
    }
}

function clearLogs() {
    const logsTerminal = document.getElementById('logs-terminal');
    if (logsTerminal) {
        logsTerminal.innerHTML = '<div class="log-empty">Logs cleared</div>';
    }
}

function handleKeyboardShortcuts(e) {
    // ESC key to close modal
    if (e.key === 'Escape') {
        closeRunDetail();
    }

    // Number keys to switch tabs
    if (e.key >= '1' && e.key <= '4' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        const tabNames = ['overview', 'runs', 'logs', 'config'];
        const tabIndex = parseInt(e.key) - 1;
        if (tabIndex < tabNames.length) {
            switchTab(tabNames[tabIndex]);
        }
    }

    // R key to refresh
    if (e.key === 'r' || e.key === 'R') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            if (currentTab === 'logs') {
                refreshLogs();
            } else {
                refreshWorkflowDetail();
            }
        }
    }
}

function startAutoRefresh() {
    // Auto-refresh every 30 seconds if there are running workflows
    const runningItems = document.querySelectorAll('.status-running');

    if (runningItems.length > 0) {
        autoRefreshInterval = setInterval(() => {
            if (currentTab === 'logs') {
                refreshLogs();
            } else if (currentTab === 'runs' || currentTab === 'overview') {
                // Refresh the page to get updated run data
                window.location.reload();
            }
        }, 30000);
    }
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bx ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1003;
        padding: 1rem;
        border-radius: 6px;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;

    // Apply type-specific styles
    if (type === 'success') {
        notification.style.background = 'rgba(34, 197, 94, 0.15)';
        notification.style.color = '#16a34a';
        notification.style.border = '1px solid rgba(34, 197, 94, 0.3)';
    } else if (type === 'error') {
        notification.style.background = 'rgba(239, 68, 68, 0.15)';
        notification.style.color = '#dc2626';
        notification.style.border = '1px solid rgba(239, 68, 68, 0.3)';
    } else {
        notification.style.background = 'var(--card-bg)';
        notification.style.color = 'var(--text-primary)';
        notification.style.border = '1px solid var(--border-color)';
    }

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'bx-check-circle';
        case 'error':
            return 'bx-x-circle';
        case 'warning':
            return 'bx-error-circle';
        default:
            return 'bx-info-circle';
    }
}

function createLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'loading-indicator';
    indicator.innerHTML = `
        <div class="loading-spinner"></div>
        <p>Loading...</p>
    `;
    indicator.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        z-index: 1002;
        text-align: center;
        border: 1px solid var(--border-color);
    `;

    const spinner = indicator.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.cssText = `
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        `;
    }

    return indicator;
}

function createLoadingContent() {
    return `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>Loading run details...</p>
        </div>
        <style>
            .loading-content {
                text-align: center;
                padding: 2rem;
            }
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 4px solid var(--border-color);
                border-top: 4px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        </style>
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
        <style>
            .error-content {
                text-align: center;
                padding: 2rem;
                color: var(--text-secondary);
            }
            .error-content i {
                font-size: 3rem;
                color: #dc2626;
                margin-bottom: 1rem;
            }
            .error-content h3 {
                margin: 0 0 0.5rem 0;
                color: var(--text-primary);
            }
            .error-content p {
                margin: 0 0 1.5rem 0;
            }
        </style>
    `;
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});
