// Enhanced Event Management for Better UX and Accessibility

// Dropdown Management
class DropdownManager {
    constructor() {
        this.activeDropdown = null;
        this.init();
    }

    init() {
        // Initialize dropdown triggers
        document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
            trigger.addEventListener('click', (e) => this.toggleDropdown(e));
            trigger.addEventListener('keydown', (e) => this.handleKeydown(e));
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAllDropdowns();
        });
    }

    toggleDropdown(event) {
        event.preventDefault();
        event.stopPropagation();

        const trigger = event.currentTarget;
        const dropdown = trigger.closest('.action-dropdown');

        if (this.activeDropdown && this.activeDropdown !== dropdown) {
            this.closeDropdown(this.activeDropdown);
        }

        if (dropdown.classList.contains('open')) {
            this.closeDropdown(dropdown);
        } else {
            this.openDropdown(dropdown);
        }
    }

    openDropdown(dropdown) {
        dropdown.classList.add('open');
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');

        trigger.setAttribute('aria-expanded', 'true');
        menu.setAttribute('aria-hidden', 'false');

        // Focus first menu item
        const firstItem = menu.querySelector('.dropdown-item');
        if (firstItem) {
            setTimeout(() => firstItem.focus(), 100);
        }

        this.activeDropdown = dropdown;
    }

    closeDropdown(dropdown) {
        dropdown.classList.remove('open');
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');

        trigger.setAttribute('aria-expanded', 'false');
        menu.setAttribute('aria-hidden', 'true');

        if (this.activeDropdown === dropdown) {
            this.activeDropdown = null;
        }
    }

    closeAllDropdowns() {
        document.querySelectorAll('.action-dropdown.open').forEach(dropdown => {
            this.closeDropdown(dropdown);
        });
    }

    handleOutsideClick(event) {
        if (this.activeDropdown && !this.activeDropdown.contains(event.target)) {
            this.closeDropdown(this.activeDropdown);
        }
    }

    handleKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.toggleDropdown(event);
        }
    }
}

// Notification Manager
class NotificationManager {
    constructor() {
        this.init();
    }

    init() {
        // Simulate notification updates
        this.updateNotificationCount();

        // Handle notification click
        const notificationBtn = document.querySelector('.notification-btn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => this.showNotifications());
        }
    }

    updateNotificationCount(count = 3) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    showNotifications() {
        // This would typically show a notification panel
        console.log('Show notifications panel');
        // For now, just hide the badge
        this.updateNotificationCount(0);
    }
}

// Enhanced Theme Management
class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        // Apply saved theme on page load
        this.applySavedTheme();

        // Update theme toggle icon
        this.updateThemeIcon();
    }

    applySavedTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
    }

    updateThemeIcon() {
        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            const currentTheme = document.body.getAttribute('data-theme');
            themeIcon.className = currentTheme === 'light' ? 'bx bx-sun' : 'bx bx-moon';
        }
    }

    toggle() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon();

        // Announce theme change for screen readers
        this.announceThemeChange(newTheme);
    }

    announceThemeChange(theme) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = `Theme changed to ${theme} mode`;

        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
    }
}

// Loading State Manager
class LoadingManager {
    constructor() {
        this.activeRequests = 0;
    }

    show(element) {
        element.classList.add('loading');
        this.activeRequests++;
        this.updateGlobalLoader();
    }

    hide(element) {
        element.classList.remove('loading');
        this.activeRequests = Math.max(0, this.activeRequests - 1);
        this.updateGlobalLoader();
    }

    updateGlobalLoader() {
        const loader = document.querySelector('.global-loader');
        if (loader) {
            loader.style.display = this.activeRequests > 0 ? 'block' : 'none';
        }
    }
}

// Initialize managers
const dropdownManager = new DropdownManager();
const notificationManager = new NotificationManager();
const themeManager = new ThemeManager();
const loadingManager = new LoadingManager();

// Global functions for backward compatibility
window.themeToggle = () => themeManager.toggle();

// Enhanced HTMX integration
document.addEventListener('htmx:beforeRequest', function(event) {
    loadingManager.show(event.target);
});

document.addEventListener('htmx:afterRequest', function(event) {
    loadingManager.hide(event.target);
});

// Handle dropdown menu keyboard navigation
document.addEventListener('keydown', function(event) {
    if (dropdownManager.activeDropdown) {
        const menuItems = dropdownManager.activeDropdown.querySelectorAll('.dropdown-item');
        const currentFocus = document.activeElement;
        const currentIndex = Array.from(menuItems).indexOf(currentFocus);

        switch(event.key) {
            case 'ArrowDown':
                event.preventDefault();
                const nextIndex = (currentIndex + 1) % menuItems.length;
                menuItems[nextIndex].focus();
                break;
            case 'ArrowUp':
                event.preventDefault();
                const prevIndex = currentIndex <= 0 ? menuItems.length - 1 : currentIndex - 1;
                menuItems[prevIndex].focus();
                break;
            case 'Enter':
            case ' ':
                if (currentFocus.classList.contains('dropdown-item')) {
                    event.preventDefault();
                    currentFocus.click();
                }
                break;
        }
    }
});

// Performance monitoring
if ('performance' in window && 'measure' in performance) {
    window.addEventListener('load', () => {
        performance.measure('page-load-time', 'navigationStart', 'loadEventEnd');
        const measure = performance.getEntriesByName('page-load-time')[0];
        console.log(`Page load time: ${Math.round(measure.duration)}ms`);
    });
}
