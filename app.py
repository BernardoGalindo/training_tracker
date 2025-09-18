from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# --- TRAINING PLAN ---
# (This should be in a separate config file in a real app)
TRAINING_PLAN = {
    0: {"name": "Rutina A + Cardio", "icon": "💪"}, # Monday
    1: {"name": "Yoga y Movilidad", "icon": "🧘"},  # Tuesday
    2: {"name": "Rutina B + Cardio", "icon": "💪"}, # Wednesday
    3: {"name": "Yoga y Movilidad", "icon": "🧘"},  # Thursday
    4: {"name": "Rutina A + Cardio", "icon": "💪"}, # Friday
    5: {"name": "Yoga y Movilidad", "icon": "🧘"},  # Saturday
    6: {"name": "Descanso", "icon": "😴"}     # Sunday
}

EXERCISES = {
    "Rutina A + Cardio": [
        {"name": "Puente de Glúteos", "details": "3s, 15-20r"},
        {"name": "Flexiones Inclinadas", "details": "3s, 10-15r"},
        {"name": "Remo con Ligas", "details": "3s, 12-15r"},
        {"name": "Pájaro-Perro", "details": "3s, 10r c/l"},
        {"name": "Plancha", "details": "3s, 30-60s"},
        {"name": "Curl de Bíceps", "details": "2s, 15-20r"},
        {"name": "Cardio Moderado", "details": "20-30m"}
    ],
    "Rutina B + Cardio": [
        {"name": "Sentadillas", "details": "3s, 10-15r"},
        {"name": "Dominadas Asistidas", "details": "3s, 5-8r"},
        {"name": "Aperturas con Ligas", "details": "3s, 12-15r"},
        {"name": "Pájaro-Perro", "details": "3s, 10r c/l"},
        {"name": "Peso Muerto Rumano", "details": "3s, 12-15r"},
        {"name": "Elevaciones Laterales", "details": "2s, 15-20r"},
        {"name": "Cardio Moderado", "details": "20-30m"}
    ],
    "Yoga y Movilidad": [
        {"name": "Gato-Vaca", "details": "10r"},
        {"name": "Perro Boca Abajo", "details": "30-60s"},
        {"name": "Cobra (suave)", "details": "3-5 resp"},
        {"name": "Postura del Niño", "details": "60s"}
    ],
    "Descanso": []
}

# --- DATABASE HELPERS ---
def get_db_connection():
    conn = sqlite3.connect('training.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS training_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            feeling TEXT,
            achievement TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- DASHBOARD DATA FUNCTIONS ---
def get_dashboard_data():
    conn = get_db_connection()
    today = datetime.now().date()
    
    # Streak
    dates = [datetime.strptime(row['date'], '%Y-%m-%d').date() for row in conn.execute("SELECT DISTINCT date FROM training_log WHERE completed = 1 ORDER BY date DESC").fetchall()]
    streak = 0
    if dates:
        if dates[0] in [today, today - timedelta(days=1)]:
            streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]).days == 1: streak += 1
                else: break

    # Workouts this week
    start_of_week = today - timedelta(days=today.weekday())
    workouts_this_week = conn.execute("SELECT COUNT(DISTINCT date) FROM training_log WHERE date >= ?", (start_of_week.isoformat(),)).fetchone()[0]

    # Chart data (last 4 weeks)
    chart_data = []
    for i in range(4):
        start = today - timedelta(days=today.weekday() + (3-i)*7)
        end = start + timedelta(days=6)
        chart_data.append(conn.execute("SELECT COUNT(DISTINCT date) FROM training_log WHERE date BETWEEN ? AND ?", (start.isoformat(), end.isoformat())).fetchone()[0])

    # Weekly calendar view
    weekly_calendar = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        routine_name = TRAINING_PLAN[day_date.weekday()]['name']
        icon = TRAINING_PLAN[day_date.weekday()]['icon']
        weekly_calendar.append({"date": day_date, "routine": routine_name, "icon": icon})

    # Today's workout
    todays_routine_name = TRAINING_PLAN[today.weekday()]['name']
    todays_workout = EXERCISES[todays_routine_name]

    conn.close()
    return {
        "streak": streak,
        "workouts_this_week": workouts_this_week,
        "chart_data": chart_data,
        "weekly_calendar": weekly_calendar,
        "todays_workout": todays_workout,
        "today": today
    }

# --- ROUTES ---
@app.route('/')
def index():
    dashboard_data = get_dashboard_data()
    return render_template('index.html', **dashboard_data)

@app.route('/save', methods=['POST'])
def save():
    conn = get_db_connection()
    date = request.form.get('date')
    exercises = request.form.getlist('exercise')
    
    for i in range(len(exercises)):
        exercise = exercises[i]
        completed = 1 if f'completed_{i}' in request.form else 0
        feeling = request.form.get(f'feeling_{i}')
        achievement = request.form.get(f'achievement_{i}')
        
        # Check if a record for this exercise on this date already exists
        exists = conn.execute('SELECT id FROM training_log WHERE date = ? AND exercise = ?', (date, exercise)).fetchone()
        if exists:
            conn.execute('UPDATE training_log SET completed = ?, feeling = ?, achievement = ? WHERE id = ?',
                         (completed, feeling, achievement, exists['id']))
        else:
            conn.execute('INSERT INTO training_log (date, exercise, completed, feeling, achievement) VALUES (?, ?, ?, ?, ?)',
                         (date, exercise, completed, feeling, achievement))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('training.db'):
        init_db()
    app.run(debug=True, port=5001) # Using a different port to avoid browser cache issues