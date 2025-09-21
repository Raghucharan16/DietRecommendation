// Modern JavaScript for Diet Recommendation App
class DietRecommendationApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkUserStatus();
        this.updateNavigation();
        this.initializeEventListeners();
        this.addPageTransitions();
    }

    checkUserStatus() {
        // Check if user is logged in by looking for user_id cookie
        const cookies = document.cookie.split(';');
        const userIdCookie = cookies.find(cookie => cookie.trim().startsWith('user_id='));
        
        if (userIdCookie) {
            this.currentUser = userIdCookie.split('=')[1];
        }
    }

    updateNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const isLoggedIn = this.currentUser !== null;
        
        navItems.forEach(item => {
            const link = item.querySelector('a');
            if (!link) return;
            
            const href = link.getAttribute('href');
            
            // Hide register and login for logged-in users
            if (isLoggedIn && (href === '/register' || href === '/login')) {
                item.classList.add('hidden');
            }
            // Hide profile and recommendations for non-logged-in users
            else if (!isLoggedIn && (href === '/profile' || href === '/recommendations')) {
                item.classList.add('hidden');
            }
            // Show logout only for logged-in users
            else if (href === '/logout' && !isLoggedIn) {
                item.classList.add('hidden');
            }
            else {
                item.classList.remove('hidden');
            }
        });

        // Add welcome message for logged-in users
        if (isLoggedIn && !document.querySelector('.welcome-message')) {
            this.addWelcomeMessage();
        }
    }

    addWelcomeMessage() {
        const container = document.querySelector('.container');
        if (container && !container.querySelector('.welcome-message')) {
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'welcome-message fade-in';
            welcomeDiv.innerHTML = `
                <h3>Welcome to Your Health Dashboard!</h3>
                <p>Get personalized diet and exercise recommendations based on your profile.</p>
            `;
            container.insertBefore(welcomeDiv, container.firstChild);
        }
    }

    initializeEventListeners() {
        // Form validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Add loading states to buttons
        const buttons = document.querySelectorAll('button[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('click', this.handleButtonClick.bind(this));
        });

        // Handle logout
        const logoutLinks = document.querySelectorAll('a[href="/logout"]');
        logoutLinks.forEach(link => {
            link.addEventListener('click', this.handleLogout.bind(this));
        });

        // Handle navigation active states
        this.setActiveNavigation();
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Basic form validation
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        // Email validation
        const emailField = form.querySelector('input[type="email"]');
        if (emailField && emailField.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.value)) {
                this.showFieldError(emailField, 'Please enter a valid email address');
                isValid = false;
            }
        }

        // Password validation for registration
        if (form.querySelector('input[name="password"]') && form.querySelector('input[name="confirm_password"]')) {
            const password = form.querySelector('input[name="password"]').value;
            const confirmPassword = form.querySelector('input[name="confirm_password"]').value;
            
            if (password !== confirmPassword) {
                this.showFieldError(form.querySelector('input[name="confirm_password"]'), 'Passwords do not match');
                isValid = false;
            }
        }

        if (!isValid) {
            event.preventDefault();
            return false;
        }

        // Show loading state
        if (submitButton) {
            this.setButtonLoading(submitButton);
        }
    }

    handleButtonClick(event) {
        const button = event.target;
        if (button.type === 'submit') {
            // Loading state is handled in form submit
            return;
        }
        this.setButtonLoading(button);
    }

    handleLogout(event) {
        event.preventDefault();
        const confirmed = confirm('Are you sure you want to logout?');
        if (confirmed) {
            // Clear user status
            this.currentUser = null;
            // Navigate to logout
            window.location.href = '/logout';
        }
    }

    setButtonLoading(button) {
        const originalText = button.textContent;
        button.textContent = 'Loading...';
        button.disabled = true;
        
        // Reset after 10 seconds max (fallback)
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 10000);
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.color = 'var(--error-color)';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.textContent = message;
        
        field.style.borderColor = 'var(--error-color)';
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.style.borderColor = '';
    }

    setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-links a');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    addPageTransitions() {
        // Add fade-in animation to main content
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.classList.add('fade-in');
        }
    }

    // Utility method to show notifications
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        switch(type) {
            case 'success':
                notification.style.backgroundColor = 'var(--success-color)';
                break;
            case 'error':
                notification.style.backgroundColor = 'var(--error-color)';
                break;
            case 'warning':
                notification.style.backgroundColor = 'var(--warning-color)';
                break;
            default:
                notification.style.backgroundColor = 'var(--primary-color)';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // Method to format recommendation content
    formatRecommendations() {
        const recommendations = document.querySelectorAll('.recommendation-content');
        recommendations.forEach(rec => {
            // Add icons to section headers
            const headers = rec.querySelectorAll('h2, h3');
            headers.forEach(header => {
                if (header.textContent.toLowerCase().includes('breakfast')) {
                    header.innerHTML = '🥐 ' + header.innerHTML;
                } else if (header.textContent.toLowerCase().includes('lunch')) {
                    header.innerHTML = '🥗 ' + header.innerHTML;
                } else if (header.textContent.toLowerCase().includes('dinner')) {
                    header.innerHTML = '🍽️ ' + header.innerHTML;
                } else if (header.textContent.toLowerCase().includes('snack')) {
                    header.innerHTML = '🍎 ' + header.innerHTML;
                } else if (header.textContent.toLowerCase().includes('exercise')) {
                    header.innerHTML = '💪 ' + header.innerHTML;
                } else if (header.textContent.toLowerCase().includes('workout')) {
                    header.innerHTML = '🏋️ ' + header.innerHTML;
                }
            });
        });
    }
}

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new DietRecommendationApp();
    
    // Format recommendations if on recommendations page
    if (window.location.pathname === '/recommendations') {
        setTimeout(() => {
            app.formatRecommendations();
        }, 500);
    }
    
    // Show success message if redirected after registration/login
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    if (message) {
        app.showNotification(decodeURIComponent(message), 'success');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

// Export for potential use in other scripts
window.DietRecommendationApp = DietRecommendationApp;