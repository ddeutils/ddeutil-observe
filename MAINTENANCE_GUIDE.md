# 🛠 Maintenance Guide - ddeutil-observe

This guide provides comprehensive instructions for maintaining, extending, and troubleshooting the **ddeutil-observe** application frontend.

## 📁 **Project Structure**

```
src/ddeutil/observe/
├── static/
│   ├── css/
│   │   ├── variables.css      # 🎨 Design system tokens
│   │   ├── utilities.css      # 🔧 Utility classes
│   │   ├── base.css          # 📄 Base styles
│   │   ├── base-navbar.css   # 🧭 Navigation styles
│   │   ├── base-sidebar.css  # 📱 Sidebar styles
│   │   ├── skeleton.css      # ⏳ Loading states
│   │   ├── auth-form.css     # 🔐 Authentication forms
│   │   └── workflow-content.css # 🔄 Workflow-specific styles
│   ├── js/
│   │   ├── core/
│   │   │   ├── config.js     # ⚙️ Application configuration
│   │   │   └── utils.js      # 🛠 Utility functions
│   │   ├── events.js         # 🎯 Global event management
│   │   ├── theme.js          # 🌓 Theme management
│   │   ├── sidebar.js        # 📱 Sidebar functionality
│   │   └── workflow-events.js # 🔄 Workflow interactions
│   └── img/
│       └── favicon.svg       # 🖼️ Application icon
└── templates/
    ├── shared/
    │   └── layout.html       # 🏗️ Base template
    └── fragments/
        ├── navbar.html       # 🧭 Navigation component
        ├── sidebar.html      # 📱 Sidebar component
        └── footer.html       # 🦶 Footer component
```

## 🎨 **Design System**

### **CSS Variables (variables.css)**

The design system is built on CSS custom properties organized into logical groups:

```css
/* Color System */
--color-primary: rgba(79, 70, 229, 1);
--color-success: rgba(34, 197, 94, 1);
--color-error: rgba(239, 68, 68, 1);

/* Spacing System (8px base) */
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */

/* Typography Scale */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
```

**How to modify colors:**
1. Update values in `variables.css`
2. Changes apply globally across the application
3. Dark theme overrides are in the same file

### **Utility Classes (utilities.css)**

Utility-first classes for rapid development:

```html
<!-- Spacing -->
<div class="p-4 m-2 gap-3">

<!-- Layout -->
<div class="flex items-center justify-between">

<!-- Typography -->
<h1 class="text-2xl font-semibold text-primary">

<!-- Colors -->
<div class="bg-primary text-white border border-accent">
```

**Adding new utilities:**
1. Follow the naming convention: `property-value`
2. Use design system variables
3. Group related utilities together
4. Add responsive variants when needed

## 🔧 **JavaScript Architecture**

### **Configuration System (config.js)**

Centralized application configuration:

```javascript
import { Config, getConfig, setConfig } from './core/config.js';

// Get configuration value
const themeKey = getConfig('ui.theme.storageKey', 'theme');

// Set configuration value
setConfig('ui.animation.duration.fast', 100);

// Environment-specific settings
if (isProduction()) {
    setConfig('performance.logToConsole', false);
}
```

**Adding new configuration:**
1. Add to the appropriate section in `Config` object
2. Use dot notation for nested properties
3. Provide sensible defaults
4. Document the purpose and usage

### **Utility Functions (utils.js)**

Reusable utility functions organized by category:

```javascript
import { DOM, Str, Storage, Validate } from './core/utils.js';

// DOM manipulation
const element = DOM.$('.my-selector');
DOM.on(element, 'click', handler);

// String utilities
const slug = Str.kebabCase('My Title'); // 'my-title'

// Storage utilities
Storage.set('userPrefs', { theme: 'dark' });
const prefs = Storage.get('userPrefs', {});

// Validation
if (Validate.email(userInput)) {
    // Valid email
}
```

**Adding new utilities:**
1. Choose the appropriate category (DOM, Str, etc.)
2. Follow the existing naming conventions
3. Include JSDoc comments
4. Add error handling where appropriate
5. Write reusable, pure functions when possible

