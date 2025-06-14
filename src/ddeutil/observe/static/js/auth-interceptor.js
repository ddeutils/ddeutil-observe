// Authentication Interceptor
// Handles global authentication errors and redirects to login page

(function() {
    'use strict';

    // Store original fetch
    const originalFetch = window.fetch;

    // Override global fetch to intercept authentication errors
    window.fetch = async function(...args) {
        try {
            const response = await originalFetch.apply(this, args);

            // Check for authentication errors
            if (response.status === 401) {
                // Try to parse response as JSON to check for specific error message
                try {
                    const clonedResponse = response.clone();
                    const errorData = await clonedResponse.json();

                    if (errorData.detail === "Could not validate credentials" ||
                        errorData.detail === "Not authenticated") {
                        handleAuthenticationError();
                        return response;
                    }
                } catch (e) {
                    // If not JSON, still handle 401 (might be HTML response)
                    handleAuthenticationError();
                    return response;
                }
            }

            // Check for redirects to login page (in case server redirects)
            if (response.redirected && response.url.includes('/auth/login')) {
                handleAuthenticationError();
                return response;
            }

            return response;
        } catch (error) {
            throw error;
        }
    };

    // Handle HTMX responses for authentication errors
    document.addEventListener('htmx:responseError', function(event) {
        if (event.detail.xhr.status === 401) {
            try {
                const errorData = JSON.parse(event.detail.xhr.responseText);
                if (errorData.detail === "Could not validate credentials" ||
                    errorData.detail === "Not authenticated") {
                    handleAuthenticationError();
                }
            } catch (e) {
                // If not JSON, still handle 401
                handleAuthenticationError();
            }
        }
    });

    // Handle XMLHttpRequest for any legacy AJAX calls
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        this._url = url;
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(data) {
        const xhr = this;

        xhr.addEventListener('load', function() {
            if (xhr.status === 401) {
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    if (errorData.detail === "Could not validate credentials" ||
                        errorData.detail === "Not authenticated") {
                        handleAuthenticationError();
                    }
                } catch (e) {
                    // If not JSON, still handle 401
                    handleAuthenticationError();
                }
            }
        });

        return originalXHRSend.apply(this, arguments);
    };

    // Global error handler for unhandled authentication errors
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.message &&
            event.reason.message.includes('Could not validate credentials')) {
            handleAuthenticationError();
        }
    });

    function handleAuthenticationError() {
        // Prevent multiple redirects
        if (window.location.pathname === '/auth/login') {
            return;
        }

        // Show notification before redirect (optional)
        showAuthErrorNotification();

        // Clear any stored tokens
        clearAuthTokens();

        // Redirect to login page
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 1000); // Small delay to show notification
    }

    function showAuthErrorNotification() {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = 'auth-error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bx bx-lock"></i>
                <span>Session expired. Redirecting to login...</span>
            </div>
        `;

        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            padding: 1rem 1.5rem;
            background: rgba(239, 68, 68, 0.15);
            color: #dc2626;
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 6px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.875rem;
            font-weight: 500;
            animation: slideInAuth 0.3s ease;
            max-width: 350px;
        `;

        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInAuth {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            .auth-error-notification .notification-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .auth-error-notification i {
                font-size: 1.125rem;
                flex-shrink: 0;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(notification);

        // Auto-remove notification
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
            if (style.parentElement) {
                style.remove();
            }
        }, 5000);
    }

    function clearAuthTokens() {
        // Clear tokens from localStorage
        try {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('token');
        } catch (e) {
            // Ignore localStorage errors
        }

        // Clear tokens from sessionStorage
        try {
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('refresh_token');
            sessionStorage.removeItem('token');
        } catch (e) {
            // Ignore sessionStorage errors
        }

        // Clear auth cookies by setting them to expire
        try {
            document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        } catch (e) {
            // Ignore cookie errors
        }
    }

    // Check if we're on login page due to authentication failure
    function checkInitialAuthState() {
        // If we're on login page and there's a referrer that's not login,
        // it might be due to auth failure
        if (window.location.pathname === '/auth/login' &&
            document.referrer &&
            !document.referrer.includes('/auth/login') &&
            !document.referrer.includes('/auth/register')) {

            // Clear tokens since we were redirected here
            clearAuthTokens();

            // Show a brief notification
            setTimeout(() => {
                showAuthErrorNotification();
            }, 500);
        }
    }

    // Initialize
    console.log('Authentication interceptor initialized');

    // Check initial state when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkInitialAuthState);
    } else {
        checkInitialAuthState();
    }
})();
