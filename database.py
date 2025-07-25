import sqlite3
import click
from flask import current_app, g

# --- Core Database Connection & Setup ---

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('✅ Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# --- Helper for safe queries ---
def query_db(query, args=(), one=False):
    try:
        db = get_db()
        cur = db.execute(query, args)
        rv = cur.fetchall()
        db.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        print(f"Database query failed: {e}")
        return None if one else []

# --- User Management Functions ---
def add_user(username, email, password_hash, role):
    query_db('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
             (username, email, password_hash, role))

def get_user_by_email(email):
    return query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)

# --- Teacher Admin: Create Functions ---

def add_or_get_university(name):
    uni = query_db('SELECT id FROM universities WHERE name = ?', (name,), one=True)
    if uni:
        return uni['id']
    # For INSERT, we need a different way to get the last row id
    db = get_db()
    cursor = db.execute('INSERT INTO universities (name) VALUES (?)', (name,))
    db.commit()
    return cursor.lastrowid

def add_or_get_stream(name):
    stream = query_db('SELECT id FROM streams WHERE name = ?', (name,), one=True)
    if stream:
        return stream['id']
    db = get_db()
    cursor = db.execute('INSERT INTO streams (name) VALUES (?)', (name,))
    db.commit()
    return cursor.lastrowid

def add_or_get_semester(number):
    sem = query_db('SELECT id FROM semesters WHERE number = ?', (number,), one=True)
    if sem:
        return sem['id']
    db = get_db()
    cursor = db.execute('INSERT INTO semesters (number) VALUES (?)', (number,))
    db.commit()
    return cursor.lastrowid

def add_subject(name, uni_id, stream_id, sem_id, teacher_id):
    query_db('INSERT INTO subjects (name, university_id, stream_id, semester_id, teacher_id) VALUES (?, ?, ?, ?, ?)',
             (name, uni_id, stream_id, sem_id, teacher_id))

def add_module(subject_id, title):
    query_db('INSERT INTO modules (subject_id, title) VALUES (?, ?)', (subject_id, title))

def add_content_to_module(module_id, content_type, data):
    query_db('INSERT INTO content (module_id, content_type, data) VALUES (?, ?, ?)',
             (module_id, content_type, data))

def add_task_to_module(module_id, description):
    query_db('INSERT INTO tasks (module_id, description) VALUES (?, ?)',
             (module_id, description))

# --- Teacher Admin: Get Functions ---
def get_subjects_by_teacher(teacher_id):
    return query_db('SELECT * FROM subjects WHERE teacher_id = ?', (teacher_id,))

# --- Student & General Get Functions ---
def get_all_subjects():
    return query_db('''
        SELECT s.id, s.name, u.name as uni_name, st.name as stream_name, sem.number as sem_number
        FROM subjects s
        JOIN universities u ON s.university_id = u.id
        JOIN streams st ON s.stream_id = st.id
        JOIN semesters sem ON s.semester_id = sem.id
        ORDER BY s.name
    ''')

def get_subject_by_id(subject_id):
    return query_db('SELECT * FROM subjects WHERE id = ?', (subject_id,), one=True)

def get_modules_by_subject(subject_id):
    return query_db('SELECT * FROM modules WHERE subject_id = ? ORDER BY title', (subject_id,))

def get_module_by_id(module_id):
    return query_db('SELECT * FROM modules WHERE id = ?', (module_id,), one=True)

def get_module_content(module_id):
    return query_db('SELECT * FROM content WHERE module_id = ?', (module_id,))

def get_module_tasks(module_id):
    return query_db('SELECT * FROM tasks WHERE module_id = ?', (module_id,))

def get_task_by_id(task_id):
    return query_db('SELECT * FROM tasks WHERE id = ?', (task_id,), one=True)

def add_proof_of_work(task_id, user_id, file_path, comments):
    query_db('INSERT INTO proof_of_work (task_id, user_id, file_path, comments) VALUES (?, ?, ?, ?)',
             (task_id, user_id, file_path, comments))

def get_user_submissions_for_module(user_id, module_id):
    return query_db('''
        SELECT p.task_id FROM proof_of_work p
        JOIN tasks t ON p.task_id = t.id
        WHERE p.user_id = ? AND t.module_id = ?
    ''', (user_id, module_id))