### **Event Management**

Enhanced event system with proper cleanup:

```javascript
// Class-based components
class MyComponent {
    constructor(element) {
        this.element = element;
        this.cleanup = [];
        this.init();
    }

    init() {
        // Add event with automatic cleanup
        const cleanup = DOM.on(this.element, 'click', this.handleClick.bind(this));
        this.cleanup.push(cleanup);
    }

    destroy() {
        // Clean up all event listeners
        this.cleanup.forEach(fn => fn());
        this.cleanup = [];
    }
}
```

## 🎯 **Component Development**

### **Adding New Components**

1. **CSS Component:**
```css
/* In appropriate CSS file */
.my-component {
    /* Use design system variables */
    padding: var(--space-4);
    background-color: var(--bg-primary);
    border-radius: var(--radius-lg);

    /* Component-specific styles */
    &__header {
        font-weight: var(--font-weight-semibold);
    }

    &__content {
        margin-top: var(--space-3);
    }

    /* States */
    &.is-loading {
        opacity: 0.6;
        pointer-events: none;
    }

    /* Responsive */
    @media (max-width: 768px) {
        padding: var(--space-2);
    }
}
```

2. **JavaScript Component:**
```javascript
// In appropriate JS file
class MyComponent {
    constructor(element, options = {}) {
        this.element = element;
        this.options = { ...this.defaults, ...options };
        this.state = {};
        this.cleanup = [];

        this.init();
    }

    get defaults() {
        return {
            autoClose: true,
            duration: getConfig('ui.animation.duration.normal', 250)
        };
    }

    init() {
        this.bindEvents();
        this.setState({ initialized: true });
    }

    bindEvents() {
        const cleanup = DOM.on(this.element, 'click', this.handleClick.bind(this));
        this.cleanup.push(cleanup);
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    render() {
        // Update DOM based on state
    }

    destroy() {
        this.cleanup.forEach(fn => fn());
        this.element.remove();
    }
}

// Export for use in other files
export default MyComponent;
```

3. **HTML Template:**
```html
<!-- Use semantic HTML -->
<div class="my-component" role="region" aria-labelledby="component-title">
    <h3 id="component-title" class="my-component__header">
        Component Title
    </h3>
    <div class="my-component__content">
        <!-- Content here -->
    </div>
</div>
```

### **Accessibility Guidelines**

Always ensure components are accessible:

1. **Semantic HTML:** Use appropriate HTML elements
2. **ARIA Labels:** Add `aria-label`, `aria-describedby`, `role` attributes
3. **Keyboard Navigation:** Support Tab, Enter, Escape, Arrow keys
4. **Focus Management:** Proper focus indicators and management
5. **Screen Readers:** Test with screen reader software

```html
<!-- Good accessibility example -->
<button class="dropdown-trigger"
        aria-label="User menu"
        aria-expanded="false"
        aria-haspopup="true">
    <img src="/static/img/profile.svg" alt="User profile">
    <i class="bx bx-chevron-down" aria-hidden="true"></i>
</button>

<div class="dropdown-menu"
     role="menu"
     aria-hidden="true">
    <div class="dropdown-item" role="menuitem" tabindex="0">
        Profile
    </div>
</div>
```

## 🧪 **Testing & Debugging**

### **Browser Testing**

Test in multiple browsers and devices:

1. **Desktop:** Chrome, Firefox, Safari, Edge
2. **Mobile:** iOS Safari, Chrome Mobile, Samsung Internet
3. **Accessibility:** Screen readers (NVDA, JAWS, VoiceOver)

### **Performance Testing**

1. **Lighthouse:** Use Chrome DevTools Lighthouse
2. **Core Web Vitals:** Monitor LCP, FID, CLS metrics
3. **Network:** Test on slow connections (3G simulation)

### **Debugging Tools**

**Console Debugging:**
```javascript
// Use the debug configuration
if (isDebug()) {
    console.log('Component initialized:', this);
}

// Performance monitoring
if (getConfig('performance.enabled')) {
    performance.mark('component-start');
    // ... component code ...
    performance.mark('component-end');
    performance.measure('component-init', 'component-start', 'component-end');
}
```

