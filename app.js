/**
 * Main Application
 * Entry point and core application logic
 */

const app = {
    habits: [],
    categories: [],
    stats: null,

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Initializing Habit Tracker...');
        
        // Initialize components
        habitModal.init();
        filters.init();
        
        // Check API health
        const isOnline = await this.checkAPI();
        
        if (isOnline) {
            await this.loadData();
        } else {
            UI.toast.error('API offline. Por favor, inicie o servidor Flask!');
        }
        
        console.log('✅ Habit Tracker initialized');
    },

    /**
     * Check API status
     */
    async checkAPI() {
        try {
            const isOnline = await API.checkHealth();
            UI.updateAPIStatus(isOnline);
            return isOnline;
        } catch (error) {
            UI.updateAPIStatus(false);
            return false;
        }
    },

    /**
     * Load all data
     */
    async loadData() {
        try {
            await Promise.all([
                this.loadCategories(),
                this.loadHabits(),
                this.loadStats()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
            UI.toast.error('Erro ao carregar dados');
        }
    },

    /**
     * Load categories
     */
    async loadCategories() {
        try {
            this.categories = await API.categories.getAll();
            this.populateCategorySelect();
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    },

    /**
     * Populate category select
     */
    populateCategorySelect() {
        const select = document.getElementById('habitCategory');
        select.innerHTML = '<option value="">Selecione...</option>';
        
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = `${category.icon} ${category.name}`;
            select.appendChild(option);
        });
    },

    /**
     * Load habits
     */
    async loadHabits() {
        UI.loading.show();
        
        try {
            this.habits = await API.habits.getAll();
            this.renderHabits();
        } catch (error) {
            console.error('Error loading habits:', error);
            UI.toast.error('Erro ao carregar hábitos');
        } finally {
            UI.loading.hide();
        }
    },

    /**
     * Render habits to the grid
     */
    renderHabits() {
        const grid = document.getElementById('habitsGrid');
        grid.innerHTML = '';
        
        if (this.habits.length === 0) {
            UI.toggleEmptyState(true);
            return;
        }
        
        UI.toggleEmptyState(false);
        
        this.habits.forEach(habit => {
            const card = UI.createHabitCard(habit);
            grid.appendChild(card);
        });
        
        // Apply current filter
        filters.setFilter(filters.current);
    },

    /**
     * Load statistics
     */
    async loadStats() {
        try {
            this.stats = await API.stats.getOverview();
            UI.updateStats(this.stats);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },

    /**
     * Toggle habit completion
     */
    async toggleHabit(habitId, completed) {
        try {
            const data = {
                habit_id: habitId,
                completed: completed ? 1 : 0
            };
            
            await API.records.create(data);
            
            UI.toast.success(
                completed ? 'Hábito completado! 🎉' : 'Marcado como não completado'
            );
            
            // Reload data
            await this.loadHabits();
            await this.loadStats();
        } catch (error) {
            console.error('Error toggling habit:', error);
            UI.toast.error('Erro ao atualizar hábito');
        }
    },

    /**
     * Refresh all data
     */
    async refreshData() {
        UI.toast.info('Atualizando dados...');
        await this.loadData();
        UI.toast.success('Dados atualizados!');
    },

    /**
     * Show analytics view (placeholder)
     */
    showAnalytics() {
        UI.toast.info('Análise completa em desenvolvimento...');
        // TODO: Implement analytics view
    },

    /**
     * Export data (placeholder)
     */
    exportData() {
        try {
            const data = {
                habits: this.habits,
                categories: this.categories,
                stats: this.stats,
                exportDate: new Date().toISOString()
            };
            
            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `habit-tracker-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            UI.toast.success('Dados exportados com sucesso!');
        } catch (error) {
            console.error('Error exporting data:', error);
            UI.toast.error('Erro ao exportar dados');
        }
    }
};

/**
 * Auto-refresh data every 5 minutes
 */
setInterval(() => {
    app.checkAPI();
}, 300000);

/**
 * Initialize app when DOM is ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}
