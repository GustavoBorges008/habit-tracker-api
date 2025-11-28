/**
 * UI Components
 * Reusable UI components and utilities
 */

const UI = {
    /**
     * Toast notifications
     */
    toast: {
        show(message, type = 'success') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            
            const icon = {
                success: 'fa-check-circle',
                error: 'fa-exclamation-circle',
                warning: 'fa-exclamation-triangle',
                info: 'fa-info-circle'
            }[type] || 'fa-info-circle';
            
            toast.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${message}</span>
            `;
            
            container.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'toastSlide 0.3s reverse';
                setTimeout(() => toast.remove(), 300);
            }, CONFIG.TOAST_DURATION);
        },
        
        success(message) {
            this.show(message, 'success');
        },
        
        error(message) {
            this.show(message, 'error');
        },
        
        warning(message) {
            this.show(message, 'warning');
        },
        
        info(message) {
            this.show(message, 'info');
        }
    },

    /**
     * Loading states
     */
    loading: {
        show(elementId = 'loadingState') {
            const element = document.getElementById(elementId);
            if (element) element.style.display = 'block';
        },
        
        hide(elementId = 'loadingState') {
            const element = document.getElementById(elementId);
            if (element) element.style.display = 'none';
        }
    },

    /**
     * Create habit card
     */
    createHabitCard(habit) {
        const card = document.createElement('div');
        card.className = `habit-card ${habit.completed_today ? 'completed' : ''}`;
        card.dataset.habitId = habit.id;
        card.dataset.filter = habit.completed_today ? 'completed' : 'pending';
        
        const streakIcon = habit.streak.current > 0 ? '🔥' : '';
        const categoryDisplay = habit.category_name ? 
            `<span class="habit-category">${habit.category_name}</span>` : '';
        
        card.innerHTML = `
            <div class="habit-header">
                <div class="habit-title-group">
                    <span class="habit-icon">${habit.icon || '✓'}</span>
                    <div>
                        <h3 class="habit-title">${habit.name}</h3>
                        ${categoryDisplay}
                    </div>
                </div>
                <div class="habit-check ${habit.completed_today ? 'checked' : ''}" 
                     onclick="app.toggleHabit(${habit.id}, ${!habit.completed_today})">
                    ${habit.completed_today ? '<i class="fas fa-check"></i>' : ''}
                </div>
            </div>
            ${habit.description ? `<p class="habit-description">${habit.description}</p>` : ''}
            <div class="habit-stats">
                <div class="habit-stat">
                    <span class="habit-stat-label">Streak</span>
                    <span class="habit-stat-value streak-fire">${streakIcon} ${habit.streak.current}</span>
                </div>
                <div class="habit-stat">
                    <span class="habit-stat-label">Melhor</span>
                    <span class="habit-stat-value">${habit.streak.best}</span>
                </div>
                <div class="habit-stat">
                    <span class="habit-stat-label">Taxa</span>
                    <span class="habit-stat-value">${habit.completion_rate}%</span>
                </div>
            </div>
        `;
        
        return card;
    },

    /**
     * Update stats display
     */
    updateStats(stats) {
        document.getElementById('totalHabits').textContent = stats.total_habits;
        document.getElementById('completedToday').textContent = stats.completed_today;
        document.getElementById('avgStreak').textContent = stats.average_streak.toFixed(1);
        document.getElementById('totalCompletions').textContent = stats.total_completions;
        
        const completionRate = stats.completion_rate_today;
        const trendEl = document.getElementById('completionTrend');
        trendEl.textContent = `${completionRate.toFixed(0)}% concluído`;
        trendEl.className = completionRate >= 50 ? 'stat-trend positive' : 'stat-trend';
    },

    /**
     * Update API status indicator
     */
    updateAPIStatus(isOnline) {
        const statusEl = document.getElementById('apiStatus');
        const statusText = statusEl.querySelector('.status-text');
        
        if (isOnline) {
            statusEl.className = 'api-status online';
            statusText.textContent = 'API Online';
        } else {
            statusEl.className = 'api-status offline';
            statusText.textContent = 'API Offline';
        }
    },

    /**
     * Show/hide empty state
     */
    toggleEmptyState(show) {
        const emptyState = document.getElementById('emptyState');
        const habitsGrid = document.getElementById('habitsGrid');
        
        if (show) {
            emptyState.style.display = 'block';
            habitsGrid.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            habitsGrid.style.display = 'grid';
        }
    }
};

/**
 * Modal Component
 */
const habitModal = {
    element: null,
    
    init() {
        this.element = document.getElementById('habitModal');
        
        // Setup form submission
        const form = document.getElementById('habitForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    },
    
    open() {
        if (this.element) {
            this.element.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    },
    
    close() {
        if (this.element) {
            this.element.classList.remove('active');
            document.body.style.overflow = '';
            this.reset();
        }
    },
    
    reset() {
        document.getElementById('habitForm').reset();
    },
    
    async handleSubmit() {
        const formData = {
            name: document.getElementById('habitName').value,
            description: document.getElementById('habitDescription').value || null,
            category_id: document.getElementById('habitCategory').value || null,
            difficulty: document.getElementById('habitDifficulty').value,
            goal_frequency: parseInt(document.getElementById('habitGoal').value),
            icon: document.getElementById('habitIcon').value || '✓'
        };
        
        try {
            await API.habits.create(formData);
            UI.toast.success('Hábito criado com sucesso! 🎉');
            this.close();
            await app.loadHabits();
        } catch (error) {
            UI.toast.error('Erro ao criar hábito');
            console.error('Error creating habit:', error);
        }
    }
};

/**
 * Filters Component
 */
const filters = {
    current: CONFIG.FILTERS.ALL,
    
    init() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });
    },
    
    setFilter(filter) {
        this.current = filter;
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        
        // Filter habit cards
        const cards = document.querySelectorAll('.habit-card');
        cards.forEach(card => {
            if (filter === CONFIG.FILTERS.ALL) {
                card.style.display = 'block';
            } else {
                card.style.display = card.dataset.filter === filter ? 'block' : 'none';
            }
        });
    }
};
