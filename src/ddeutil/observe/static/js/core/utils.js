/**
 * Utility Functions
 * =================
 * Common utility functions for the Observe application.
 * 
 * @version 1.0.0
 * @author ddeutil-observe
 */

/**
 * DOM Utilities
 */
export const DOM = {
    /**
     * Safe query selector
     * @param {string} selector - CSS selector
     * @param {Element} parent - Parent element (default: document)
     * @returns {Element|null}
     */
    $(selector, parent = document) {
        try {
            return parent.querySelector(selector);
        } catch (error) {
            console.warn(`Invalid selector: ${selector}`, error);
            return null;
        }
    },

    /**
     * Safe query selector all
     * @param {string} selector - CSS selector
     * @param {Element} parent - Parent element (default: document)
     * @returns {NodeList}
     */
    $$(selector, parent = document) {
        try {
            return parent.querySelectorAll(selector);
        } catch (error) {
            console.warn(`Invalid selector: ${selector}`, error);
            return [];
        }
    },

    /**
     * Create element with attributes and content
     * @param {string} tag - HTML tag name
     * @param {Object} attributes - Element attributes
     * @param {string|Element|Array} content - Element content
     * @returns {Element}
     */
    create(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className' || key === 'class') {
                element.className = value;
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    element.dataset[dataKey] = dataValue;
                });
            } else if (key.startsWith('aria-') || key.startsWith('data-')) {
                element.setAttribute(key, value);
            } else {
                element[key] = value;
            }
        });

        if (content) {
            if (typeof content === 'string') {
                element.textContent = content;
            } else if (content instanceof Element) {
                element.appendChild(content);
            } else if (Array.isArray(content)) {
                content.forEach(item => {
                    if (typeof item === 'string') {
                        element.appendChild(document.createTextNode(item));
                    } else if (item instanceof Element) {
                        element.appendChild(item);
                    }
                });
            }
        }

        return element;
    },

    /**
     * Check if element is visible
     * @param {Element} element - Element to check
     * @returns {boolean}
     */
    isVisible(element) {
        if (!element) return false;
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0';
    },

    /**
     * Get element's offset relative to document
     * @param {Element} element - Element
     * @returns {Object} {top, left, width, height}
     */
    getOffset(element) {
        if (!element) return { top: 0, left: 0, width: 0, height: 0 };
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height
        };
    },

    /**
     * Smooth scroll to element
     * @param {Element|string} target - Element or selector
     * @param {Object} options - Scroll options
     */
    scrollTo(target, options = {}) {
        const element = typeof target === 'string' ? this.$(target) : target;
        if (!element) return;

        const defaults = {
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
        };

        element.scrollIntoView({ ...defaults, ...options });
    },

    /**
     * Add event listener with automatic cleanup
     * @param {Element} element - Element
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @param {Object} options - Event options
     * @returns {Function} Cleanup function
     */
    on(element, event, handler, options = {}) {
        element.addEventListener(event, handler, options);
        return () => element.removeEventListener(event, handler, options);
    },

    /**
     * Delegate event listener
     * @param {Element} parent - Parent element
     * @param {string} selector - Child selector
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @returns {Function} Cleanup function
     */
    delegate(parent, selector, event, handler) {
        const delegatedHandler = (e) => {
            const target = e.target.closest(selector);
            if (target && parent.contains(target)) {
                handler.call(target, e);
            }
        };

        parent.addEventListener(event, delegatedHandler);
        return () => parent.removeEventListener(event, delegatedHandler);
    }
};

/**
 * String Utilities
 */
export const Str = {
    /**
     * Capitalize first letter
     * @param {string} str - String to capitalize
     * @returns {string}
     */
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Convert to kebab-case
     * @param {string} str - String to convert
     * @returns {string}
     */
    kebabCase(str) {
        if (!str) return '';
        return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    },

    /**
     * Convert to camelCase
     * @param {string} str - String to convert
     * @returns {string}
     */
    camelCase(str) {
        if (!str) return '';
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    },

    /**
     * Truncate string with ellipsis
     * @param {string} str - String to truncate
     * @param {number} length - Max length
     * @param {string} suffix - Suffix (default: '...')
     * @returns {string}
     */
    truncate(str, length, suffix = '...') {
        if (!str || str.length <= length) return str;
        return str.substring(0, length) + suffix;
    },

    /**
     * Generate random string
     * @param {number} length - String length
     * @param {string} chars - Character set
     * @returns {string}
     */
    random(length = 8, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },

    /**
     * Escape HTML
     * @param {string} str - String to escape
     * @returns {string}
     */
    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};

