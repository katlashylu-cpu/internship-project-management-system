# Internship & Project Management System

A Flask-based web application for managing internship project submissions and evaluations.

## Features

- Create and view student project submissions
- Upload project files
- Track project status
- Create evaluation rubrics and criteria
- Record evaluator scores and comments
- View an admin dashboard with project completion statistics
- Track submission versions in the database model

## Technology stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite (default) or MySQL
- HTML, CSS, Bootstrap and JavaScript in Jinja templates

## Project structure

```text
.
├── app.py
├── requirements.txt
├── .env.example
├── templates/
└── uploads/
```

## Run locally

1. Install Python 3.10 or later.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Configure MySQL by setting `DATABASE_URL` in your environment. Example:

   ```text
   mysql+pymysql://USERNAME:PASSWORD@localhost/internship_db
   ```

   If `DATABASE_URL` is not set, the application uses SQLite and creates `instance/internship.db` automatically.

5. Set a private secret key in the `SECRET_KEY` environment variable before deployment. Do not commit secrets to GitHub.
6. Start the application:

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000/` in your browser.

## Important limitation

The current `check_plagiarism()` function calculates a deterministic value from an MD5 file hash. It is a placeholder/mock score, **not a genuine plagiarism detection system**. Do not present this score as a real plagiarism result.

## Security notes

- Uploaded files and local databases are excluded from this repository.
- Configure a strong `SECRET_KEY` outside source control.
- Add authentication and authorization before deploying this application publicly. The current admin route is not protected by login authentication.
- Validate and restrict uploaded file types and sizes before using this application with untrusted users.

## Status

This repository is a cleaned portfolio copy of the project. Test it in your own environment before deployment.
