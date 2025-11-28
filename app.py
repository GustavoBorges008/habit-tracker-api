"""
HABIT TRACKER - Backend Completo
Sistema avançado de rastreamento de hábitos com Flask

Estrutura do projeto:
habit-tracker/
├── app.py (este arquivo)
├── database.db (será criado automaticamente)
└── requirements.txt

Instalar dependências:
pip install flask flask-cors python-dateutil

Executar:
python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from dateutil import parser
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'database.db'

# ==================== CONFIGURAÇÃO DO BANCO ====================

def get_db():
    """Conecta ao banco de dados"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Inicializa o banco de dados com todas as tabelas"""
    db = get_db()
    cursor = db.cursor()
    
    # Tabela de Categorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#6366f1',
            icon TEXT DEFAULT '📌',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de Hábitos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            difficulty TEXT DEFAULT 'medium',
            goal_frequency INTEGER DEFAULT 7,
            reminder_time TEXT,
            color TEXT DEFAULT '#10b981',
            icon TEXT DEFAULT '✓',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # Tabela de Registros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            completed INTEGER DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, date)
        )
    ''')
    
    # Tabela de Conquistas/Milestones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            streak_milestone INTEGER,
            unlocked_at TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    ''')
    
    # Inserir categorias padrão se não existirem
    default_categories = [
        ('Saúde', '#ef4444', '💪'),
        ('Estudo', '#3b82f6', '📚'),
        ('Trabalho', '#8b5cf6', '💼'),
        ('Bem-estar', '#10b981', '🧘'),
        ('Social', '#f59e0b', '👥'),
        ('Criatividade', '#ec4899', '🎨')
    ]
    
    for cat_name, cat_color, cat_icon in default_categories:
        cursor.execute(
            'INSERT OR IGNORE INTO categories (name, color, icon) VALUES (?, ?, ?)',
            (cat_name, cat_color, cat_icon)
        )
    
    db.commit()
    db.close()

# ==================== UTILITÁRIOS ====================

def calculate_streak(habit_id):
    """Calcula o streak atual de um hábito"""
    db = get_db()
    cursor = db.cursor()
    
    today = datetime.now().date()
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    # Buscar todos os registros ordenados por data
    cursor.execute('''
        SELECT date, completed FROM records 
        WHERE habit_id = ? AND completed = 1
        ORDER BY date DESC
    ''', (habit_id,))
    
    records = cursor.fetchall()
    db.close()
    
    if not records:
        return {'current': 0, 'best': 0}
    
    # Calcular streak atual
    for record in records:
        record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
        expected_date = today - timedelta(days=current_streak)
        
        if record_date == expected_date:
            current_streak += 1
        else:
            break
    
    # Calcular melhor streak
    prev_date = None
    for record in records:
        record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
        
        if prev_date is None or (prev_date - record_date).days == 1:
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            temp_streak = 1
        
        prev_date = record_date
    
    return {'current': current_streak, 'best': max(best_streak, current_streak)}

def get_completion_rate(habit_id, days=30):
    """Calcula a taxa de conclusão dos últimos N dias"""
    db = get_db()
    cursor = db.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).date()
    
    cursor.execute('''
        SELECT COUNT(*) as completed FROM records 
        WHERE habit_id = ? AND date >= ? AND completed = 1
    ''', (habit_id, start_date))
    
    completed = cursor.fetchone()['completed']
    db.close()
    
    return round((completed / days) * 100, 1)

