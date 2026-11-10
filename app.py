
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import hashlib

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///internship.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Use a private environment variable in production.
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'dev-only-change-this-key'
)

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

db = SQLAlchemy(app)


# Database Models

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='In Progress')

    submissions = db.relationship(
        'Submission',
        backref='project',
        lazy=True
    )


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id'),
        nullable=False
    )
    file_path = db.Column(db.String(200), nullable=False)
    version = db.Column(db.Integer, default=1)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    plagiarism_score = db.Column(db.Float, nullable=True)

    evaluations = db.relationship(
        'Evaluation',
        backref='submission',
        lazy=True
    )


class Rubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    criteria = db.relationship(
        'Criterion',
        backref='rubric',
        lazy=True
    )


class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rubric_id = db.Column(
        db.Integer,
        db.ForeignKey('rubric.id'),
        nullable=False
    )
    description = db.Column(db.String(200), nullable=False)
    max_points = db.Column(db.Integer, nullable=False)


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(
        db.Integer,
        db.ForeignKey('submission.id'),
        nullable=False
    )
    criterion_id = db.Column(
        db.Integer,
        db.ForeignKey('criterion.id'),
        nullable=False
    )
    score = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)


# Mock plagiarism check
def check_plagiarism(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            score = int(hashlib.md5(content).hexdigest(), 16) % 100
            return score

    except OSError as error:
        print(f"Plagiarism check failed: {error}")
        return None


# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Home page
@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)


# Submit project
@app.route('/submit', methods=['GET', 'POST'])
def submit_project():

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        student_id = request.form.get('student_id', '').strip()
        file = request.files.get('file')

        if not title or not student_id:
            flash('Please enter all required details.', 'danger')
            return redirect(url_for('submit_project'))

        if not file or not file.filename:
            flash('Please select a project file.', 'danger')
            return redirect(url_for('submit_project'))

        filename = secure_filename(file.filename)

        if not filename:
            flash('Invalid filename.', 'danger')
            return redirect(url_for('submit_project'))

        project = Project(
            title=title,
            student_id=student_id
        )

        db.session.add(project)
        db.session.commit()

        saved_filename = f"{project.id}_v1_{filename}"
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            saved_filename
        )

        file.save(file_path)

        plagiarism_score = check_plagiarism(file_path)

        submission = Submission(
            project_id=project.id,
            file_path=file_path,
            plagiarism_score=plagiarism_score
        )

        db.session.add(submission)
        db.session.commit()

        flash(
            'Project submitted successfully!',
            'success'
        )

        return redirect(url_for('index'))

    return render_template('submit.html')


# View project
@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)

    return render_template(
        'project.html',
        project=project
    )


# Admin dashboard
@app.route('/admin')
def admin_dashboard():

    total_projects = Project.query.count()

    completed_projects = Project.query.filter_by(
        status='Completed'
    ).count()

    completion_rate = (
        completed_projects / total_projects * 100
        if total_projects > 0 else 0
    )

    projects = Project.query.all()

    return render_template(
        'admin.html',
        total_projects=total_projects,
        completed_projects=completed_projects,
        completion_rate=completion_rate,
        projects=projects
    )


# Get rubric criteria (missing route added)
@app.route('/get_criteria/<int:rubric_id>')
def get_criteria(rubric_id):

    rubric = Rubric.query.get_or_404(rubric_id)

    criteria = [
        {
            'id': criterion.id,
            'description': criterion.description,
            'max_points': criterion.max_points
        }
        for criterion in rubric.criteria
    ]

    return jsonify({'criteria': criteria})


# Create rubric
@app.route('/rubric/create', methods=['GET', 'POST'])
def create_rubric():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        criteria = request.form.getlist('criteria[]')
        max_points = request.form.getlist('max_points[]')

        if not name:
            flash('Please enter a rubric name.', 'danger')
            return redirect(url_for('create_rubric'))

        if len(criteria) != len(max_points) or not criteria:
            flash('Please provide valid rubric criteria.', 'danger')
            return redirect(url_for('create_rubric'))

        rubric = Rubric(name=name)

        db.session.add(rubric)
        db.session.flush()

        for description, points in zip(criteria, max_points):

            description = description.strip()

            if not description:
                continue

            try:
                points = int(points)
            except (ValueError, TypeError):
                flash('Please enter valid points.', 'danger')
                db.session.rollback()
                return redirect(url_for('create_rubric'))

            if points <= 0:
                flash('Maximum points must be greater than zero.', 'danger')
                db.session.rollback()
                return redirect(url_for('create_rubric'))

            criterion = Criterion(
                rubric_id=rubric.id,
                description=description,
                max_points=points
            )

            db.session.add(criterion)

        db.session.commit()

        flash('Rubric created successfully!', 'success')

        return redirect(url_for('admin_dashboard'))

    return render_template('create_rubric.html')


# Evaluate submission
@app.route('/evaluate/<int:submission_id>', methods=['GET', 'POST'])
def evaluate_submission(submission_id):

    submission = Submission.query.get_or_404(submission_id)
    rubrics = Rubric.query.all()

    if request.method == 'POST':

        try:
            rubric_id = int(request.form.get('rubric_id', ''))
        except (ValueError, TypeError):
            flash('Please select a valid rubric.', 'danger')
            return redirect(
                url_for('evaluate_submission', submission_id=submission_id)
            )

        rubric = Rubric.query.get_or_404(rubric_id)
        criteria = Criterion.query.filter_by(
            rubric_id=rubric.id
        ).all()

        scores = request.form.getlist('scores[]')
        comments = request.form.getlist('comments[]')

        if not criteria or len(scores) != len(criteria):
            flash('Please provide scores for all criteria.', 'danger')
            return redirect(
                url_for('evaluate_submission', submission_id=submission_id)
            )

        evaluations = []

        for criterion, score, comment in zip(criteria, scores, comments):

            try:
                score = int(score)
            except (ValueError, TypeError):
                flash('Please enter valid scores.', 'danger')
                return redirect(
                    url_for(
                        'evaluate_submission',
                        submission_id=submission_id
                    )
                )

            if score < 0 or score > criterion.max_points:
                flash(
                    f'Score for {criterion.description} must be between 0 and {criterion.max_points}.',
                    'danger'
                )
                return redirect(
                    url_for(
                        'evaluate_submission',
                        submission_id=submission_id
                    )
                )

            evaluations.append(
                Evaluation(
                    submission_id=submission.id,
                    criterion_id=criterion.id,
                    score=score,
                    comments=comment
                )
            )

        db.session.add_all(evaluations)
        db.session.commit()

        flash('Evaluation submitted successfully!', 'success')

        return redirect(
            url_for(
                'view_project',
                project_id=submission.project_id
            )
        )

    return render_template(
        'evaluate.html',
        submission=submission,
        rubrics=rubrics
    )


# Application entry point
if __name__ == '__main__':

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")

    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
