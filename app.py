from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import database
from functools import wraps

app = Flask(__name__)

# --- Configuration ---
app.config.from_mapping(
    SECRET_KEY='a_very_secret_key_that_should_be_changed',
    DATABASE=os.path.join(app.instance_path, 'wiki_syllabus.db'),
)
app.config['UPLOAD_FOLDER'] = 'uploads'

try:
    os.makedirs(app.instance_path)
    os.makedirs(app.config['UPLOAD_FOLDER'])
except OSError:
    pass

# --- Initialize Database with App ---
database.init_app(app)

# --- Decorator for protecting teacher routes ---
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'teacher':
            flash("You do not have permission to access this page.")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- User Authentication Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if database.get_user_by_email(email):
            flash('Email is already registered.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        database.add_user(username, email, hashed_password, role)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = database.get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

# --- Main Student-Facing Routes ---
def check_auth():
    if 'user_id' not in session:
        flash("You need to be logged in to view this page.")
        return False
    return True

@app.route('/dashboard')
def dashboard():
    if not check_auth():
        return redirect(url_for('login'))
    
    if session['role'] == 'student':
        subjects = database.get_all_subjects()
        return render_template('dashboard.html', subjects=subjects)
    
    if session['role'] == 'teacher':
        return redirect(url_for('admin_dashboard'))

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    if not check_auth():
        return redirect(url_for('login'))
    subject = database.get_subject_by_id(subject_id)
    modules = database.get_modules_by_subject(subject_id)
    if not subject:
        flash("Subject not found.")
        return redirect(url_for('dashboard'))
    return render_template('subject.html', subject=subject, modules=modules)

@app.route('/module/<int:module_id>')
def module(module_id):
    if not check_auth():
        return redirect(url_for('login'))
    module_details = database.get_module_by_id(module_id)
    if not module_details:
        flash("Module not found.")
        return redirect(url_for('dashboard'))
    content = database.get_module_content(module_id)
    tasks = database.get_module_tasks(module_id)
    user_submissions = database.get_user_submissions_for_module(session['user_id'], module_id)
    submitted_task_ids = {sub['task_id'] for sub in user_submissions}
    return render_template('module.html', module=module_details, content=content, tasks=tasks, submitted_task_ids=submitted_task_ids)

@app.route('/task/<int:task_id>/submit', methods=['GET', 'POST'])
def submit_proof_of_work(task_id):
    if not check_auth():
        return redirect(url_for('login'))
    task = database.get_task_by_id(task_id)
    if not task:
        flash("Task not found.")
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        comments = request.form['comments']
        file = request.files.get('proof')
        if not file or file.filename == '':
            flash('You must select a file to upload.')
            return redirect(request.url)
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        database.add_proof_of_work(task_id, session['user_id'], file_path, comments)
        flash('Proof of Work submitted successfully!')
        return redirect(url_for('module', module_id=task['module_id']))
    return render_template('submit_proof.html', task=task)

# --- Teacher Admin Routes ---

@app.route('/admin')
@teacher_required
def admin_dashboard():
    teacher_id = session['user_id']
    subjects = database.get_subjects_by_teacher(teacher_id)
    return render_template('admin/admin_dashboard.html', subjects=subjects)

@app.route('/admin/subject/add', methods=['GET', 'POST'])
@teacher_required
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        university_name = request.form['university_name']
        stream_name = request.form['stream_name']
        semester_number = request.form['semester_number']
        teacher_id = session['user_id']
        uni_id = database.add_or_get_university(university_name)
        stream_id = database.add_or_get_stream(stream_name)
        sem_id = database.add_or_get_semester(semester_number)
        database.add_subject(subject_name, uni_id, stream_id, sem_id, teacher_id)
        flash(f"Subject '{subject_name}' created successfully!")
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_subject.html')

@app.route('/admin/subject/<int:subject_id>/manage', methods=['GET', 'POST'])
@teacher_required
def manage_subject(subject_id):
    subject = database.get_subject_by_id(subject_id)
    if not subject or subject['teacher_id'] != session['user_id']:
        flash("Subject not found or you don't have permission to edit it.")
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        module_title = request.form['module_title']
        database.add_module(subject_id, module_title)
        flash(f"Module '{module_title}' added successfully.")
        return redirect(url_for('manage_subject', subject_id=subject_id))
    modules = database.get_modules_by_subject(subject_id)
    return render_template('admin/manage_subject.html', subject=subject, modules=modules)

@app.route('/admin/module/<int:module_id>/manage', methods=['GET', 'POST'])
@teacher_required
def manage_module(module_id):
    module = database.get_module_by_id(module_id)
    subject = database.get_subject_by_id(module['subject_id'])
    if not subject or subject['teacher_id'] != session['user_id']:
        flash("You do not have permission to edit this module.")
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        if 'add_content' in request.form:
            content_data = request.form['content_data']
            database.add_content_to_module(module_id, 'text', content_data)
            flash("New content added successfully.")
        elif 'add_task' in request.form:
            task_description = request.form['task_description']
            database.add_task_to_module(module_id, task_description)
            flash("New task added successfully.")
        return redirect(url_for('manage_module', module_id=module_id))
    existing_content = database.get_module_content(module_id)
    existing_tasks = database.get_module_tasks(module_id)
    return render_template('admin/manage_module.html', 
                           module=module, 
                           content=existing_content, 
                           tasks=existing_tasks)

if __name__ == '__main__':
    app.run(debug=True)