**CSS Debugging:**
```css
/* Debug mode styles */
[data-debug="true"] * {
    outline: 1px solid red !important;
}

/* Performance debugging */
[data-debug="animations"] * {
    animation-duration: 5s !important;
    transition-duration: 5s !important;
}
```

## 🔄 **Common Maintenance Tasks**

### **Updating Colors**

1. Modify values in `variables.css`
2. Update both light and dark theme variants
3. Test contrast ratios for accessibility
4. Verify changes across all components

### **Adding New Breakpoints**

1. Add breakpoint to `variables.css`:
```css
:root {
    --breakpoint-xs: 480px;
    --breakpoint-sm: 640px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 1024px;
    --breakpoint-xl: 1280px;
}
```

2. Add responsive utilities in `utilities.css`:
```css
@media (min-width: 480px) {
    .xs\:block { display: block; }
    .xs\:hidden { display: none; }
}
```

### **Performance Optimization**

1. **CSS Optimization:**
   - Remove unused CSS classes
   - Minimize specificity
   - Use efficient selectors
   - Leverage CSS containment

2. **JavaScript Optimization:**
   - Lazy load components
   - Debounce user inputs
   - Use event delegation
   - Clean up event listeners

3. **Asset Optimization:**
   - Compress images
   - Use modern image formats (WebP, AVIF)
   - Implement lazy loading
   - Minimize HTTP requests

### **Accessibility Audits**

Regular accessibility checks:

1. **Automated Tools:**
   - axe-core browser extension
   - Lighthouse accessibility audit
   - WAVE web accessibility evaluator

2. **Manual Testing:**
   - Keyboard navigation only
   - Screen reader testing
   - High contrast mode
   - Zoom to 200%

## 🚨 **Troubleshooting**

### **Common Issues**

**Styles not applying:**
1. Check CSS file loading order in `layout.html`
2. Verify CSS selector specificity
3. Check for typos in class names
4. Inspect element in browser DevTools

**JavaScript errors:**
1. Check browser console for errors
2. Verify module imports/exports
3. Check for undefined variables
4. Validate event listener cleanup

**Performance issues:**
1. Check for memory leaks (event listeners)
2. Optimize expensive DOM operations
3. Use CSS transforms for animations
4. Implement virtual scrolling for large lists

### **Browser Compatibility**

**CSS Features:**
- Use autoprefixer for vendor prefixes
- Provide fallbacks for modern CSS features
- Test in IE11 if required

**JavaScript Features:**
- Use Babel for transpilation if needed
- Provide polyfills for missing features
- Use feature detection instead of browser detection

## 📋 **Maintenance Checklist**

### **Monthly Tasks**

- [ ] Update dependencies
- [ ] Run accessibility audit
- [ ] Check performance metrics
- [ ] Review browser compatibility
- [ ] Clean up unused code
- [ ] Update documentation

### **Quarterly Tasks**

- [ ] Major dependency updates
- [ ] Security vulnerability scan
- [ ] Performance benchmark comparison
- [ ] User feedback review
- [ ] Refactoring opportunities assessment

### **Annual Tasks**

- [ ] Major framework updates
- [ ] Design system review
- [ ] Architecture review
- [ ] Legacy code removal
- [ ] Performance budget review

## 🎓 **Learning Resources**

### **CSS & Design Systems**

- [CSS Custom Properties Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Design Systems Guide](https://www.designsystems.com/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### **JavaScript Architecture**

- [JavaScript Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Event Handling Best Practices](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events)
- [Performance Best Practices](https://web.dev/performance/)

### **Tools & Testing**

- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [axe-core](https://github.com/dequelabs/axe-core)
- [Can I Use](https://caniuse.com/)

---

## 📞 **Support**

For questions or issues:

1. Check this maintenance guide
2. Review the code comments and documentation
3. Search for similar issues in the project history
4. Create a detailed issue report with:
   - Browser/OS information
   - Steps to reproduce
   - Expected vs actual behavior
   - Console errors (if any)

---

**Last Updated:** $(date +%Y-%m-%d)
**Version:** 1.0.0
