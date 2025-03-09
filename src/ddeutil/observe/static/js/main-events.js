function runWorkflow(element) {
    const workflowName = element.closest('tr').querySelector('.workflow-name').textContent;
    alert(`Triggering workflow: ${workflowName}`);
}

function showDetail(element) {
    document.getElementById('workflow-content-article').classList.add('with-detail');
    document.getElementById('workflow-content-article-detail').classList.add('active');
    element.closest('tr').classList.add('active');

    // Re-render Mermaid diagram
    mermaid.init(undefined, document.getElementById('mermaid-diagram'));
}

function hideDetail() {
    document.getElementById('workflow-content-article').classList.remove('with-detail');
    document.getElementById('workflow-content-article-detail').classList.remove('active');

    const rows = document.querySelectorAll('#workflow-results tr');
    rows.forEach(row => row.classList.remove('active'));
}
