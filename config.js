/**
 * Configuration file
 * Centralized configuration for the Habit Tracker app
 */

const CONFIG = {
    
    API_URL: 'https://habit-tracker-api-66ad.onrender.com/api',
    API_BASE: 'https://habit-tracker-api-66ad.onrender.com',
};
    // Request timeout in milliseconds
    REQUEST_TIMEOUT: 10000,
    
    // Toast duration in milliseconds
    TOAST_DURATION: 3000,
    
    // Animation delays
    ANIMATION_DELAY: 300,
    
    // Filters
    FILTERS: {
        ALL: 'all',
        COMPLETED: 'completed',
        PENDING: 'pending'
    },
    
    // Difficulty levels
    DIFFICULTY: {
        EASY: 'easy',
        MEDIUM: 'medium',
        HARD: 'hard'
    },
    
    // Local storage keys
    STORAGE_KEYS: {
        THEME: 'habit_tracker_theme',
        FILTER: 'habit_tracker_filter'
    }
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
