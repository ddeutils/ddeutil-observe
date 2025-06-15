// Workflow Detail Page JavaScript

// Global variables
let currentTab = 'overview';
let workflowName = '';
let autoRefreshInterval = null;
let durationChart = null;
let taskDurationChart = null;
let taskFailureChart = null;
let selectedExecutionDate = null;
let executionData = [];
let dagInstance = null;
let workflowData = null;  // Add workflowData to global variables

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Get workflow name from URL
    const pathParts = window.location.pathname.split('/');
    const nameIndex = pathParts.indexOf('detail');
    if (nameIndex !== -1 && pathParts[nameIndex + 1]) {
        workflowName = pathParts[nameIndex + 1];
        console.log('Initialized workflow:', workflowName);

        // Initialize workflow data
        const workflowDataElement = document.getElementById('workflow-data');
        if (workflowDataElement) {
            workflowData = JSON.parse(workflowDataElement.textContent);
        }

        // Load initial data based on active tab
        const activeTab = document.querySelector('.tab-button.active')?.dataset.tab || 'overview';
        switchTab(activeTab);

        // Setup event listeners
        setupEventListeners();
    }
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
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });

    // DAG controls
    document.querySelectorAll('.zoom-controls button').forEach(button => {
        button.addEventListener('click', (e) => {
            const action = e.target.closest('button').dataset.action;
            handleDagZoom(action);
        });
    });

    document.querySelectorAll('.layout-controls button').forEach(button => {
        button.addEventListener('click', (e) => {
            const layout = e.target.closest('button').dataset.layout;
            toggleDagLayout(layout);
        });
    });

    // Task details panel
    document.querySelector('#task-details .btn-ghost').addEventListener('click', closeTaskDetails);

    // Setup keyboard shortcuts
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
    if (currentTab === tabName) return;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tabName);
        button.setAttribute('aria-selected', button.dataset.tab === tabName);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    currentTab = tabName;
    loadTabContent(tabName);
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
        case 'dag':
            initializeDagView();
            break;
        case 'execution':
            loadExecutionAnalysis();
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

