// Workflow Detail Page JavaScript

// Global variables
let currentTab = 'overview';
let workflowName = '';
let autoRefreshInterval = null;
let durationChart = null;
let selectedExecutionDate = null;
let executionData = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Get workflow name from URL
    const pathParts = window.location.pathname.split('/');
    const nameIndex = pathParts.indexOf('detail');
    if (nameIndex !== -1 && pathParts[nameIndex + 1]) {
        workflowName = pathParts[nameIndex + 1];
        console.log('Initialized workflow:', workflowName);

        // Load initial data based on active tab
        const activeTab = document.querySelector('.tab-button.active')?.dataset.tab || 'overview';
        switchTab(activeTab);

        // Start auto-refresh for overview
        if (activeTab === 'overview') {
            startAutoRefresh();
        }
    }

    // Setup keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
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
    console.log('Switching to tab:', tabName);

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
    });
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`)?.setAttribute('aria-selected', 'true');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`)?.classList.add('active');

    // Stop auto-refresh
    stopAutoRefresh();

    // Load tab-specific content
    switch(tabName) {
        case 'overview':
            startAutoRefresh();
            break;
        case 'execution':
            loadExecutionAnalysis();
            break;
        case 'config':
            // Config is already loaded in template
            break;
    }
}

function loadTabContent(tabName) {
    switch (tabName) {
        case 'logs':
            loadLogs();
            break;
        case 'duration':
            loadDurationChart();
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

async function loadDurationChart(limit = null) {
    if (!workflowName) return;

    const limitSelect = document.getElementById('duration-limit');
    if (!limit && limitSelect) {
        limit = limitSelect.value;
    }

    try {
        const response = await fetch(`/api/v1/workflow/${workflowName}/duration-data?limit=${limit || 50}`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            executionData = result.data;
            createDurationChart(result.data);
            updateDurationStats(result.data);

            // If no execution is selected, select the latest
            if (!selectedExecutionDate && executionData.length > 0) {
                const latestExecution = executionData[executionData.length - 1];
                selectedExecutionDate = latestExecution.execution_date;
                updateSelectedExecutionInfo(latestExecution);
            }
        } else {
            console.error('Failed to load duration data');
        }
    } catch (error) {
        console.error('Error loading duration data:', error);
    }
}

function createDurationChart(data) {
    const ctx = document.getElementById('duration-chart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (durationChart) {
        durationChart.destroy();
    }

    // Prepare data for Chart.js
    const labels = data.map(item => {
        const date = new Date(item.execution_date);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    });

    const durations = data.map(item => item.duration);
    const statuses = data.map(item => item.status);

    // Color points based on status
    const backgroundColors = statuses.map(status => {
        switch (status) {
            case 'success': return '#10b981';
            case 'failed': return '#ef4444';
            case 'running': return '#f59e0b';
            case 'pending': return '#6b7280';
            default: return '#8b5cf6';
        }
    });

    durationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Execution Duration (seconds)',
                data: durations,
                borderColor: '#3b82f6',
                backgroundColor: backgroundColors,
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8,
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: `${workflowName} - Execution Duration Over Time`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const index = context[0].dataIndex;
                            const item = data[index];
                            return `Run: ${item.release_id}`;
                        },
                        label: function(context) {
                            const index = context.dataIndex;
                            const item = data[index];
                            return [
                                `Duration: ${item.duration.toFixed(2)}s`,
                                `Status: ${item.status}`,
                                `Date: ${new Date(item.execution_date).toLocaleString()}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Execution Time'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Duration (seconds)'
                    },
                    beginAtZero: true
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const clickedExecution = data[elementIndex];
                    selectExecution(clickedExecution);
                }
            }
        }
    });
}

function updateDurationStats(data) {
    if (!data || data.length === 0) return;

    const durations = data.map(item => item.duration);
    const avgDuration = durations.reduce((a, b) => a + b, 0) / durations.length;
    const minDuration = Math.min(...durations);
    const maxDuration = Math.max(...durations);

    const avgElement = document.getElementById('avg-duration');
    const minElement = document.getElementById('min-duration');
    const maxElement = document.getElementById('max-duration');
    const totalElement = document.getElementById('total-runs');

    if (avgElement) avgElement.textContent = `${avgDuration.toFixed(2)}s`;
    if (minElement) minElement.textContent = `${minDuration.toFixed(2)}s`;
    if (maxElement) maxElement.textContent = `${maxDuration.toFixed(2)}s`;
    if (totalElement) totalElement.textContent = data.length;
}

function selectExecution(execution) {
    selectedExecutionDate = execution.execution_date;
    updateSelectedExecutionInfo(execution);

    // Reload execution details
    loadExecutionRuns();
    loadExecutionLogs();

    // Update chart selection (visual feedback)
    highlightSelectedPoint(execution);
}

function updateSelectedExecutionInfo(execution) {
    const titleElement = document.getElementById('selected-execution-title');
    const dateElement = document.getElementById('selected-execution-date');
    const statusElement = document.getElementById('selected-execution-status');

    if (titleElement) {
        titleElement.textContent = `Run: ${execution.release_id}`;
    }

    if (dateElement) {
        const executionDate = new Date(execution.execution_date);
        dateElement.textContent = executionDate.toLocaleString();
    }

    if (statusElement) {
        statusElement.textContent = execution.status.toUpperCase();
        statusElement.className = `status-badge status-${execution.status}`;
    }
}

function highlightSelectedPoint(execution) {
    // Find the index of the selected execution
    const selectedIndex = executionData.findIndex(item =>
        item.execution_date === execution.execution_date
    );

    if (selectedIndex !== -1 && durationChart) {
        // Create highlight effect by updating point styles
        const dataset = durationChart.data.datasets[0];
        const originalRadius = 6;
        const highlightRadius = 10;

        // Ensure pointRadius is an array
        if (!Array.isArray(dataset.pointRadius)) {
            dataset.pointRadius = new Array(dataset.data.length).fill(originalRadius);
        } else {
            // Reset all point radii
            dataset.pointRadius = dataset.pointRadius.map(() => originalRadius);
        }

        // Highlight selected point
        dataset.pointRadius[selectedIndex] = highlightRadius;

        durationChart.update('none');
    }
}

// Execution Analysis Tab Functions
async function loadExecutionAnalysis() {
    if (!workflowName) return;

    try {
        // Load duration chart first
        await loadDurationChart();

        // Load latest execution by default
        if (executionData.length > 0) {
            const latestExecution = executionData[executionData.length - 1];
            selectedExecutionDate = latestExecution.execution_date;
            updateSelectedExecutionInfo(latestExecution);
            await loadExecutionRuns();
            await loadExecutionLogs();
        }
    } catch (error) {
        console.error('Error loading execution analysis:', error);
    }
}

// Execution Tab Functions
function switchExecutionTab(tabName) {
    // Update execution tab buttons
    document.querySelectorAll('.execution-tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    // Update execution tab content
    document.querySelectorAll('.execution-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`execution-${tabName}-tab`)?.classList.add('active');

    // Load tab-specific content
    switch(tabName) {
        case 'runs':
            loadExecutionRuns();
            break;
        case 'logs':
            loadExecutionLogs();
            break;
    }
}

async function loadExecutionRuns() {
    if (!workflowName || !selectedExecutionDate) return;

    const timelineContainer = document.getElementById('execution-runs-timeline');
    if (!timelineContainer) return;

    // Show loading
    timelineContainer.innerHTML = `
        <div class="runs-loading">
            <i class="bx bx-loader-alt bx-spin"></i>
            <p>Loading execution runs...</p>
        </div>
    `;

    try {
        const selectedDate = new Date(selectedExecutionDate).toISOString().split('T')[0];
        const response = await fetch(`/api/v1/workflow/${workflowName}/runs?start_date=${selectedDate}&end_date=${selectedDate}&limit=10`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            displayExecutionRuns(result.runs);
        } else {
            throw new Error('Failed to load runs');
        }
    } catch (error) {
        console.error('Error loading execution runs:', error);
        timelineContainer.innerHTML = `
            <div class="empty-state">
                <i class="bx bx-exclamation-circle"></i>
                <p>Failed to load execution runs</p>
            </div>
        `;
    }
}

function displayExecutionRuns(runs) {
    const timelineContainer = document.getElementById('execution-runs-timeline');
    if (!timelineContainer) return;

    if (!runs || runs.length === 0) {
        timelineContainer.innerHTML = `
            <div class="empty-state">
                <i class="bx bx-time"></i>
                <p>No runs found for selected date</p>
            </div>
        `;
        return;
    }

    const runsHtml = runs.map(run => `
        <div class="timeline-item status-${run.status}" data-status="${run.status}">
            <div class="timeline-marker">
                <div class="timeline-dot status-${run.status}"></div>
            </div>
            <div class="timeline-content">
                <div class="timeline-card" onclick="viewRunDetail('${run.id}')">
                    <div class="timeline-header">
                        <div class="run-title">
                            <span class="run-id">${run.release_id}</span>
                            <span class="run-date">${new Date(run.execution_date).toLocaleString()}</span>
                        </div>
                        <div class="run-status-badge status-${run.status}">
                            ${getStatusIcon(run.status)}
                            ${run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                        </div>
                    </div>
                    <div class="timeline-body">
                        <div class="run-details">
                            <span class="detail-item">
                                <strong>Duration:</strong>
                                ${run.duration ? `${run.duration.toFixed(2)}s` : '-'}
                            </span>
                            ${run.error_message ? `
                                <span class="detail-item error">
                                    <strong>Error:</strong> ${run.error_message.substring(0, 100)}...
                                </span>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    timelineContainer.innerHTML = runsHtml;
}

async function loadExecutionLogs() {
    if (!workflowName || !selectedExecutionDate) return;

    const logsContainer = document.getElementById('execution-logs-terminal');
    if (!logsContainer) return;

    // Show loading
    logsContainer.innerHTML = `
        <div class="log-loading">
            <i class="bx bx-loader-alt bx-spin"></i>
            <p>Loading execution logs...</p>
        </div>
    `;

    try {
        const selectedDate = new Date(selectedExecutionDate).toISOString().split('T')[0];
        const response = await fetch(`/api/v1/workflow/${workflowName}/logs?date=${selectedDate}`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            displayExecutionLogs(result.logs);
        } else {
            throw new Error('Failed to load logs');
        }
    } catch (error) {
        console.error('Error loading execution logs:', error);
        logsContainer.innerHTML = `
            <div class="log-loading">
                <i class="bx bx-exclamation-circle"></i>
                <p>Failed to load execution logs</p>
            </div>
        `;
    }
}

function displayExecutionLogs(logs) {
    const logsContainer = document.getElementById('execution-logs-terminal');
    if (!logsContainer) return;

    if (!logs || logs.length === 0) {
        logsContainer.innerHTML = `
            <div class="log-loading">
                <i class="bx bx-info-circle"></i>
                <p>No logs found for selected execution</p>
            </div>
        `;
        return;
    }

    const logsHtml = logs.map(log => `
        <div class="log-entry level-${log.level?.toLowerCase() || 'info'}">
            <span class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
            <span class="log-level level-${log.level?.toLowerCase() || 'info'}">[${log.level || 'INFO'}]</span>
            <span class="log-message">${log.message}</span>
        </div>
    `).join('');

    logsContainer.innerHTML = logsHtml;

    // Scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Filter Functions
function filterExecutionData() {
    const dateFilter = document.getElementById('execution-date-filter')?.value;
    const statusFilter = document.getElementById('execution-status-filter')?.value;

    // If we have specific filters, reload the runs data
    if (dateFilter || statusFilter) {
        loadFilteredExecutionRuns(dateFilter, statusFilter);
    } else {
        // Otherwise, show current execution runs
        loadExecutionRuns();
    }
}

async function loadFilteredExecutionRuns(dateFilter, statusFilter) {
    if (!workflowName) return;

    const timelineContainer = document.getElementById('execution-runs-timeline');
    if (!timelineContainer) return;

    // Show loading
    timelineContainer.innerHTML = `
        <div class="runs-loading">
            <i class="bx bx-loader-alt bx-spin"></i>
            <p>Loading filtered runs...</p>
        </div>
    `;

    try {
        let url = `/api/v1/workflow/${workflowName}/runs?limit=50`;
        if (dateFilter) {
            url += `&start_date=${dateFilter}&end_date=${dateFilter}`;
        }
        if (statusFilter) {
            url += `&status=${statusFilter}`;
        }

        const response = await fetch(url, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            displayExecutionRuns(result.runs);
        } else {
            throw new Error('Failed to load filtered runs');
        }
    } catch (error) {
        console.error('Error loading filtered runs:', error);
        timelineContainer.innerHTML = `
            <div class="empty-state">
                <i class="bx bx-exclamation-circle"></i>
                <p>Failed to load filtered runs</p>
            </div>
        `;
    }
}

function filterLogs() {
    const levelFilter = document.getElementById('log-level-filter')?.value;
    const logEntries = document.querySelectorAll('.log-entry');

    logEntries.forEach(entry => {
        if (!levelFilter || entry.classList.contains(`level-${levelFilter.toLowerCase()}`)) {
            entry.style.display = 'block';
        } else {
            entry.style.display = 'none';
        }
    });
}

// Utility Functions
function getStatusIcon(status) {
    switch (status) {
        case 'success':
            return '<i class="bx bx-check-circle"></i>';
        case 'failed':
            return '<i class="bx bx-x-circle"></i>';
        case 'running':
            return '<i class="bx bx-time"></i>';
        case 'pending':
            return '<i class="bx bx-hourglass"></i>';
        default:
            return '<i class="bx bx-circle"></i>';
    }
}

// Refresh Functions
function refreshDurationChart() {
    loadDurationChart();
}

function refreshSelectedExecution() {
    if (selectedExecutionDate) {
        loadExecutionRuns();
        loadExecutionLogs();
    }
}

function refreshLogs() {
    loadExecutionLogs();
}

function clearLogs() {
    const logsContainer = document.getElementById('execution-logs-terminal');
    if (logsContainer) {
        logsContainer.innerHTML = `
            <div class="log-loading">
                <i class="bx bx-info-circle"></i>
                <p>Logs cleared</p>
            </div>
        `;
    }
}

// Auto-refresh functionality
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    autoRefreshInterval = setInterval(() => {
        const activeTab = document.querySelector('.tab-button.active')?.dataset.tab;

        if (activeTab === 'overview') {
            // Refresh overview data
            window.location.reload();
        } else if (activeTab === 'execution') {
            // Refresh execution analysis
            loadDurationChart();
            if (selectedExecutionDate) {
                loadExecutionRuns();
                loadExecutionLogs();
            }
        }
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function refreshWorkflowDetail() {
    window.location.reload();
}

// Workflow actions
async function runWorkflow(workflowName) {
    if (!workflowName) return;

    try {
        const response = await fetch(`/api/v1/workflow/${workflowName}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();

            // Show success notification
            showNotification('Workflow run triggered successfully!', 'success');

            // Refresh the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Failed to trigger workflow run', 'error');
        }
    } catch (error) {
        console.error('Error running workflow:', error);
        showNotification('Failed to trigger workflow run', 'error');
    }
}

// Run detail modal
async function viewRunDetail(runId) {
    if (!runId) return;

    const modal = document.getElementById('run-detail-modal');
    const modalContent = document.getElementById('run-detail-content');

    if (!modal || !modalContent) return;

    // Show modal with loading
    modalContent.innerHTML = `
        <div class="modal-loading">
            <i class="bx bx-loader-alt bx-spin"></i>
            <p>Loading run details...</p>
        </div>
    `;
    modal.classList.add('active');

    try {
        const response = await fetch(`/api/v1/workflow/run/${runId}`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const runDetail = await response.json();
            displayRunDetail(runDetail);
        } else {
            throw new Error('Failed to load run details');
        }
    } catch (error) {
        console.error('Error loading run details:', error);
        modalContent.innerHTML = `
            <div class="modal-error">
                <i class="bx bx-exclamation-circle"></i>
                <p>Failed to load run details</p>
            </div>
        `;
    }
}

function displayRunDetail(runDetail) {
    const modalContent = document.getElementById('run-detail-content');
    const modalTitle = document.getElementById('run-detail-title');

    if (modalTitle) {
        modalTitle.textContent = `Run Details - ${runDetail.release_id}`;
    }

    if (modalContent) {
        modalContent.innerHTML = `
            <div class="run-detail-content">
                <div class="run-detail-header">
                    <div class="run-detail-info">
                        <h3>${runDetail.workflow_name}</h3>
                        <p>${runDetail.workflow_desc || 'No description'}</p>
                    </div>
                    <div class="run-detail-status">
                        <span class="status-badge status-${runDetail.status}">
                            ${getStatusIcon(runDetail.status)}
                            ${runDetail.status.charAt(0).toUpperCase() + runDetail.status.slice(1)}
                        </span>
                    </div>
                </div>

                <div class="run-detail-stats">
                    <div class="stat-item">
                        <span class="stat-label">Execution Date:</span>
                        <span class="stat-value">${new Date(runDetail.execution_date).toLocaleString()}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Duration:</span>
                        <span class="stat-value">${runDetail.duration ? `${runDetail.duration.toFixed(2)}s` : '-'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Start Time:</span>
                        <span class="stat-value">${runDetail.start_time ? new Date(runDetail.start_time).toLocaleString() : '-'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">End Time:</span>
                        <span class="stat-value">${runDetail.end_time ? new Date(runDetail.end_time).toLocaleString() : '-'}</span>
                    </div>
                </div>

                ${runDetail.error_message ? `
                    <div class="run-detail-error">
                        <h4>Error Message</h4>
                        <pre>${runDetail.error_message}</pre>
                    </div>
                ` : ''}

                ${runDetail.logs && runDetail.logs.length > 0 ? `
                    <div class="run-detail-logs">
                        <h4>Execution Logs</h4>
                        <div class="logs-preview">
                            ${runDetail.logs.map(log => `
                                <div class="log-preview-item">
                                    <strong>${log.workflow_name}</strong> - ${log.type}
                                    ${log.traces && log.traces.length > 0 ? `
                                        <div class="log-traces">
                                            ${log.traces.map(trace =>
                                                trace.meta ? trace.meta.map(meta => `
                                                    <div class="trace-item">
                                                        <span class="trace-time">${new Date(meta.datetime).toLocaleTimeString()}</span>
                                                        <span class="trace-message">${meta.message}</span>
                                                    </div>
                                                `).join('') : ''
                                            ).join('')}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

function closeRunDetail() {
    const modal = document.getElementById('run-detail-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal on outside click
document.addEventListener('click', function(e) {
    const modal = document.getElementById('run-detail-modal');
    if (modal && e.target === modal) {
        closeRunDetail();
    }
});

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bx ${type === 'success' ? 'bx-check-circle' : type === 'error' ? 'bx-x-circle' : 'bx-info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="bx bx-x"></i>
        </button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + R: Refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshWorkflowDetail();
    }

    // Escape: Close modal
    if (e.key === 'Escape') {
        closeRunDetail();
    }
}
