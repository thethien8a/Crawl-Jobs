/**
 * CrawlJob Frontend - API Communication Module
 * Handles all API requests and responses
 */

// API Configuration
const API_CONFIG = {
    baseUrl: 'http://127.0.0.1:8000',
    timeout: 10000, // 10 seconds
    retries: 3,
    retryDelay: 1000 // 1 second
};

/**
 * Generic API request wrapper with error handling and retries
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {Object} options - Fetch options
 * @param {number} retryCount - Current retry attempt
 * @returns {Promise<Object>} Response data
 */
async function apiRequest(endpoint, options = {}, retryCount = 0) {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error(`API Request failed: ${error.message}`);

        // Retry logic for network errors
        if (retryCount < API_CONFIG.retries &&
            (error.name === 'TypeError' || error.name === 'AbortError')) {

            console.log(`Retrying request (${retryCount + 1}/${API_CONFIG.retries})...`);

            await new Promise(resolve => setTimeout(resolve, API_CONFIG.retryDelay));
            return apiRequest(endpoint, options, retryCount + 1);
        }

        throw error;
    }
}

/**
 * Health check API
 * @returns {Promise<Object>} Health status
 */
async function checkHealth() {
    return await apiRequest('/health');
}

/**
 * Search jobs API
 * @param {Object} params - Search parameters
 * @param {string} params.keyword - Search keyword
 * @param {number} params.page - Page number
 * @param {number} params.page_size - Items per page
 * @param {Object} params.filters - Additional filters (future use)
 * @returns {Promise<Object>} Search results
 */
async function searchJobsAPI(params = {}) {
    const queryParams = new URLSearchParams();

    // Add basic parameters
    if (params.keyword) queryParams.append('keyword', params.keyword);
    if (params.page) queryParams.append('page', params.page);
    if (params.page_size) queryParams.append('page_size', params.page_size);

    // Add filter parameters (for future enhancement)
    if (params.filters) {
        Object.entries(params.filters).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach(v => queryParams.append(key, v));
            } else if (value !== null && value !== undefined && value !== '') {
                queryParams.append(key, value);
            }
        });
    }

    const queryString = queryParams.toString();
    const endpoint = `/jobs${queryString ? '?' + queryString : ''}`;

    return await apiRequest(endpoint);
}

/**
 * Get filter options (for future enhancement)
 * @returns {Promise<Object>} Available filter options
 */
async function getFilterOptions() {
    return await apiRequest('/filter-options');
}

/**
 * Get job statistics (for future enhancement)
 * @param {Object} params - Filter parameters
 * @returns {Promise<Object>} Statistics data
 */
async function getJobStatistics(params = {}) {
    const queryParams = new URLSearchParams(params);
    const endpoint = `/stats?${queryParams.toString()}`;

    return await apiRequest(endpoint);
}

/**
 * Validate API configuration
 * @returns {boolean} True if API is accessible
 */
async function validateAPIConfig() {
    try {
        await checkHealth();
        console.log('✅ API configuration valid');
        return true;
    } catch (error) {
        console.error('❌ API configuration invalid:', error.message);
        return false;
    }
}

/**
 * API Error class for custom error handling
 */
class APIError extends Error {
    constructor(message, status, endpoint) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.endpoint = endpoint;
    }
}

/**
 * Handle API errors with user-friendly messages
 * @param {Error} error - The error object
 * @returns {string} User-friendly error message
 */
function handleAPIError(error) {
    if (error instanceof APIError) {
        switch (error.status) {
            case 400:
                return 'Dữ liệu tìm kiếm không hợp lệ. Vui lòng thử lại.';
            case 404:
                return 'Không tìm thấy dịch vụ API. Vui lòng kiểm tra kết nối.';
            case 429:
                return 'Quá nhiều yêu cầu. Vui lòng thử lại sau.';
            case 500:
                return 'Lỗi máy chủ. Vui lòng thử lại sau.';
            default:
                return `Lỗi API: ${error.message}`;
        }
    }

    if (error.name === 'TypeError') {
        return 'Không thể kết nối tới máy chủ. Vui lòng kiểm tra mạng.';
    }

    if (error.name === 'AbortError') {
        return 'Yêu cầu bị timeout. Vui lòng thử lại.';
    }

    return `Lỗi không xác định: ${error.message}`;
}

/**
 * Cache management for API responses
 */
class APICache {
    constructor(maxSize = 50) {
        this.cache = new Map();
        this.maxSize = maxSize;
    }

    set(key, data, ttl = 300000) { // 5 minutes default TTL
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });
    }

    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() - item.timestamp > item.ttl) {
            this.cache.delete(key);
            return null;
        }

        return item.data;
    }

    clear() {
        this.cache.clear();
    }

    size() {
        return this.cache.size;
    }
}

// Global cache instance
const apiCache = new APICache();

/**
 * Cached API request wrapper
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @param {boolean} useCache - Whether to use cache
 * @returns {Promise<Object>} Response data
 */
async function cachedAPIRequest(endpoint, options = {}, useCache = true) {
    if (!useCache) {
        return await apiRequest(endpoint, options);
    }

    const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
    let data = apiCache.get(cacheKey);

    if (data) {
        console.log('📋 Using cached data for:', endpoint);
        return data;
    }

    data = await apiRequest(endpoint, options);
    apiCache.set(cacheKey, data);

    return data;
}

/**
 * Batch API requests for performance
 * @param {Array} requests - Array of request objects
 * @returns {Promise<Array>} Array of responses
 */
async function batchAPIRequests(requests) {
    const promises = requests.map(async (request) => {
        try {
            return await apiRequest(request.endpoint, request.options);
        } catch (error) {
            return { error: error.message, endpoint: request.endpoint };
        }
    });

    return await Promise.allSettled(promises);
}

// Export functions for use in other modules
window.CrawlJobAPI = {
    // Core functions
    checkHealth,
    searchJobsAPI,
    getFilterOptions,
    getJobStatistics,
    validateAPIConfig,

    // Utility functions
    apiRequest,
    cachedAPIRequest,
    batchAPIRequests,
    handleAPIError,

    // Classes
    APIError,
    APICache,

    // Configuration
    CONFIG: API_CONFIG
};