function initializeDagView() {
    // Clear previous content
    d3.select('#dag-canvas').selectAll('*').remove();

    // Get canvas dimensions
    const canvas = document.getElementById('dag-canvas');
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    // Create SVG container with explicit dimensions
    const svg = d3.select('#dag-canvas')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .attr('class', 'dag-svg');

    // Add background pattern
    const defs = svg.append('defs');

    // Create grid pattern
    const gridPattern = defs.append('pattern')
        .attr('id', 'grid-pattern')
        .attr('patternUnits', 'userSpaceOnUse')
        .attr('width', 40)
        .attr('height', 40);

    gridPattern.append('path')
        .attr('d', 'M 40 0 L 0 0 0 40')
        .attr('fill', 'none')
        .attr('stroke', 'var(--border-color)')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.2);

    // Add background rectangle with pattern
    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .attr('class', 'dag-background');

    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'url(#grid-pattern)')
        .attr('class', 'dag-grid');

    // Create main group for the graph
    const g = svg.append('g')
        .attr('class', 'dag-inner');

    // Create defs for arrow markers
    defs.append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('class', 'arrowhead-path');

    // Get workflow jobs and their dependencies
    const jobs = workflowData.jobs || {};

    // Create nodes and links data
    const nodes = Object.entries(jobs).map(([id, config]) => ({
        id,
        type: config.type || 'default',
        params: config.params || {},
        status: getNodeStatus(id)
    }));

    const links = [];
    Object.entries(jobs).forEach(([id, config]) => {
        if (config.depends_on) {
            config.depends_on.forEach(depId => {
                links.push({
                    source: depId,
                    target: id
                });
            });
        }
    });

    // Create force simulation with adjusted parameters
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(60))
        .force('x', d3.forceX(width / 2).strength(0.1))
        .force('y', d3.forceY(height / 2).strength(0.1));

    // Create links
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(links)
        .enter()
        .append('path')
        .attr('class', 'task-edge')
        .attr('marker-end', 'url(#arrowhead)');

    // Create nodes
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add node rectangles
    node.append('rect')
        .attr('class', d => `node-shape ${d.status}`)
        .attr('width', 180)
        .attr('height', 40)
        .attr('rx', 8)
        .attr('ry', 8)
        .attr('x', -90)
        .attr('y', -20);

    // Add status indicator
    node.append('circle')
        .attr('class', d => `status-indicator ${d.status}`)
        .attr('r', 6)
        .attr('cx', -70)
        .attr('cy', -10);

    // Add job type icon
    node.append('text')
        .attr('class', 'job-type-icon')
        .attr('x', -50)
        .attr('y', -5)
        .text(d => getJobTypeIcon(d.type));

    // Add node label
    node.append('text')
        .attr('class', 'node-label')
        .attr('x', -30)
        .attr('y', 5)
        .text(d => d.id);

    // Add zoom behavior with adjusted scale extent
    const zoom = d3.zoom()
        .scaleExtent([0.1, 2])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
            if (window.updateMinimap) {
                window.updateMinimap(event.transform);
            }
        });

    svg.call(zoom);

    // Update positions on simulation tick
    simulation.on('tick', () => {
        // Keep nodes within bounds
        nodes.forEach(d => {
            d.x = Math.max(90, Math.min(width - 90, d.x));
            d.y = Math.max(20, Math.min(height - 20, d.y));
        });

        link.attr('d', d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            const dr = Math.sqrt(dx * dx + dy * dy);
            return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
        });

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Add click handlers for nodes
    node.on('click', function(event, d) {
        showTaskDetails(d.id);
    })
    .on('mouseover', function(event, d) {
        d3.select(this).classed('hover', true);
        // Highlight connected edges
        link.classed('highlight', l =>
            l.source.id === d.id || l.target.id === d.id
        );
    })
    .on('mouseout', function(event, d) {
        d3.select(this).classed('hover', false);
        link.classed('highlight', false);
    });

    // Add hover effects for edges
    link.on('mouseover', function(event, d) {
        d3.select(this).classed('hover', true);
    })
    .on('mouseout', function(event, d) {
        d3.select(this).classed('hover', false);
    });

    // Store the graph instance
    dagInstance = { svg, g, simulation, zoom };

    // Add minimap after dagInstance is created
    addMinimap(svg, g, nodes, links);

    // Handle window resize
    const resizeObserver = new ResizeObserver(entries => {
        for (const entry of entries) {
            const newWidth = entry.contentRect.width;
            const newHeight = entry.contentRect.height;

            // Update SVG dimensions
            svg.attr('width', newWidth)
               .attr('height', newHeight)
               .attr('viewBox', `0 0 ${newWidth} ${newHeight}`);

            // Update background and grid
            svg.select('.dag-background')
               .attr('width', newWidth)
               .attr('height', newHeight);

            svg.select('.dag-grid')
               .attr('width', newWidth)
               .attr('height', newHeight);

            // Update force simulation center and bounds
            simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.force('x', d3.forceX(newWidth / 2).strength(0.1));
            simulation.force('y', d3.forceY(newHeight / 2).strength(0.1));

            // Update minimap position
            const minimap = d3.select('.minimap');
            if (!minimap.empty()) {
                minimap.attr('transform', `translate(${newWidth - 174}, ${newHeight - 174})`);
            }

            // Restart simulation to apply new forces
            simulation.alpha(0.3).restart();
        }
    });

    resizeObserver.observe(canvas);

    // Initial fit
    handleDagZoom('fit');
}

