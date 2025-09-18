
import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for

# --- CONFIGURATION ---
PORT = 5001
DB_NAME = "training_v1.db" # Changed DB name for v1

# --- TRAINING PLAN (Simplified for v1) ---
# This will be a fixed plan for September 2025
# The HTML will be generated directly based on this.

# --- HTML & CSS TEMPLATE (in a single string) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan de Entrenamiento v1</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Plan de Entrenamiento - Septiembre 2025 (v1)</h1>
    <form action="/save" method="post">
        {daily_sections}
        <button type="submit" class="save-btn">Guardar Progreso</button>
    </form>
</body>
</html>
"""

# --- DATABASE & DATA LOGIC ---
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS log (id INTEGER PRIMARY KEY, date TEXT, exercise TEXT, completed INTEGER, notes TEXT)')
    conn.commit()
    conn.close()

# --- FLASK APPLICATION ---
app = Flask(__name__)

@app.route('/')
def index():
    daily_sections_html = ""
    exercise_counter = 0

    conn = get_db()
    # Fetch all saved exercises to pre-fill the form
    saved_exercises = conn.execute('SELECT date, exercise, completed, notes FROM log').fetchall()
    conn.close()

    # Organize saved exercises for easy lookup
    # {'YYYY-MM-DD': {'Exercise Name': {'completed': 1/0, 'notes': '...'}}}
    saved_data = {}
    for row in saved_exercises:
        date = row['date']
        exercise_name = row['exercise']
        completed = row['completed']
        notes = row['notes']
        if date not in saved_data:
            saved_data[date] = {}
        saved_data[date][exercise_name] = {'completed': completed, 'notes': notes}

    for month, weeks in TRAINING_PLAN.items():
        # daily_sections_html += f"<h2>{month}</h2>" # Uncomment if you want a month title
        for week_name, days in weeks.items():
            daily_sections_html += f"<div class=\"week\"><h2>{week_name}</h2>"
            for date_str, day_data in days.items():
                daily_sections_html += f"<div class=\"day\"><h3>{day_data['day_name']}</h3>"
                if day_data['exercises']:
                    daily_sections_html += "<tr>"
                    for header in day_data['headers']:
                        daily_sections_html += f"<th>{header}</th>"
                    daily_sections_html += "</tr>"

                    for exercise in day_data['exercises']:
                        # Check if this exercise was completed on this date
                        exercise_saved_data = saved_data.get(date_str, {}).get(exercise['name'], {})
                        is_completed = exercise_saved_data.get('completed', 0)
                        saved_notes = exercise_saved_data.get('notes', '')
                        
                        checked_attr = "checked" if is_completed else ""
                        
                        # Generate exercise details dynamically
                        exercise_details_html = ""
                        for key, value in exercise.items():
                            if key != "name": # 'name' is handled separately
                                exercise_details_html += f"<td>{value}</td>"

                        daily_sections_html += f'''
                            <input type="hidden" name="date_{exercise_counter}" value="{date_str}">
                            <tr>
                                <input type="hidden" name="exercise_{exercise_counter}" value="{exercise["name"]}">
                                <td>{exercise["name"]}</td>
                                {exercise_details_html}
                                <td class="completed-checkbox"><input type="checkbox" name="completed_{exercise_counter}" {checked_attr}></td>
                                <td><input type="text" class="notes-input" name="notes_{exercise_counter}" value="{saved_notes}"></td>
                            </tr>
                        '''
                        exercise_counter += 1
                    daily_sections_html += "</table>"
                else:
                    daily_sections_html += "<p>Día de descanso o sin ejercicios programados.</p>" # Added for rest days
                daily_sections_html += "</div>"
            daily_sections_html += "</div>"

    return HTML_TEMPLATE.format(daily_sections=daily_sections_html)

    # --- TRAINING PLAN (Dynamic) ---
TRAINING_PLAN = {
    "September 2025": {
        "Week 3 (17-21 de Septiembre)": {
            "2025-09-17": {
                "day_name": "Miercoles, 17 de Septiembre - Rutina A + Cardio",
                "exercises": [
                    {"name": "Puente de Glúteos", "series": "3", "reps": "15-20", "rest": "60 seg"},
                    {"name": "Flexiones Inclinadas", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Remo con Ligas", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Plancha (sobre antebrazos)", "series": "3", "reps": "30-60 seg", "rest": "45 seg"},
                    {"name": "Curl de Bíceps con Ligas", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-18": {
                "day_name": "Jueves, 18 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            },
            "2025-09-19": {
                "day_name": "Viernes, 19 de Septiembre - Rutina B + Cardio",
                "exercises": [
                    {"name": "Sentadillas (Squats)", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Dominadas Asistidas/Negativas", "series": "3", "reps": "5-8 o Al fallo*", "rest": "90 seg"},
                    {"name": "Aperturas con Ligas (Chest Flys)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro (Bird-Dog)", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Peso Muerto Rumano (SIN PESO)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Elevaciones Laterales", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-20": {
                "day_name": "Sábado, 20 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            },
            "2025-09-21": {
                "day_name": "Domingo, 21 de Septiembre - Descanso",
                "exercises": [],
                "headers": []
            }
        },
        "Week 4 (22-28 de Septiembre)": {
            "2025-09-22": {
                "day_name": "Lunes, 22 de Septiembre - Rutina A + Cardio",
                "exercises": [
                    {"name": "Puente de Glúteos", "series": "3", "reps": "15-20", "rest": "60 seg"},
                    {"name": "Flexiones Inclinadas", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Remo con Ligas", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Plancha (sobre antebrazos)", "series": "3", "reps": "30-60 seg", "rest": "45 seg"},
                    {"name": "Curl de Bíceps con Ligas", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-23": {
                "day_name": "Martes, 23 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            },
            "2025-09-24": {
                "day_name": "Miercoles, 24 de Septiembre - Rutina B + Cardio",
                "exercises": [
                    {"name": "Sentadillas (Squats)", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Dominadas Asistidas/Negativas", "series": "3", "reps": "5-8 o Al fallo*", "rest": "90 seg"},
                    {"name": "Aperturas con Ligas (Chest Flys)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro (Bird-Dog)", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Peso Muerto Rumano (SIN PESO)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Elevaciones Laterales", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-25": {
                "day_name": "Jueves, 25 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            },
            "2025-09-26": {
                "day_name": "Viernes, 26 de Septiembre - Rutina A + Cardio",
                "exercises": [
                    {"name": "Puente de Glúteos", "series": "3", "reps": "15-20", "rest": "60 seg"},
                    {"name": "Flexiones Inclinadas", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Remo con Ligas", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Plancha (sobre antebrazos)", "series": "3", "reps": "30-60 seg", "rest": "45 seg"},
                    {"name": "Curl de Bíceps con Ligas", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-27": {
                "day_name": "Sábado, 27 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            },
            "2025-09-28": {
                "day_name": "Domingo, 28 de Septiembre - Descanso",
                "exercises": [],
                "headers": []
            }
        },
        "Week 5 (29-30 de Septiembre)": {
            "2025-09-29": {
                "day_name": "Lunes, 29 de Septiembre - Rutina B + Cardio",
                "exercises": [
                    {"name": "Sentadillas (Squats)", "series": "3", "reps": "10-15", "rest": "60 seg"},
                    {"name": "Dominadas Asistidas/Negativas", "series": "3", "reps": "5-8 o Al fallo*", "rest": "90 seg"},
                    {"name": "Aperturas con Ligas (Chest Flys)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Pájaro-Perro (Bird-Dog)", "series": "3", "reps": "10 (c/lado)", "rest": "45 seg"},
                    {"name": "Peso Muerto Rumano (SIN PESO)", "series": "3", "reps": "12-15", "rest": "60 seg"},
                    {"name": "Elevaciones Laterales", "series": "2", "reps": "15-20", "rest": "45 seg"},
                    {"name": "Cardio Moderado", "series": "1", "reps": "20-30 min", "rest": "N/A"}
                ],
                "headers": ["Ejercicio", "Series", "Repeticiones", "Descanso", "Completado", "Notas"]
            },
            "2025-09-30": {
                "day_name": "Martes, 30 de Septiembre - Yoga y Movilidad",
                "exercises": [
                    {"name": "Postura del Gato-Vaca", "duration": "10 repeticiones"},
                    {"name": "Perro Boca Abajo (rodillas dobladas)", "duration": "30-60 seg"},
                    {"name": "Postura de la Cobra (suave)", "duration": "3-5 respiraciones"},
                    {"name": "Postura del Niño", "duration": "60 seg"}
                ],
                "headers": ["Ejercicio", "Duración/Repeticiones", "Completado", "Notas"]
            }
        }
    }
}

# --- HTML & CSS TEMPLATE (in a single string) ---

    return HTML_TEMPLATE.format(daily_sections=daily_sections_html)

@app.route('/save', methods=['POST'])
def save():
    conn = get_db()
    # In v1, we save all exercises from the form for the current day
    # We need to get the date from the form, as it's not necessarily today
    
    # Find the date from the first exercise's hidden input
    # This assumes at least one exercise is submitted
    submitted_date = None
    for key in request.form:
        if key.startswith('date_'):
            submitted_date = request.form[key]
            break

    if not submitted_date:
        # Fallback to today if date not found (shouldn't happen with correct form)
        submitted_date = datetime.now().date().isoformat()

    i = 0
    while f'exercise_{i}' in request.form:
        exercise = request.form[f'exercise_{i}']
        completed = 1 if f'completed_{i}' in request.form else 0
        notes = request.form.get(f'notes_{i}', '') # v1 includes notes
        
        # Check if a record for this exercise on this date already exists
        exists = conn.execute('SELECT id FROM log WHERE date = ? AND exercise = ?', (submitted_date, exercise)).fetchone()
        if exists:
            conn.execute('UPDATE log SET completed = ? WHERE id = ?', (completed, exists['id']))
        else:
            conn.execute('INSERT INTO log (date, exercise, completed) VALUES (?, ?, ?)', (submitted_date, exercise, completed))
        i += 1
        
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=False, host='0.0.0.0', port=PORT)
