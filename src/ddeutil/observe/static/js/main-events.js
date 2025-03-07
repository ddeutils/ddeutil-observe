// Add event listeners for any run buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.run-btn').forEach(button => {
        button.addEventListener('click', function() {
            const workflowName = this.closest('tr').querySelector('.workflow-name').textContent;
            alert(`Triggering workflow: ${workflowName}`);
            // In a real app, this would trigger an API call to run the workflow
        });
    });
});