// Drag functions
function dragstarted(event, d) {
    if (!event.active) dagInstance.simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) dagInstance.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function addMinimap(svg, g, nodes, links) {
    const minimapSize = 150;
    const minimap = svg.append('g')
        .attr('class', 'minimap')
        .attr('transform', `translate(${svg.node().clientWidth - minimapSize - 24}, ${svg.node().clientHeight - minimapSize - 24})`);

    // Add background
    minimap.append('rect')
        .attr('class', 'minimap-background')
        .attr('width', minimapSize)
        .attr('height', minimapSize)
        .attr('rx', 4)
        .attr('ry', 4)
        .attr('fill', 'var(--bg-primary)')
        .attr('stroke', 'var(--border-color)')
        .attr('stroke-width', 1);

    // Add viewport indicator
    minimap.append('rect')
        .attr('class', 'minimap-viewport')
        .attr('width', minimapSize)
        .attr('height', minimapSize)
        .attr('fill', 'var(--primary-color-light)')
        .attr('stroke', 'var(--primary-color)')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.3);

    // Get the bounds of all nodes
    const bounds = getGraphBounds(nodes);
    const scale = Math.min(
        minimapSize / (bounds.width || 1),
        minimapSize / (bounds.height || 1)
    ) * 0.8;

    // Add minimap nodes
    const minimapNodes = minimap.append('g')
        .attr('class', 'minimap-nodes')
        .selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('r', 3)
        .attr('fill', d => {
            switch(d.status) {
                case 'success': return 'var(--success-color)';
                case 'failed': return 'var(--error-color)';
                case 'running': return 'var(--warning-color)';
                default: return 'var(--text-secondary)';
            }
        })
        .attr('stroke', 'var(--bg-primary)')
        .attr('stroke-width', 1);

    // Add minimap links
    const minimapLinks = minimap.append('g')
        .attr('class', 'minimap-links')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', 'var(--border-color)')
        .attr('stroke-width', 1)
        .attr('opacity', 0.5);

    // Update minimap positions
    function updateMinimap(transform) {
        const centerX = svg.node().clientWidth / 2;
        const centerY = svg.node().clientHeight / 2;

        // Update nodes
        minimapNodes
            .attr('cx', d => {
                const x = (d.x - bounds.x) * scale + (minimapSize / 2);
                return isNaN(x) ? minimapSize / 2 : x;
            })
            .attr('cy', d => {
                const y = (d.y - bounds.y) * scale + (minimapSize / 2);
                return isNaN(y) ? minimapSize / 2 : y;
            });

        // Update links
        minimapLinks
            .attr('x1', d => {
                const x = (d.source.x - bounds.x) * scale + (minimapSize / 2);
                return isNaN(x) ? minimapSize / 2 : x;
            })
            .attr('y1', d => {
                const y = (d.source.y - bounds.y) * scale + (minimapSize / 2);
                return isNaN(y) ? minimapSize / 2 : y;
            })
            .attr('x2', d => {
                const x = (d.target.x - bounds.x) * scale + (minimapSize / 2);
                return isNaN(x) ? minimapSize / 2 : x;
            })
            .attr('y2', d => {
                const y = (d.target.y - bounds.y) * scale + (minimapSize / 2);
                return isNaN(y) ? minimapSize / 2 : y;
            });

        // Update viewport indicator
        const viewport = minimap.select('.minimap-viewport');
        if (transform) {
            const viewportWidth = minimapSize / transform.k;
            const viewportHeight = minimapSize / transform.k;
            const viewportX = (-transform.x / transform.k - bounds.x) * scale + (minimapSize / 2);
            const viewportY = (-transform.y / transform.k - bounds.y) * scale + (minimapSize / 2);

            viewport
                .attr('width', Math.min(viewportWidth, minimapSize))
                .attr('height', Math.min(viewportHeight, minimapSize))
                .attr('x', Math.max(0, Math.min(viewportX, minimapSize - viewportWidth)))
                .attr('y', Math.max(0, Math.min(viewportY, minimapSize - viewportHeight)));
        }
    }

    // Initial update
    updateMinimap();

    // Store update function for later use
    window.updateMinimap = updateMinimap;
}

function getGraphBounds(nodes) {
    if (!nodes.length) return { x: 0, y: 0, width: 0, height: 0 };

    const xCoords = nodes.map(n => n.x).filter(x => !isNaN(x));
    const yCoords = nodes.map(n => n.y).filter(y => !isNaN(y));

    if (!xCoords.length || !yCoords.length) return { x: 0, y: 0, width: 0, height: 0 };

    const minX = Math.min(...xCoords);
    const maxX = Math.max(...xCoords);
    const minY = Math.min(...yCoords);
    const maxY = Math.max(...yCoords);

    return {
        x: minX,
        y: minY,
        width: maxX - minX,
        height: maxY - minY
    };
}

