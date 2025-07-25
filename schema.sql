-- Drop tables if they exist to ensure a clean slate on re-initialization.
DROP TABLE IF EXISTS proof_of_work;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS semesters;
DROP TABLE IF EXISTS streams;
DROP TABLE IF EXISTS universities;
DROP TABLE IF EXISTS users;


-- Main hierarchy tables
CREATE TABLE universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER NOT NULL UNIQUE
);

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher'))
);

-- Subjects table linked to the hierarchy
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    university_id INTEGER NOT NULL,
    stream_id INTEGER NOT NULL,
    semester_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL, -- The teacher who created/owns it
    FOREIGN KEY (university_id) REFERENCES universities (id),
    FOREIGN KEY (stream_id) REFERENCES streams (id),
    FOREIGN KEY (semester_id) REFERENCES semesters (id),
    FOREIGN KEY (teacher_id) REFERENCES users (id)
);

-- Modules table links to subjects
CREATE TABLE modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

-- Content for each module
CREATE TABLE content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    content_type TEXT NOT NULL CHECK(content_type IN ('text', 'video_url')),
    data TEXT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules (id)
);

-- Tasks for each module
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules (id)
);

-- Proof of Work submissions by students
CREATE TABLE proof_of_work (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    comments TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);