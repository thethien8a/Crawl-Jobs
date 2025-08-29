/**
 * CrawlJob Frontend - UI Helper Module
 * Contains utility functions for DOM manipulation and UI interactions
 */

/**
 * Create HTML for a job card
 * @param {Object} job - Job data object
 * @returns {string} HTML string for job card
 */
function createJobCardHTML(job) {
    return `
        <div class="job-card card">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <div class="mb-2">
                            ${job.job_url ?
                                `<h5 class="card-title mb-1">
                                    <a href="${job.job_url}" target="_blank" class="text-primary fw-bold text-decoration-none job-title-link">
                                        ${job.job_title || 'Chưa có tiêu đề'}
                                        <i class="fas fa-external-link-alt ms-1 small"></i>
                                    </a>
                                </h5>` :
                                `<h5 class="card-title mb-1 text-primary fw-bold">
                                    ${job.job_title || 'Chưa có tiêu đề'}
                                </h5>`
                            }
                        </div>

                        <div class="d-flex justify-content-between align-items-center mb-2 company-row">
                            <div>
                                <i class="fas fa-building text-muted me-2"></i>
                                <strong>${job.company_name || 'Chưa có thông tin'}</strong>
                            </div>
                            <span class="badge source-badge ${getSourceBadgeClass(job.source_site)}">
                                ${formatSourceSite(job.source_site)}
                            </span>
                        </div>

                        <div class="row mb-2">
                            <div class="col-sm-6">
                                <i class="fas fa-map-marker-alt text-muted me-2"></i>
                                <span>${job.location || 'Chưa có thông tin'}</span>
                            </div>
                            <div class="col-sm-6">
                                <i class="fas fa-money-bill-wave text-muted me-2"></i>
                                <span class="salary-highlight">${job.salary || 'Thỏa thuận'}</span>
                            </div>
                        </div>

                        ${job.job_type ? `
                        <div class="mb-2">
                            <i class="fas fa-clock text-muted me-2"></i>
                            <span class="badge bg-secondary">${job.job_type}</span>
                            ${job.experience_level ? `<span class="badge bg-info ms-1">${job.experience_level}</span>` : ''}
                        </div>
                        ` : ''}
                    </div>

                    <div class="col-md-4 text-md-end">
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-calendar text-muted me-1"></i>
                                ${formatDate(job.updated_at || job.created_at)}
                            </small>
                        </div>

                        ${job.job_url ? `
                        <a href="${job.job_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-external-link-alt me-1"></i>Xem chi tiết
                        </a>
                        ` : ''}
                    </div>
                </div>

                ${job.job_description ? `
                <div class="mt-3">
                    <div class="job-description" id="desc-${job.job_url ? job.job_url.split('/').pop() : Math.random()}">
                        <strong class="text-muted">Mô tả:</strong>
                        <p class="mt-1 mb-0">${job.job_description.substring(0, 200)}${job.job_description.length > 200 ? '...' : ''}</p>
                    </div>
                    ${job.job_description.length > 200 ? `
                    <button class="expand-btn mt-1" onclick="toggleDescription(this)">
                        <i class="fas fa-chevron-down me-1"></i>Xem thêm
                    </button>
                    ` : ''}
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

/**
 * Create HTML for statistics cards
 * @param {number} totalJobs - Total number of jobs
 * @param {number} sources - Number of unique sources
 * @param {number} companies - Number of unique companies
 * @returns {string} HTML string for stats
 */
function createStatsHTML(totalJobs, sources, companies) {
    return `
        <div class="col-md-4">
            <div class="stats-card text-center">
                <h3><i class="fas fa-briefcase me-2"></i>${totalJobs}</h3>
                <p class="mb-0">Việc làm tìm thấy</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stats-card text-center">
                <h3><i class="fas fa-globe me-2"></i>${sources}</h3>
                <p class="mb-0">Nguồn dữ liệu</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stats-card text-center">
                <h3><i class="fas fa-building me-2"></i>${companies}</h3>
                <p class="mb-0">Công ty</p>
            </div>
        </div>
    `;
}

/**
 * Create HTML for pagination
 * @param {number} currentPage - Current page number
 * @param {number} totalItems - Total items in current response
 * @returns {string} HTML string for pagination
 */
function createPaginationHTML(currentPage, totalItems) {
    let paginationHTML = '';

    // Previous button
    if (currentPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="event.preventDefault(); searchJobs(${currentPage - 1}); return false;">
                    <i class="fas fa-chevron-left me-1"></i>Trước
                </a>
            </li>
        `;
    }

    // Current page
    paginationHTML += `
        <li class="page-item active">
            <span class="page-link">Trang ${currentPage}</span>
        </li>
    `;

    // Next button (show if we got full page of results)
    if (typeof window.getCurrentPageSize === 'function' && totalItems >= window.getCurrentPageSize()) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="event.preventDefault(); searchJobs(${currentPage + 1}); return false;">
                    Sau<i class="fas fa-chevron-right ms-1"></i>
                </a>
            </li>
        `;
    }

    return paginationHTML;
}

/**
 * Get CSS class for source badge
 * @param {string} source - Source site name
 * @returns {string} CSS class for badge
 */
function getSourceBadgeClass(source) {
    const classes = {
        'linkedin.com': 'bg-primary',
        'jobsgo.vn': 'bg-success',
        'joboko.com': 'bg-warning',
        '123job.vn': 'bg-info',
        'careerviet.vn': 'bg-secondary',
        'jobstreet.vn': 'bg-dark',
        'topcv.vn': 'bg-danger',
        'itviec.com': 'bg-info',
        'careerlink.vn': 'bg-success',
        'vietnamworks.com': 'bg-warning'
    };
    return classes[source] || 'bg-light text-dark';
}

/**
 * Format source site name for display
 * @param {string} source - Source site URL
 * @returns {string} Formatted site name
 */
function formatSourceSite(source) {
    const names = {
        'linkedin.com': 'LinkedIn',
        'jobsgo.vn': 'JobsGO',
        'joboko.com': 'JobOKO',
        '123job.vn': '123Job',
        'careerviet.vn': 'CareerViet',
        'jobstreet.vn': 'JobStreet',
        'topcv.vn': 'TopCV',
        'itviec.com': 'ITviec',
        'careerlink.vn': 'CareerLink',
        'vietnamworks.com': 'VietnamWorks'
    };
    return names[source] || source;
}

/**
 * Format date for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return 'Chưa có thông tin';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    } catch (error) {
        console.warn('Date formatting error:', error);
        return dateString;
    }
}

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function to limit function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Create loading spinner HTML
 * @param {string} message - Loading message
 * @returns {string} HTML string for loading spinner
 */
function createLoadingSpinner(message = 'Đang tải...') {
    return `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">${message}</p>
        </div>
    `;
}

/**
 * Create error message HTML
 * @param {string} message - Error message
 * @param {string} type - Error type (danger, warning, info)
 * @returns {string} HTML string for error message
 */
function createErrorMessage(message, type = 'danger') {
    return `
        <div class="alert alert-${type} text-center">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

/**
 * Create empty state HTML
 * @param {string} message - Empty state message
 * @param {string} icon - FontAwesome icon class
 * @returns {string} HTML string for empty state
 */
function createEmptyState(message = 'Không tìm thấy kết quả', icon = 'fa-inbox') {
    return `
        <div class="text-center text-muted py-5">
            <i class="fas ${icon} fa-3x mb-3"></i>
            <h4>${message}</h4>
        </div>
    `;
}

/**
 * Animate element with fade-in effect
 * @param {HTMLElement} element - Element to animate
 */
function fadeInElement(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';
    element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

    requestAnimationFrame(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    });
}

/**
 * Scroll element into view smoothly
 * @param {HTMLElement} element - Element to scroll to
 * @param {Object} options - Scroll options
 */
function scrollToElement(element, options = {}) {
    const defaultOptions = {
        behavior: 'smooth',
        block: 'start',
        inline: 'nearest'
    };

    element.scrollIntoView({ ...defaultOptions, ...options });
}

/**
 * Create notification toast
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast-notification alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease;
    `;

    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    toast.innerHTML = `
        <i class="fas ${iconMap[type] || iconMap.info} me-2"></i>
        ${message}
        <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
    `;

    document.body.appendChild(toast);

    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }
}

/**
 * Add CSS for toast animations
 */
function addToastStyles() {
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize toast styles on load
document.addEventListener('DOMContentLoaded', addToastStyles);

/**
 * Export functions for use in other modules
 */
window.CrawlJobUI = {
    // HTML creation functions
    createJobCardHTML,
    createStatsHTML,
    createPaginationHTML,
    createLoadingSpinner,
    createErrorMessage,
    createEmptyState,

    // Utility functions
    getSourceBadgeClass,
    formatSourceSite,
    formatDate,
    debounce,
    throttle,
    fadeInElement,
    scrollToElement,
    showToast,

    // Animation helpers
    addToastStyles
};