def get_best_weekday(habit_id):
    """Retorna o melhor dia da semana para o hábito"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            CAST(strftime('%w', date) AS INTEGER) as weekday,
            COUNT(*) as count
        FROM records 
        WHERE habit_id = ? AND completed = 1
        GROUP BY weekday
        ORDER BY count DESC
        LIMIT 1
    ''', (habit_id,))
    
    result = cursor.fetchone()
    db.close()
    
    if result:
        weekdays = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        return weekdays[result['weekday']]
    
    return None

# ==================== ROTAS - CATEGORIAS ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Lista todas as categorias"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(categories)

@app.route('/api/categories', methods=['POST'])
def create_category():
    """Cria uma nova categoria"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO categories (name, color, icon) 
            VALUES (?, ?, ?)
        ''', (data['name'], data.get('color', '#6366f1'), data.get('icon', '📌')))
        db.commit()
        category_id = cursor.lastrowid
        db.close()
        return jsonify({'id': category_id, 'message': 'Categoria criada com sucesso'}), 201
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'error': 'Categoria já existe'}), 400

# ==================== ROTAS - HÁBITOS ====================

@app.route('/api/habits', methods=['GET'])
def get_habits():
    """Lista todos os hábitos com estatísticas"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT h.*, c.name as category_name, c.color as category_color 
        FROM habits h
        LEFT JOIN categories c ON h.category_id = c.id
        WHERE h.active = 1
        ORDER BY h.created_at DESC
    ''')
    
    habits = []
    for row in cursor.fetchall():
        habit = dict(row)
        
        # Adicionar estatísticas
        habit['streak'] = calculate_streak(habit['id'])
        habit['completion_rate'] = get_completion_rate(habit['id'])
        habit['best_weekday'] = get_best_weekday(habit['id'])
        
        # Verificar se foi completado hoje
        today = datetime.now().date().isoformat()
        cursor.execute(
            'SELECT completed FROM records WHERE habit_id = ? AND date = ?',
            (habit['id'], today)
        )
        today_record = cursor.fetchone()
        habit['completed_today'] = bool(today_record and today_record['completed'])
        
        habits.append(habit)
    
    db.close()
    return jsonify(habits)

@app.route('/api/habits/<int:habit_id>', methods=['GET'])
def get_habit(habit_id):
    """Retorna detalhes de um hábito específico"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT h.*, c.name as category_name 
        FROM habits h
        LEFT JOIN categories c ON h.category_id = c.id
        WHERE h.id = ?
    ''', (habit_id,))
    
    habit = cursor.fetchone()
    
    if not habit:
        db.close()
        return jsonify({'error': 'Hábito não encontrado'}), 404
    
    habit_dict = dict(habit)
    habit_dict['streak'] = calculate_streak(habit_id)
    habit_dict['completion_rate'] = get_completion_rate(habit_id)
    habit_dict['best_weekday'] = get_best_weekday(habit_id)
    
    db.close()
    return jsonify(habit_dict)

@app.route('/api/habits', methods=['POST'])
def create_habit():
    """Cria um novo hábito"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO habits 
        (name, description, category_id, difficulty, goal_frequency, reminder_time, color, icon) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data.get('description'),
        data.get('category_id'),
        data.get('difficulty', 'medium'),
        data.get('goal_frequency', 7),
        data.get('reminder_time'),
        data.get('color', '#10b981'),
        data.get('icon', '✓')
    ))
    
    db.commit()
    habit_id = cursor.lastrowid
    db.close()
    
    return jsonify({'id': habit_id, 'message': 'Hábito criado com sucesso'}), 201

@app.route('/api/habits/<int:habit_id>', methods=['PUT'])
def update_habit(habit_id):
    """Atualiza um hábito existente"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        UPDATE habits 
        SET name = ?, description = ?, category_id = ?, difficulty = ?, 
            goal_frequency = ?, reminder_time = ?, color = ?, icon = ?
        WHERE id = ?
    ''', (
        data['name'],
        data.get('description'),
        data.get('category_id'),
        data.get('difficulty'),
        data.get('goal_frequency'),
        data.get('reminder_time'),
        data.get('color'),
        data.get('icon'),
        habit_id
    ))
    
    db.commit()
    db.close()
    
    return jsonify({'message': 'Hábito atualizado com sucesso'})

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    """Remove um hábito (soft delete)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE habits SET active = 0 WHERE id = ?', (habit_id,))
    db.commit()
    db.close()
    
    return jsonify({'message': 'Hábito removido com sucesso'})

# ==================== ROTAS - REGISTROS ====================

@app.route('/api/records', methods=['POST'])
def create_record():
    """Registra a conclusão de um hábito"""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    date = data.get('date', datetime.now().date().isoformat())
    
    try:
        cursor.execute('''
            INSERT INTO records (habit_id, date, completed, notes) 
            VALUES (?, ?, ?, ?)
        ''', (data['habit_id'], date, data.get('completed', 1), data.get('notes')))
        
        db.commit()
        record_id = cursor.lastrowid
        db.close()
        
        return jsonify({'id': record_id, 'message': 'Registro criado com sucesso'}), 201
    except sqlite3.IntegrityError:
        # Se já existe, atualiza
        cursor.execute('''
            UPDATE records 
            SET completed = ?, notes = ?
            WHERE habit_id = ? AND date = ?
        ''', (data.get('completed', 1), data.get('notes'), data['habit_id'], date))
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Registro atualizado com sucesso'})

