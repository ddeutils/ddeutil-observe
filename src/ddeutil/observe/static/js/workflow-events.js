function runWorkflow(element) {
    const workflowName = element.closest('tr').querySelector('.workflow-name').textContent;
    alert(`Triggering workflow: ${workflowName}`);
}

function showDetail(element) {
    document.getElementById('workflow-content-article').classList.add('with-detail');
    document.getElementById('workflow-content-article-detail').classList.add('active');
    element.closest('tr').classList.add('active');
}

function hideDetail() {
    document.getElementById('workflow-content-article').classList.remove('with-detail');
    document.getElementById('workflow-content-article-detail').classList.remove('active');

    const rows = document.querySelectorAll('#workflow-results tr');
    rows.forEach(row => row.classList.remove('active'));
}

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
            document.getElementById(tabId + '-tab').classList.add('active');

        });
    });
});


function toggleHistoryDetails(header) {
    const details = header.nextElementSibling;
    details.classList.toggle('open');
}