function getNodeStatus(taskId) {
    // TODO: Implement actual status checking logic
    return 'pending';
}

function getJobTypeIcon(jobType) {
    const icons = {
        'python': '📝',
        'shell': '💻',
        'sql': '🗃️',
        'default': '⚙️'
    };
    return icons[jobType] || icons.default;
}

function handleDagZoom(action) {
    if (!dagInstance) return;

    const svg = dagInstance.svg;
    const zoom = dagInstance.zoom;
    const g = dagInstance.g;

    switch (action) {
        case 'in':
            svg.transition().duration(300).call(zoom.scaleBy, 1.3);
            break;
        case 'out':
            svg.transition().duration(300).call(zoom.scaleBy, 0.7);
            break;
        case 'fit':
            const svgElement = svg.node();
            const graphElement = g.node();
            const graphWidth = graphElement.getBBox().width;
            const graphHeight = graphElement.getBBox().height;
            const containerWidth = svgElement.clientWidth;
            const containerHeight = svgElement.clientHeight;

            const scale = Math.min(
                containerWidth / graphWidth,
                containerHeight / graphHeight
            ) * 0.8;

            const transform = d3.zoomIdentity
                .translate(containerWidth / 2, containerHeight / 2)
                .scale(scale)
                .translate(-graphWidth / 2, -graphHeight / 2);

            svg.transition().duration(300).call(zoom.transform, transform);
            break;
    }
}

function toggleDagLayout(layout) {
    if (!dagInstance) return;

    const g = dagInstance.g;
    g.graph().rankdir = layout === 'horizontal' ? 'LR' : 'TB';

    // Re-render the graph
    const render = new dagreD3.render();
    dagInstance.inner.call(render, g);

    // Reset zoom to fit
    handleDagZoom('fit');
}

// Add zoomDag function
function zoomDag(action) {
    if (!dagInstance) return;
    handleDagZoom(action);
}

function showTaskDetails(taskId) {
    const taskDetails = document.getElementById('task-details');
    const task = workflowData.jobs[taskId];

    if (!task) return;

    // Update task details content
    document.getElementById('task-id').textContent = taskId;
    document.getElementById('task-type').textContent = task.type || 'default';
    document.getElementById('task-status').textContent = getNodeStatus(taskId);
    document.getElementById('task-duration').textContent = getTaskDuration(taskId);

    // Update parameters
    const paramsJson = document.getElementById('task-params-json');
    paramsJson.textContent = JSON.stringify(task.params || {}, null, 2);

    // Update dependencies
    const dependenciesList = document.getElementById('task-dependencies');
    if (task.depends_on && task.depends_on.length > 0) {
        dependenciesList.innerHTML = task.depends_on.map(depId => `
            <div class="dependency-item" onclick="showTaskDetails('${depId}')">
                <i class="bx bx-git-branch"></i>
                ${depId}
            </div>
        `).join('');
    } else {
        dependenciesList.innerHTML = '<div class="empty-state">No dependencies</div>';
    }

    // Show the panel
    taskDetails.classList.add('open');
}

function closeTaskDetails() {
    const taskDetails = document.getElementById('task-details');
    taskDetails.classList.remove('open');
}

function getTaskDuration(taskId) {
    // TODO: Implement actual duration calculation
    return '-';
}

function updateMinimap(transform) {
    if (!dagInstance) return;

    const minimap = d3.select('.minimap');
    const viewport = minimap.select('.minimap-viewport');

    if (viewport.empty()) return;

    const svg = dagInstance.svg.node();
    const scale = transform.k;
    const x = -transform.x / scale;
    const y = -transform.y / scale;
    const width = svg.clientWidth / scale;
    const height = svg.clientHeight / scale;

    const minimapSize = 150;

    // Add safety checks for NaN values
    const safeX = isNaN(x) ? 0 : x;
    const safeY = isNaN(y) ? 0 : y;
    const safeWidth = isNaN(width) ? minimapSize : width;
    const safeHeight = isNaN(height) ? minimapSize : height;

    viewport
        .attr('x', safeX * (minimapSize / svg.clientWidth))
        .attr('y', safeY * (minimapSize / svg.clientHeight))
        .attr('width', safeWidth * (minimapSize / svg.clientWidth))
        .attr('height', safeHeight * (minimapSize / svg.clientHeight));
}