@app.route('/api/records/<int:habit_id>', methods=['GET'])
def get_records(habit_id):
    """Retorna histórico de registros de um hábito"""
    days = request.args.get('days', 30, type=int)
    start_date = (datetime.now() - timedelta(days=days)).date()
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM records 
        WHERE habit_id = ? AND date >= ?
        ORDER BY date DESC
    ''', (habit_id, start_date))
    
    records = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify(records)

@app.route('/api/records/heatmap/<int:habit_id>', methods=['GET'])
def get_heatmap(habit_id):
    """Retorna dados para heatmap (tipo GitHub) dos últimos 365 dias"""
    db = get_db()
    cursor = db.cursor()
    
    start_date = (datetime.now() - timedelta(days=365)).date()
    
    cursor.execute('''
        SELECT date, completed FROM records 
        WHERE habit_id = ? AND date >= ?
        ORDER BY date
    ''', (habit_id, start_date))
    
    records = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return jsonify(records)

# ==================== ROTAS - ESTATÍSTICAS ====================

@app.route('/api/stats/overview', methods=['GET'])
def get_overview_stats():
    """Retorna estatísticas gerais do usuário"""
    db = get_db()
    cursor = db.cursor()
    
    # Total de hábitos ativos
    cursor.execute('SELECT COUNT(*) as total FROM habits WHERE active = 1')
    total_habits = cursor.fetchone()['total']
    
    # Hábitos completados hoje
    today = datetime.now().date().isoformat()
    cursor.execute('''
        SELECT COUNT(DISTINCT habit_id) as completed 
        FROM records 
        WHERE date = ? AND completed = 1
    ''', (today,))
    completed_today = cursor.fetchone()['completed']
    
    # Streak médio
    cursor.execute('SELECT id FROM habits WHERE active = 1')
    habit_ids = [row['id'] for row in cursor.fetchall()]
    
    total_streak = 0
    for hid in habit_ids:
        streak = calculate_streak(hid)
        total_streak += streak['current']
    
    avg_streak = round(total_streak / len(habit_ids), 1) if habit_ids else 0
    
    # Total de registros
    cursor.execute('SELECT COUNT(*) as total FROM records WHERE completed = 1')
    total_completions = cursor.fetchone()['total']
    
    db.close()
    
    return jsonify({
        'total_habits': total_habits,
        'completed_today': completed_today,
        'completion_rate_today': round((completed_today / total_habits * 100), 1) if total_habits > 0 else 0,
        'average_streak': avg_streak,
        'total_completions': total_completions
    })

@app.route('/api/stats/comparison', methods=['GET'])
def get_comparison_stats():
    """Compara estatísticas entre hábitos"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id, name FROM habits WHERE active = 1')
    habits = cursor.fetchall()
    
    comparison = []
    for habit in habits:
        streak = calculate_streak(habit['id'])
        rate = get_completion_rate(habit['id'], 30)
        
        comparison.append({
            'id': habit['id'],
            'name': habit['name'],
            'current_streak': streak['current'],
            'best_streak': streak['best'],
            'completion_rate_30d': rate
        })
    
    db.close()
    
    # Ordenar por streak atual
    comparison.sort(key=lambda x: x['current_streak'], reverse=True)
    
    return jsonify(comparison)

# ==================== ROTA INICIAL ====================

@app.route('/')
def home():
    """Página inicial da API"""
    return jsonify({
        'message': 'Habit Tracker API',
        'version': '1.0',
        'endpoints': {
            'categories': '/api/categories',
            'habits': '/api/habits',
            'records': '/api/records',
            'stats': '/api/stats/overview'
        }
    })

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print('🔧 Criando banco de dados...')
        init_db()
        print('✅ Banco de dados criado com sucesso!')
    
    print('\n🚀 Habit Tracker API rodando!')
    print('📍 Acesse: http://127.0.0.1:5000')
    print('📚 Documentação: http://127.0.0.1:5000/\n')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
