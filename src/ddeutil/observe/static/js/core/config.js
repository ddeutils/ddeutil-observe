/**
 * Application Configuration
 * =========================
 * Centralized configuration for the Observe application.
 * 
 * Usage:
 * - Import this module to access configuration values
 * - Modify values here to change application behavior
 * - Environment-specific overrides can be applied
 * 
 * @version 1.0.0
 * @author ddeutil-observe
 */

/**
 * Application configuration object
 */
export const Config = {
    // Application metadata
    app: {
        name: 'Observe',
        version: '1.0.0',
        environment: 'development', // development, staging, production
        debug: true,
    },

    // API configuration
    api: {
        baseUrl: '',
        timeout: 30000, // 30 seconds
        retryAttempts: 3,
        retryDelay: 1000, // 1 second
    },

    // UI configuration
    ui: {
        // Theme settings
        theme: {
            defaultTheme: 'light',
            storageKey: 'observe-theme',
            autoDetect: true, // Auto-detect system preference
        },

        // Animation settings
        animation: {
            duration: {
                fast: 150,
                normal: 250,
                slow: 350,
            },
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            respectReducedMotion: true,
        },

        // Layout settings
        layout: {
            sidebar: {
                width: 220,
                collapsedWidth: 60,
                breakpoint: 768,
                storageKey: 'observe-sidebar-collapsed',
            },
            header: {
                height: 60,
                sticky: true,
            },
        },

        // Notification settings
        notifications: {
            position: 'top-right',
            duration: 5000,
            maxVisible: 5,
            enableSound: false,
        },

        // Loading states
        loading: {
            minDuration: 300, // Minimum loading time to prevent flicker
            showSpinner: true,
            showProgress: false,
        },
    },

    // HTMX configuration
    htmx: {
        timeout: 30000,
        defaultHeaders: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        indicators: {
            defaultClass: 'htmx-loading',
            spinnerClass: 'spinner',
        },
    },

    // Form configuration
    forms: {
        validation: {
            realtime: true,
            debounceDelay: 300,
            showErrors: true,
            scrollToError: true,
        },
        submission: {
            preventDoubleSubmit: true,
            showLoadingState: true,
            confirmDangerous: true,
        },
    },

    // Search configuration
    search: {
        debounceDelay: 750,
        minLength: 0,
        showNoResults: true,
        maxResults: 50,
    },

    // Table configuration
    tables: {
        pagination: {
            defaultPageSize: 25,
            pageSizes: [10, 25, 50, 100],
            showInfo: true,
        },
        sorting: {
            defaultDirection: 'asc',
            showIndicators: true,
        },
    },

    // Modal/Dialog configuration
    modals: {
        closeOnBackdropClick: true,
        closeOnEscape: true,
        focusFirstElement: true,
        preventBodyScroll: true,
        animationDuration: 250,
    },

    // Dropdown configuration
    dropdowns: {
        closeOnOutsideClick: true,
        closeOnEscape: true,
        closeOnItemClick: true,
        keyboardNavigation: true,
        animationDuration: 200,
    },

    // Performance monitoring
    performance: {
        enabled: true,
        sampleRate: 1.0, // 100% sampling in development
        logToConsole: true,
        trackPageLoadTime: true,
        trackUserInteractions: true,
    },

    // Error handling
    errors: {
        showToUser: true,
        logToConsole: true,
        reportToServer: false,
        fallbackMessage: 'An unexpected error occurred. Please try again.',
    },

    // Accessibility
    accessibility: {
        announceChanges: true,
        focusManagement: true,
        keyboardNavigation: true,
        highContrastSupport: true,
        reducedMotionSupport: true,
    },

    // Storage configuration
    storage: {
        prefix: 'observe-',
        type: 'localStorage', // localStorage, sessionStorage
        encryption: false,
    },

    // Workflow-specific configuration
    workflow: {
        autoRefresh: false,
        refreshInterval: 30000, // 30 seconds
        showDetailOnSelect: true,
        confirmDelete: true,
        maxHistoryItems: 100,
    },

    // Development tools
    dev: {
        showDebugInfo: false,
        mockApiCalls: false,
        slowNetwork: false,
        logLevel: 'info', // error, warn, info, debug
    },
};

/**
 * Environment-specific configuration overrides
 */
const environmentConfigs = {
    production: {
        app: {
            debug: false,
        },
        performance: {
            sampleRate: 0.1, // 10% sampling in production
            logToConsole: false,
        },
        errors: {
            logToConsole: false,
            reportToServer: true,
        },
        dev: {
            showDebugInfo: false,
            logLevel: 'error',
        },
    },
    staging: {
        app: {
            debug: true,
        },
        performance: {
            sampleRate: 0.5, // 50% sampling in staging
        },
        dev: {
            logLevel: 'warn',
        },
    },
};

/**
 * Apply environment-specific overrides
 */
function applyEnvironmentConfig() {
    const envConfig = environmentConfigs[Config.app.environment];
    if (envConfig) {
        deepMerge(Config, envConfig);
    }
}

/**
 * Deep merge utility function
 */
function deepMerge(target, source) {
    for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            if (!target[key]) target[key] = {};
            deepMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

/**
 * Get configuration value with dot notation
 * @param {string} path - Dot notation path (e.g., 'ui.theme.defaultTheme')
 * @param {any} defaultValue - Default value if path not found
 * @returns {any} Configuration value
 */
export function getConfig(path, defaultValue = null) {
    return path.split('.').reduce((obj, key) => (obj && obj[key] !== undefined) ? obj[key] : defaultValue, Config);
}

/**
 * Set configuration value with dot notation
 * @param {string} path - Dot notation path
 * @param {any} value - Value to set
 */
export function setConfig(path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    const target = keys.reduce((obj, key) => {
        if (!obj[key]) obj[key] = {};
        return obj[key];
    }, Config);
    target[lastKey] = value;
}

/**
 * Check if we're in development mode
 * @returns {boolean}
 */
export function isDevelopment() {
    return Config.app.environment === 'development';
}

/**
 * Check if we're in production mode
 * @returns {boolean}
 */
export function isProduction() {
    return Config.app.environment === 'production';
}

/**
 * Get debug mode status
 * @returns {boolean}
 */
export function isDebug() {
    return Config.app.debug;
}

/**
 * Log configuration
 */
export function logConfig() {
    if (Config.app.debug) {
        console.group('📋 Application Configuration');
        console.table(Config.app);
        console.groupEnd();
    }
}

// Apply environment configuration on module load
applyEnvironmentConfig();

// Export the main configuration object as default
export default Config; 