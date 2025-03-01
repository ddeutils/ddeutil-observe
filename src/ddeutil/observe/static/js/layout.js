//const body = document.querySelector("body");
//const darkLight = document.querySelector("#darkLight");
//
//// NOTE: Dark Mode
//darkLight.addEventListener("click", () => {
//    body.classList.toggle("dark");
//    if (body.classList.contains("dark")) {
//        document.setI
//        darkLight.classList.replace("bx-sun", "bx-moon");
//    } else {
//        darkLight.classList.replace("bx-moon", "bx-sun");
//    }
//});

// Theme Toggle Functionality
document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Check for saved theme preference
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
});
