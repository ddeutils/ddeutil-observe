// Theme Toggle Functionality
document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

function themeToggle(){
    const themeIcon = document.querySelector('#theme-toggle i');
    themeIcon.className = document.body.dataset.theme === 'light' ? 'bx bx-sun' : 'bx bx-moon';
}

// Check for saved theme preference
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }

    // Start with collapsed sidebar on mobile
    if (window.innerWidth <= 768) {
        toggleSidebar()
    }

});