/**
 * Array Utilities
 */
export const Arr = {
    /**
     * Remove item from array
     * @param {Array} array - Array
     * @param {*} item - Item to remove
     * @returns {Array} New array
     */
    remove(array, item) {
        return array.filter(x => x !== item);
    },

    /**
     * Get unique items from array
     * @param {Array} array - Array
     * @returns {Array} Unique items
     */
    unique(array) {
        return [...new Set(array)];
    },

    /**
     * Chunk array into smaller arrays
     * @param {Array} array - Array to chunk
     * @param {number} size - Chunk size
     * @returns {Array} Array of chunks
     */
    chunk(array, size) {
        const chunks = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    },

    /**
     * Group array by key
     * @param {Array} array - Array to group
     * @param {string|Function} key - Grouping key or function
     * @returns {Object} Grouped object
     */
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = typeof key === 'function' ? key(item) : item[key];
            if (!groups[group]) groups[group] = [];
            groups[group].push(item);
            return groups;
        }, {});
    }
};

/**
 * Object Utilities
 */
export const Obj = {
    /**
     * Deep clone object
     * @param {Object} obj - Object to clone
     * @returns {Object} Cloned object
     */
    clone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    /**
     * Deep merge objects
     * @param {Object} target - Target object
     * @param {...Object} sources - Source objects
     * @returns {Object} Merged object
     */
    merge(target, ...sources) {
        for (const source of sources) {
            for (const key in source) {
                if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                    if (!target[key]) target[key] = {};
                    this.merge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
        }
        return target;
    },

    /**
     * Get nested property value
     * @param {Object} obj - Object
     * @param {string} path - Dot notation path
     * @param {*} defaultValue - Default value
     * @returns {*} Property value
     */
    get(obj, path, defaultValue = undefined) {
        return path.split('.').reduce((current, key) => 
            current && current[key] !== undefined ? current[key] : defaultValue, obj
        );
    },

    /**
     * Set nested property value
     * @param {Object} obj - Object
     * @param {string} path - Dot notation path
     * @param {*} value - Value to set
     * @returns {Object} Modified object
     */
    set(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!current[key]) current[key] = {};
            return current[key];
        }, obj);
        target[lastKey] = value;
        return obj;
    },

    /**
     * Check if object is empty
     * @param {Object} obj - Object to check
     * @returns {boolean}
     */
    isEmpty(obj) {
        return Object.keys(obj).length === 0;
    }
};

/**
 * Storage Utilities
 */
export const Storage = {
    /**
     * Get item from storage with JSON parsing
     * @param {string} key - Storage key
     * @param {*} defaultValue - Default value
     * @param {string} type - Storage type ('local' or 'session')
     * @returns {*} Stored value
     */
    get(key, defaultValue = null, type = 'local') {
        try {
            const storage = type === 'session' ? sessionStorage : localStorage;
            const item = storage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn(`Failed to get storage item: ${key}`, error);
            return defaultValue;
        }
    },

    /**
     * Set item in storage with JSON stringification
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     * @param {string} type - Storage type ('local' or 'session')
     * @returns {boolean} Success status
     */
    set(key, value, type = 'local') {
        try {
            const storage = type === 'session' ? sessionStorage : localStorage;
            storage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn(`Failed to set storage item: ${key}`, error);
            return false;
        }
    },

    /**
     * Remove item from storage
     * @param {string} key - Storage key
     * @param {string} type - Storage type ('local' or 'session')
     */
    remove(key, type = 'local') {
        try {
            const storage = type === 'session' ? sessionStorage : localStorage;
            storage.removeItem(key);
        } catch (error) {
            console.warn(`Failed to remove storage item: ${key}`, error);
        }
    },

    /**
     * Clear all items from storage
     * @param {string} type - Storage type ('local' or 'session')
     */
    clear(type = 'local') {
        try {
            const storage = type === 'session' ? sessionStorage : localStorage;
            storage.clear();
        } catch (error) {
            console.warn('Failed to clear storage', error);
        }
    }
};

/**
 * Function Utilities
 */
