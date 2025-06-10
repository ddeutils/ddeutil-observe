// Workflow Management JavaScript
class WorkflowManager {
    constructor() {
        this.dialog = document.getElementById("create-workflow-dialog");
        this.form = document.getElementById("create-workflow-form");
        this.searchInput = document.querySelector('input[name="search_text"]');
        this.init();
    }

    init() {
        this.setupSearchFunctionality();
        this.setupFormValidation();
        this.setupDialogEvents();
    }

    // Search functionality
    setupSearchFunctionality() {
        if (!this.searchInput) return;

        const searchContainer = this.searchInput.closest('.search-container');
        const clearButton = searchContainer?.querySelector('.search-clear');
        const searchIcon = searchContainer?.querySelector('.search-icon');

        // Show/hide clear button based on input value
        this.searchInput.addEventListener('input', (e) => {
            const hasValue = e.target.value.trim().length > 0;
            if (clearButton) {
                clearButton.style.display = hasValue ? 'flex' : 'none';
            }
            if (searchIcon) {
                searchIcon.style.opacity = hasValue ? '0.5' : '1';
            }
        });

        // Clear search functionality
        window.clearSearch = () => {
            this.searchInput.value = '';
            this.searchInput.dispatchEvent(new Event('input'));
            this.searchInput.focus();

            // Trigger HTMX to refresh results
            htmx.trigger(this.searchInput, 'keyup');
        };
    }

    // Form validation and character counting
    setupFormValidation() {
        if (!this.form) return;

        const nameInput = this.form.querySelector('#workflow-name');
        const descriptionTextarea = this.form.querySelector('#workflow-description');
        const descriptionCount = this.form.querySelector('#description-count');

        // Character counting for description
        if (descriptionTextarea && descriptionCount) {
            const updateCount = () => {
                const count = descriptionTextarea.value.length;
                descriptionCount.textContent = count;

                // Add warning class if approaching limit
                const countContainer = descriptionCount.closest('.character-count');
                if (count > 450) {
                    countContainer.classList.add('warning');
                } else {
                    countContainer.classList.remove('warning');
                }
            };

            descriptionTextarea.addEventListener('input', updateCount);
            updateCount(); // Initialize count
        }

        // Real-time validation
        if (nameInput) {
            nameInput.addEventListener('input', () => {
                this.validateField(nameInput);
            });
        }
    }

    // Dialog event handling
    setupDialogEvents() {
        if (!this.dialog) return;

        // Close on backdrop click
        const backdrop = this.dialog.querySelector('.dialog-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => this.hideDialog());
        }

        // Close on Escape key
        this.dialog.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideDialog();
            }
        });

        // Prevent form submission on Enter in input fields (except textarea)
        this.form?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.type !== 'submit') {
                e.preventDefault();
            }
        });
    }

    // Field validation
    validateField(field) {
        const errorDiv = field.parentNode.querySelector('.form-error');
        let isValid = true;
        let errorMessage = '';

        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
            errorMessage = 'This field is required';
        } else if (field.type === 'text' && field.value.trim().length < 2) {
            isValid = false;
            errorMessage = 'Name must be at least 2 characters long';
        }

        // Update UI
        if (errorDiv) {
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = isValid ? 'none' : 'block';
        }

        field.classList.toggle('error', !isValid);
        return isValid;
    }

    // Show dialog
    showDialog() {
        if (!this.dialog) return;

        this.dialog.showModal();
        document.body.classList.add('dialog-open');

        // Focus first input
        const firstInput = this.form?.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    // Hide dialog
    hideDialog() {
        if (!this.dialog) return;

        this.dialog.close();
        document.body.classList.remove('dialog-open');
        this.resetForm();
    }

    // Reset form
    resetForm() {
        if (!this.form) return;

        this.form.reset();

        // Reset validation states
        this.form.querySelectorAll('.form-error').forEach(error => {
            error.style.display = 'none';
        });

        this.form.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
        });

        // Reset character count
        const descriptionCount = this.form.querySelector('#description-count');
        if (descriptionCount) {
            descriptionCount.textContent = '0';
            descriptionCount.closest('.character-count')?.classList.remove('warning');
        }
    }

    // Handle form submission
    async handleSubmit(event) {
        event.preventDefault();

        const submitBtn = this.form.querySelector('#create-submit-btn');
        const btnContent = submitBtn?.querySelector('.btn-content');
        const btnLoading = submitBtn?.querySelector('.btn-loading');

        // Validate all fields
        const nameInput = this.form.querySelector('#workflow-name');
        const isValid = this.validateField(nameInput);

        if (!isValid) {
            nameInput.focus();
            return;
        }

        // Show loading state
        if (submitBtn && btnContent && btnLoading) {
            submitBtn.disabled = true;
            btnContent.style.display = 'none';
            btnLoading.style.display = 'flex';
        }

        try {
            // Simulate API call (replace with actual implementation)
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Success - close dialog and show success message
            this.hideDialog();
            this.showSuccessMessage('Workflow created successfully!');

            // Refresh workflow list (trigger HTMX or reload)
            this.refreshWorkflowList();

        } catch (error) {
            console.error('Failed to create workflow:', error);
            this.showErrorMessage('Failed to create workflow. Please try again.');
        } finally {
            // Reset loading state
            if (submitBtn && btnContent && btnLoading) {
                submitBtn.disabled = false;
                btnContent.style.display = 'flex';
                btnLoading.style.display = 'none';
            }
        }
    }

    // Show success message
    showSuccessMessage(message) {
        // You can implement a toast notification system here
        console.log('Success:', message);
    }

    // Show error message
    showErrorMessage(message) {
        // You can implement a toast notification system here
        console.error('Error:', message);
    }

    // Refresh workflow list
    refreshWorkflowList() {
        // Trigger HTMX refresh or page reload
        if (this.searchInput) {
            htmx.trigger(this.searchInput, 'keyup');
        }
    }
}

