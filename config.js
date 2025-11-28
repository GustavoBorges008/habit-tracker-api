/**
 * Configuration file
 * Centralized configuration for the Habit Tracker app
 */

const CONFIG = {
    // API Configuration
    API_URL: 'http://127.0.0.1:5000/api',
    API_BASE: 'http://127.0.0.1:5000',
    
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