// Update the existing workflowData
workflowData = {
    id: 'sample-workflow',
    name: 'Sample Workflow',
    description: 'A sample workflow with multiple stages and jobs',
    status: 'running',
    created_at: '2024-03-20T10:00:00Z',
    updated_at: '2024-03-20T10:30:00Z',
    schedule: {
        type: 'cron',
        value: '0 0 * * *'
    },
    stages: [
        {
            id: 'stage1',
            name: 'Data Collection',
            description: 'Collect data from various sources',
            status: 'completed',
            jobs: ['collect_api_data', 'collect_db_data', 'validate_data']
        },
        {
            id: 'stage2',
            name: 'Data Processing',
            description: 'Process and transform the collected data',
            status: 'running',
            jobs: ['process_data', 'transform_data', 'enrich_data']
        },
        {
            id: 'stage3',
            name: 'Data Analysis',
            description: 'Analyze the processed data',
            status: 'pending',
            jobs: ['analyze_data', 'generate_reports', 'notify_results']
        },
        {
            id: 'stage4',
            name: 'Data Storage',
            description: 'Store the analyzed data',
            status: 'pending',
            jobs: ['store_results', 'archive_data', 'cleanup_temp']
        }
    ],
    jobs: {
        'collect_api_data': {
            type: 'http',
            params: {
                url: 'https://api.example.com/data',
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer token123'
                }
            },
            depends_on: []
        },
        'collect_db_data': {
            type: 'sql',
            params: {
                query: 'SELECT * FROM source_table',
                connection: 'source_db'
            },
            depends_on: []
        },
        'validate_data': {
            type: 'python',
            params: {
                script: 'validate_data.py',
                input_path: '/data/raw',
                output_path: '/data/validated'
            },
            depends_on: ['collect_api_data', 'collect_db_data']
        },
        'process_data': {
            type: 'python',
            params: {
                script: 'process_data.py',
                input_path: '/data/validated',
                output_path: '/data/processed'
            },
            depends_on: ['validate_data']
        },
        'transform_data': {
            type: 'sql',
            params: {
                query: 'TRANSFORM_DATA.sql',
                connection: 'target_db'
            },
            depends_on: ['process_data']
        },
        'enrich_data': {
            type: 'python',
            params: {
                script: 'enrich_data.py',
                input_path: '/data/processed',
                output_path: '/data/enriched'
            },
            depends_on: ['transform_data']
        },
        'analyze_data': {
            type: 'python',
            params: {
                script: 'analyze_data.py',
                input_path: '/data/enriched',
                output_path: '/data/analysis'
            },
            depends_on: ['enrich_data']
        },
        'generate_reports': {
            type: 'python',
            params: {
                script: 'generate_reports.py',
                input_path: '/data/analysis',
                output_path: '/reports'
            },
            depends_on: ['analyze_data']
        },
        'notify_results': {
            type: 'http',
            params: {
                url: 'https://api.example.com/notify',
                method: 'POST',
                body: {
                    'report_path': '/reports'
                }
            },
            depends_on: ['generate_reports']
        },
        'store_results': {
            type: 'sql',
            params: {
                query: 'STORE_RESULTS.sql',
                connection: 'archive_db'
            },
            depends_on: ['analyze_data']
        },
        'archive_data': {
            type: 'shell',
            params: {
                command: 'archive_data.sh',
                source: '/data/analysis',
                destination: '/archive'
            },
            depends_on: ['store_results']
        },
        'cleanup_temp': {
            type: 'shell',
            params: {
                command: 'cleanup.sh',
                paths: ['/data/temp', '/data/processed']
            },
            depends_on: ['archive_data', 'notify_results']
        }
    }
};