// Workflow detail functions
function runWorkflow(element) {
    const workflowName = element.closest('tr').querySelector('.workflow-name')?.textContent;
    alert(`Triggering workflow: ${workflowName}`);
}

function showDetail(element) {
    const detail = document.getElementById("workflow-content-article-detail");
    const detailTemplate = document.getElementById("workflow-detail-skeleton");

    if (detail && detailTemplate) {
        detail.innerHTML = "";
        detail.appendChild(detailTemplate.content.cloneNode(true));

        document.getElementById('workflow-content-article')?.classList.add('with-detail');
        document.getElementById('workflow-content-article-detail')?.classList.add('active');
        element.closest('tr')?.classList.add('active');
    }
}

function hideDetail() {
    document.getElementById('workflow-content-article')?.classList.remove('with-detail');
    document.getElementById('workflow-content-article-detail')?.classList.remove('active');

    const rows = document.querySelectorAll('#workflow-results tr');
    rows.forEach(row => row.classList.remove('active'));
}

function toggleHistoryDetails(header) {
    const details = header.nextElementSibling;
    details?.classList.toggle('open');
}

function refreshWorkflows() {
    const searchInput = document.querySelector('input[name="search_text"]');
    if (searchInput) {
        htmx.trigger(searchInput, 'keyup');
    }
}

// Initialize workflow manager
let workflowManager;

document.addEventListener('DOMContentLoaded', () => {
    workflowManager = new WorkflowManager();
});

// Global functions for backward compatibility
window.showCreateDialog = (show) => {
    if (show) {
        workflowManager?.showDialog();
    } else {
        workflowManager?.hideDialog();
    }
};

window.hideCreateDialog = () => workflowManager?.hideDialog();

window.handleCreateWorkflow = (event) => workflowManager?.handleSubmit(event);

// HTMX event handlers
document.addEventListener('htmx:beforeRequest', (event) => {
    if (event.detail.elt.name === 'search_text') {
        const searchContainer = event.detail.elt.closest('.search-container');
        const loadingIndicator = searchContainer?.querySelector('.search-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
    }
});

document.addEventListener('htmx:afterRequest', (event) => {
    if (event.detail.elt.name === 'search_text') {
        const searchContainer = event.detail.elt.closest('.search-container');
        const loadingIndicator = searchContainer?.querySelector('.search-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
});

// Detail Tab switching
document.body.addEventListener('htmx:afterSwap', function (event) {
    document.querySelectorAll('.detail-tab .tab').forEach(tab => {
        tab.addEventListener('click', function() {
            // Update active tab
            document.querySelectorAll('.detail-tab .tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding content
            const tabId = this.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabId + '-tab')?.classList.add('active');
        });
    });
});
