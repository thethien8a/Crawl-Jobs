/**
 * CrawlJob Frontend - Main JavaScript
 * Handles core application logic, search functionality, and page management
 */

// Global variables
const API_BASE = 'http://127.0.0.1:8000';
let currentPage = 1;
let currentKeyword = '';
let currentPageSize = 20;

/**
 * Main application initialization
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 Initializing CrawlJob Frontend');

    // Set up event listeners
    setupEventListeners();

    // Check API health
    checkAPIHealth();

    // Initialize UI components
    initializeUI();

    console.log('✅ CrawlJob Frontend initialized successfully');
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Search button
    const searchBtn = document.querySelector('button[onclick*="searchJobs"]');
    if (searchBtn) {
        searchBtn.addEventListener('click', () => searchJobs(1));
    }

    // Enter key on search input
    const keywordInput = document.getElementById('keyword');
    if (keywordInput) {
        keywordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchJobs(1);
            }
        });
    }

    // Page size change
    const pageSizeSelect = document.getElementById('pageSize');
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', function() {
            const newPageSize = parseInt(this.value);
            if (newPageSize !== currentPageSize) {
                currentPageSize = newPageSize;
                console.log(`📏 Page size changed to ${currentPageSize}`);
                // Reset to page 1 when page size changes
                if (currentKeyword.trim()) {
                    searchJobs(1);
                }
            }
        });
    }
}

/**
 * Check API health on startup
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            console.log('✅ API connection successful');
            showNotification('API connection successful', 'success');
        } else {
            console.warn('⚠️ API health check failed');
            showNotification('API connection failed', 'warning');
        }
    } catch (error) {
        console.error('❌ API not available:', error);
        showNotification('API not available. Please start the backend server.', 'error');
    }
}

/**
 * Search jobs with given parameters
 * @param {number} page - Page number to search
 */
async function searchJobs(page = 1) {
    const keyword = document.getElementById('keyword').value.trim();
    const pageSize = parseInt(document.getElementById('pageSize').value);

    // Update current state
    currentPage = page;
    currentKeyword = keyword;
    currentPageSize = pageSize;

    // Show loading state
    showLoading(true);
    hideResults();

    try {
        // Use API module for search
        const params = {
            keyword: keyword || undefined,
            page: page,
            page_size: pageSize
        };

        const data = await window.CrawlJobAPI.searchJobsAPI(params);

        // Display results
        displayResults(data);
        updateStats(data);
        updatePagination(data);

        // Log successful search
        console.log(`🔍 Found ${data.items?.length || 0} jobs for "${keyword}"`);

    } catch (error) {
        console.error('❌ Search error:', error);
        const errorMessage = window.CrawlJobAPI.handleAPIError(error);
        showError(`Lỗi tìm kiếm: ${errorMessage}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Display search results
 * @param {Object} data - API response data
 */
function displayResults(data) {
    const resultsDiv = document.getElementById('results');

    if (!data.items || data.items.length === 0) {
        resultsDiv.innerHTML = window.CrawlJobUI.createEmptyState(
            'Không tìm thấy việc làm phù hợp',
            'fa-inbox'
        );
        return;
    }

    const jobsHTML = data.items.map(job => window.CrawlJobUI.createJobCardHTML(job)).join('');
    resultsDiv.innerHTML = jobsHTML;

    // Add event listeners for job cards
    addJobCardEventListeners();

    console.log(`📊 Displayed ${data.items.length} job results`);
}

/**
 * Update statistics display
 * @param {Object} data - API response data
 */
function updateStats(data) {
    const statsDiv = document.getElementById('stats');

    if (!data.items || data.items.length === 0) {
        statsDiv.style.display = 'none';
        return;
    }

    const totalJobs = data.items.length;
    const sources = [...new Set(data.items.map(job => job.source_site))];
    const companies = [...new Set(data.items.map(job => job.company_name))].filter(c => c);

    statsDiv.innerHTML = window.CrawlJobUI.createStatsHTML(totalJobs, sources.length, companies.length);
    statsDiv.style.display = 'flex';

    console.log(`📈 Updated stats: ${totalJobs} jobs, ${sources.length} sources, ${companies.length} companies`);
}

/**
 * Update pagination display
 * @param {Object} data - API response data
 */
function updatePagination(data) {
    const paginationDiv = document.getElementById('pagination');

    // Hide pagination if no data
    if (!data.items || data.items.length === 0) {
        paginationDiv.style.display = 'none';
        return;
    }

    // Show pagination if:
    // 1. We have a full page of results (may have more pages)
    // 2. We're on page > 1 (can go back)
    const hasFullPage = data.items.length >= currentPageSize;
    const hasPreviousPage = currentPage > 1;

    if (!hasFullPage && !hasPreviousPage) {
        paginationDiv.style.display = 'none';
        return;
    }

    const paginationHTML = window.CrawlJobUI.createPaginationHTML(currentPage, data.items.length);
    const paginationList = paginationDiv.querySelector('ul');
    if (paginationList) {
        paginationList.innerHTML = paginationHTML;
        paginationDiv.style.display = 'block';
    }

    console.log(`📄 Updated pagination: Page ${currentPage}, Items: ${data.items.length}, Full page: ${hasFullPage}, Has previous: ${hasPreviousPage}`);
    console.log(`📄 Pagination HTML:`, paginationHTML);
}

/**
 * Show/hide loading state
 * @param {boolean} show - Whether to show loading
 */
function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
}

/**
 * Hide results and pagination
 */
function hideResults() {
    const resultsDiv = document.getElementById('results');
    const paginationDiv = document.getElementById('pagination');
    const statsDiv = document.getElementById('stats');

    if (resultsDiv) resultsDiv.innerHTML = '';
    if (paginationDiv) paginationDiv.style.display = 'none';
    if (statsDiv) statsDiv.style.display = 'none';
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, warning, error)
 */
function showNotification(message, type = 'info') {
    // Simple console notification for now
    const prefix = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    };

    console.log(`${prefix[type] || prefix.info} ${message}`);
}

/**
 * Initialize UI components
 */
function initializeUI() {
    // Set default values
    const keywordInput = document.getElementById('keyword');
    if (keywordInput && !keywordInput.value) {
        keywordInput.value = 'python';
    }

    console.log('🎨 UI components initialized');
}

/**
 * Add event listeners to job cards after they're rendered
 */
function addJobCardEventListeners() {
    // Add toggle description functionality
    document.querySelectorAll('.expand-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            toggleDescription(this);
        });
    });

    // Add smooth animations
    document.querySelectorAll('.job-card').forEach(card => {
        card.classList.add('fade-in');
    });
}

/**
 * Toggle job description expansion
 * @param {HTMLElement} button - The toggle button
 */
function toggleDescription(button) {
    const descDiv = button.previousElementSibling;
    const isExpanded = descDiv.classList.contains('expanded');

    if (isExpanded) {
        descDiv.classList.remove('expanded');
        button.innerHTML = '<i class="fas fa-chevron-down me-1"></i>Xem thêm';
    } else {
        descDiv.classList.add('expanded');
        button.innerHTML = '<i class="fas fa-chevron-up me-1"></i>Thu gọn';
    }
}

/**
 * Export functions for use in other modules
 */
window.CrawlJob = {
    searchJobs,
    showLoading,
    showError,
    showNotification,
    hideResults,
    // Export getters for global variables
    getCurrentPage: () => currentPage,
    getCurrentPageSize: () => currentPageSize
};
