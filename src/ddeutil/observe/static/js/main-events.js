function runWorkflow(element) {
    const workflowName = element.closest('tr').querySelector('.workflow-name').textContent;
    alert(`Triggering workflow: ${workflowName}`);
}

function showDetail() {
    document.getElementById('workflow-content-article').classList.add('with-detail');
    document.getElementById('workflow-content-article-detail').classList.add('active');

    // Re-render Mermaid diagram
    mermaid.init(undefined, document.getElementById('mermaid-diagram'));
}

function hideDetail() {
    document.getElementById('workflow-content-article').classList.remove('with-detail');
    document.getElementById('workflow-content-article-detail').classList.remove('active');
}
