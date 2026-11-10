
# Internship & Project Management System

A web-based application developed using Python and Flask to manage internship project submissions, track progress, and evaluate student projects using customizable rubrics.

## Features

- Submit and manage student internship projects
- Upload project documents
- Track project status and submission versions
- Create evaluation rubrics with multiple criteria
- Evaluate submissions using scores and comments
- View project details and submission history
- Admin dashboard with project statistics and completion rate

## Technology Stack

- **Backend:** Python, Flask
- **Database:** SQLite / MySQL
- **ORM:** Flask-SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Template Engine:** Jinja2

## Project Structure

```text
internship-project-management-system/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── submit.html
│   ├── project.html
│   ├── admin.html
│   ├── create_rubric.html
│   └── evaluate.html
│
└── uploads/
    └── .gitkeep
```

## Installation and Setup

1. Install Python 3.10 or later.

2. Clone the repository:

   ```bash
   git clone https://github.com/katlashylu-cpu/internship-project-management-system.git
   ```

3. Navigate to the project directory:

   ```bash
   cd internship-project-management-system
   ```

4. Create and activate a virtual environment.

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Configure your environment variables:
   - Set a private `SECRET_KEY`.
   - Optionally configure `DATABASE_URL` to use MySQL.
   - SQLite is used by default.

7. Run the application:

   ```bash
   python app.py
   ```

8. Open your browser:

   http://127.0.0.1:5000/

## Database Configuration

The application uses SQLite by default.

To use MySQL, configure `DATABASE_URL`:

```text
mysql+pymysql://USERNAME:PASSWORD@localhost/internship_db
```

## Important Limitation

The current plagiarism-checking function uses an MD5 file hash to generate a placeholder score. It does not perform genuine plagiarism detection.

## Security Considerations

- Local database files and uploaded documents are excluded from version control.
- Configure a strong secret key through environment variables.
- Authentication and authorization should be implemented before public deployment.
- Uploaded file types and sizes should be validated before accepting untrusted files.

## Project Status

This is a portfolio version of the Internship & Project Management System. Local testing is recommended before deployment.

