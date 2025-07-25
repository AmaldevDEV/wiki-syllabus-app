# Wiki Syllabus

Wiki Syllabus empowers teachers to easily build dynamic, step-by-step courses from the ground up. For students, it transforms the learning process into a clear, interactive roadmap where they can track progress and showcase their work.

This is a full-stack web application built with Python and Flask.

## Key Features

-   **Dual User Roles:** Secure registration and login for both Students and Teachers.
-   **Teacher Admin Panel:** A protected area for teachers to create and manage the entire course hierarchy (Subjects, Modules, Content, and Tasks).
-   **Student Dashboard:** A clean interface for students to view available courses and navigate through modules.
-   **Proof of Work:** Functionality for students to upload and submit their work for tasks.

## Tech Stack

-   **Backend:** Python, Flask
-   **Database:** SQLite
-   **Frontend:** HTML, CSS, Bootstrap

## How to Run Locally

1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Set the Flask environment variable: `export FLASK_APP=app.py` (or `set FLASK_APP=app.py` on Windows).
4.  Initialize the database: `flask init-db`
5.  Run the application: `flask run`
