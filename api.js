/**
 * API Service
 * Handles all API calls to the backend
 */

const API = {
    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
            
            const response = await fetch(url, {
                ...mergedOptions,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    /**
     * Check API health
     */
    async checkHealth() {
        try {
            const response = await fetch(CONFIG.API_BASE);
            return response.ok;
        } catch (error) {
            return false;
        }
    },

    /**
     * Categories API
     */
    categories: {
        async getAll() {
            return await API.request('/categories');
        },
        
        async create(data) {
            return await API.request('/categories', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
    },

    /**
     * Habits API
     */
    habits: {
        async getAll() {
            return await API.request('/habits');
        },
        
        async getById(id) {
            return await API.request(`/habits/${id}`);
        },
        
        async create(data) {
            return await API.request('/habits', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async update(id, data) {
            return await API.request(`/habits/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        async delete(id) {
            return await API.request(`/habits/${id}`, {
                method: 'DELETE'
            });
        }
    },

    /**
     * Records API
     */
    records: {
        async create(data) {
            return await API.request('/records', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async getByHabit(habitId, days = 30) {
            return await API.request(`/records/${habitId}?days=${days}`);
        },
        
        async getHeatmap(habitId) {
            return await API.request(`/records/heatmap/${habitId}`);
        }
    },

    /**
     * Stats API
     */
    stats: {
        async getOverview() {
            return await API.request('/stats/overview');
        },
        
        async getComparison() {
            return await API.request('/stats/comparison');
        }
    }
};
