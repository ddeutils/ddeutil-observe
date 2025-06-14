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

// Enhanced Notification Manager
class NotificationManager {
    constructor() {
        this.isDropdownOpen = false;
        this.badge = document.getElementById('notification-count');
        this.init();
    }

    init() {
        this.loadUnreadCount();
        this.setupEventListeners();

        // Auto-refresh every 30 seconds
        setInterval(() => {
            if (!this.isDropdownOpen) {
                this.loadUnreadCount();
            }
        }, 30000);
    }

    setupEventListeners() {
        // Listen for HTMX events to refresh count
        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.xhr.responseURL?.includes('/notifications/')) {
                this.loadUnreadCount();
            }
        });

        // Handle notification dropdown close events
        document.addEventListener('click', (event) => {
            const dropdown = document.querySelector('.notification-dropdown');
            if (dropdown && !dropdown.contains(event.target) && this.isDropdownOpen) {
                this.closeDropdown();
            }
        });
    }

    async loadUnreadCount() {
        try {
            const response = await fetch('/notifications/count?user_id=observe');
            const data = await response.json();
            this.updateBadge(data.unread_count);
        } catch (error) {
            console.error('Failed to load notification count:', error);
            // Fallback to mock data if API fails
            this.updateBadge(4);
        }
    }

    updateBadge(count) {
        if (this.badge) {
            this.badge.textContent = count;
            this.badge.classList.toggle('has-notifications', count > 0);

            // Update accessibility
            const button = this.badge.closest('.notification-btn');
            if (button) {
                const label = count > 0
                    ? `View ${count} notification${count === 1 ? '' : 's'}`
                    : 'No new notifications';
                button.setAttribute('aria-label', label);
            }
        }
    }

    toggleDropdown(button) {
        const dropdown = button.closest('.notification-dropdown');
        const menu = dropdown?.querySelector('.notification-menu');

        if (!menu) return;

        this.isDropdownOpen = !this.isDropdownOpen;

        menu.setAttribute('aria-hidden', (!this.isDropdownOpen).toString());
        button.setAttribute('aria-expanded', this.isDropdownOpen.toString());

        if (this.isDropdownOpen) {
            dropdown.classList.add('open');

            // Close other dropdowns
            document.querySelectorAll('.action-dropdown.open').forEach(dd => {
                if (dd !== dropdown) {
                    dd.classList.remove('open');
                }
            });

            // Close on escape key
            const handleEscape = (event) => {
                if (event.key === 'Escape') {
                    this.closeDropdown();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);

        } else {
            dropdown.classList.remove('open');
        }
    }

    closeDropdown() {
        const dropdown = document.querySelector('.notification-dropdown');
        const button = dropdown?.querySelector('.notification-btn');
        const menu = dropdown?.querySelector('.notification-menu');

        if (dropdown && button && menu) {
            this.isDropdownOpen = false;
            dropdown.classList.remove('open');
            menu.setAttribute('aria-hidden', 'true');
            button.setAttribute('aria-expanded', 'false');
        }
    }

    // Method to add new notification (for real-time updates)
    addNotification(notification) {
        console.log('New notification received:', notification);
        this.loadUnreadCount();

        // Show brief notification toast if needed
        this.showToast(notification);
    }

    showToast(notification) {
        // Create a brief toast notification for new alerts
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <div class="toast-icon ${notification.color}">
                <i class="bx ${notification.icon}"></i>
            </div>
            <div class="toast-content">
                <strong>${notification.title}</strong>
                <p>${notification.message}</p>
            </div>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);

        // Remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 5000);
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
window.toggleNotificationDropdown = (button) => notificationManager.toggleDropdown(button);

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
        // Use a more reliable approach with proper timing checks
        setTimeout(() => {
            try {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation && navigation.loadEventEnd > 0) {
                    const loadTime = navigation.loadEventEnd - navigation.navigationStart;
                    console.log(`Page load time: ${Math.round(loadTime)}ms`);
                } else {
                    // Fallback to simple timing
                    const loadTime = performance.now();
                    console.log(`Page ready time: ${Math.round(loadTime)}ms`);
                }
            } catch (error) {
                console.log('Performance monitoring not available');
            }
        }, 100); // Small delay to ensure load event has completed
    });
}