export const Fn = {
    /**
     * Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @param {boolean} immediate - Execute immediately
     * @returns {Function} Debounced function
     */
    debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    /**
     * Throttle function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Create function that can only be called once
     * @param {Function} func - Function
     * @returns {Function} Once function
     */
    once(func) {
        let called = false;
        let result;
        return function executedFunction(...args) {
            if (!called) {
                called = true;
                result = func.apply(this, args);
            }
            return result;
        };
    },

    /**
     * Sleep function
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

/**
 * Date Utilities
 */
export const Date = {
    /**
     * Format date
     * @param {Date|string|number} date - Date to format
     * @param {string} format - Format string
     * @returns {string} Formatted date
     */
    format(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';

        const pad = (num) => String(num).padStart(2, '0');
        
        return format
            .replace(/YYYY/g, d.getFullYear())
            .replace(/MM/g, pad(d.getMonth() + 1))
            .replace(/DD/g, pad(d.getDate()))
            .replace(/HH/g, pad(d.getHours()))
            .replace(/mm/g, pad(d.getMinutes()))
            .replace(/ss/g, pad(d.getSeconds()));
    },

    /**
     * Get relative time string
     * @param {Date|string|number} date - Date
     * @returns {string} Relative time
     */
    relative(date) {
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return `${seconds}s ago`;
    },

    /**
     * Check if date is today
     * @param {Date|string|number} date - Date to check
     * @returns {boolean}
     */
    isToday(date) {
        const d = new Date(date);
        const today = new Date();
        return d.toDateString() === today.toDateString();
    }
};

/**
 * URL Utilities
 */
export const URL = {
    /**
     * Parse query string
     * @param {string} search - Query string (default: window.location.search)
     * @returns {Object} Parsed parameters
     */
    parseQuery(search = window.location.search) {
        const params = new URLSearchParams(search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    },

    /**
     * Build query string
     * @param {Object} params - Parameters object
     * @returns {string} Query string
     */
    buildQuery(params) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                searchParams.append(key, value);
            }
        });
        return searchParams.toString();
    },

    /**
     * Update URL without page reload
     * @param {string} url - New URL
     * @param {string} title - Page title
     */
    push(url, title = '') {
        if (window.history && window.history.pushState) {
            window.history.pushState({}, title, url);
        }
    }
};

/**
 * Validation Utilities
 */
export const Validate = {
    /**
     * Check if value is email
     * @param {string} email - Email to validate
     * @returns {boolean}
     */
    email(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Check if value is URL
     * @param {string} url - URL to validate
     * @returns {boolean}
     */
    url(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Check if value is required
     * @param {*} value - Value to check
     * @returns {boolean}
     */
    required(value) {
        if (value === null || value === undefined) return false;
        if (typeof value === 'string') return value.trim().length > 0;
        if (Array.isArray(value)) return value.length > 0;
        return true;
    },

    /**
     * Check minimum length
     * @param {string} value - Value to check
     * @param {number} min - Minimum length
     * @returns {boolean}
     */
    minLength(value, min) {
        return value && value.length >= min;
    },

    /**
     * Check maximum length
     * @param {string} value - Value to check
     * @param {number} max - Maximum length
     * @returns {boolean}
     */
    maxLength(value, max) {
        return !value || value.length <= max;
    }
};

/**
 * CSS Class Utilities
 */
export const CSS = {
    /**
     * Build CSS class string
     * @param {Object|Array|string} classes - Classes to combine
     * @returns {string} CSS class string
     */
    classes(...args) {
        const result = [];
        
        args.forEach(arg => {
            if (!arg) return;
            
            if (typeof arg === 'string') {
                result.push(arg);
            } else if (Array.isArray(arg)) {
                result.push(...arg);
            } else if (typeof arg === 'object') {
                Object.entries(arg).forEach(([key, value]) => {
                    if (value) result.push(key);
                });
            }
        });
        
        return result.join(' ');
    },

    /**
     * Toggle CSS class
     * @param {Element} element - Element
     * @param {string} className - Class name
     * @param {boolean} force - Force add/remove
     */
    toggle(element, className, force) {
        if (!element) return;
        element.classList.toggle(className, force);
    },

    /**
     * Add CSS classes
     * @param {Element} element - Element
     * @param {...string} classNames - Class names
     */
    add(element, ...classNames) {
        if (!element) return;
        element.classList.add(...classNames);
    },

    /**
     * Remove CSS classes
     * @param {Element} element - Element
     * @param {...string} classNames - Class names
     */
    remove(element, ...classNames) {
        if (!element) return;
        element.classList.remove(...classNames);
    }
};

// Export all utilities as a single object
export default {
    DOM,
    Str,
    Arr,
    Obj,
    Storage,
    Fn,
    Date,
    URL,
    Validate,
    CSS
}; 