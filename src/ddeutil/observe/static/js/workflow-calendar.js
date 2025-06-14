// Workflow Timeline JavaScript

// Global variables
let selectedRun = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeTimelinePage();
    setupEventListeners();
});

function initializeTimelinePage() {
    // Update page title with current filters
    updatePageTitle();

    // Setup tooltips
    setupTooltips();
}

function setupEventListeners() {
    // Filter form submission
    const filterForm = document.getElementById('timeline-filter-form');
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

    // Timeline item clicks
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach(item => {
        item.addEventListener('click', function() {
            const runId = this.dataset.runId;
            if (runId) {
                viewRunDetail(runId);
            }
        });
    });
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

    const url = '/workflow/calendar' + (params.toString() ? '?' + params.toString() : '');
    window.location.href = url;
}

function refreshTimeline() {
    const loadingIndicator = createLoadingIndicator();
    document.body.appendChild(loadingIndicator);

    setTimeout(() => {
        window.location.reload();
    }, 500);
}

async function viewRunDetail(runId) {
    selectedRun = runId;
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
    selectedRun = null;
}

function handleKeyboardShortcuts(e) {
    // ESC key to close modal
    if (e.key === 'Escape') {
        closeRunDetail();
    }

    // R key to refresh timeline
    if (e.key === 'r' || e.key === 'R') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            refreshTimeline();
        }
    }

    // F key to focus on workflow filter
    if (e.key === 'f' || e.key === 'F') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            const workflowFilter = document.getElementById('workflow-filter');
            if (workflowFilter) {
                workflowFilter.focus();
            }
        }
    }
}

function updatePageTitle() {
    const workflowFilter = document.getElementById('workflow-filter');
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');
    const statusFilter = document.getElementById('status-filter');

    let titleParts = ['Workflow Timeline'];

    if (workflowFilter && workflowFilter.value) {
        titleParts.push(`- ${workflowFilter.value}`);
    }

    if (startDate && endDate && startDate.value && endDate.value) {
        titleParts.push(`(${startDate.value} to ${endDate.value})`);
    }

    if (statusFilter && statusFilter.value) {
        titleParts.push(`- ${statusFilter.value.charAt(0).toUpperCase() + statusFilter.value.slice(1)}`);
    }

    document.title = titleParts.join(' ') + ' - Observe';
}

function setupTooltips() {
    // Initialize tooltips for status badges and other elements
    const elementsWithTooltips = document.querySelectorAll('[title]');

    elementsWithTooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.getAttribute('title'));
        });

        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    // Remove existing tooltip
    hideTooltip();

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    tooltip.style.position = 'fixed';
    tooltip.style.left = `${rect.left + (rect.width - tooltipRect.width) / 2}px`;
    tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;
    tooltip.style.background = 'var(--text-primary)';
    tooltip.style.color = 'var(--card-bg)';
    tooltip.style.padding = '0.5rem';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '0.75rem';
    tooltip.style.zIndex = '1001';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.opacity = '0';
    tooltip.style.transition = 'opacity 0.2s ease';

    // Animate in
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
}

function hideTooltip() {
    const existingTooltip = document.querySelector('.tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
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

// Auto-refresh functionality for running workflows
function setupAutoRefresh() {
    const runningItems = document.querySelectorAll('.timeline-item.status-running');

    if (runningItems.length > 0) {
        // Auto-refresh every 30 seconds if there are running workflows
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    }
}

// Initialize auto-refresh
document.addEventListener('DOMContentLoaded', setupAutoRefresh);
