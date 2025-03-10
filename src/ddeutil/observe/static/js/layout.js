// Theme Toggle Functionality
document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

document.body.addEventListener('htmx:afterOnLoad', function(event) {
    if (event.detail.pathInfo.requestPath === '/toggle-sidebar') {
        document.getElementById('sidebar').classList.toggle('collapsed');
        document.getElementById('main-content').classList.toggle('expanded');
    }

    if (event.detail.pathInfo.requestPath === '/toggle-theme') {
        const themeIcon = document.querySelector('#theme-toggle i');
        themeIcon.className = document.body.dataset.theme === 'light' ? 'bx bx-sun' : 'bx bx-moon';
    }
});

// Check for saved theme preference
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }

    // Start with collapsed sidebar on mobile
    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.add('collapsed');
        document.getElementById('main-content').classList.add('expanded');
    }

});
