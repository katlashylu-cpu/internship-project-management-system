# app.py
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import hashlib  # For mock plagiarism check

app = Flask(__name__)
# Configure DATABASE_URL in your environment for MySQL. SQLite is used by default.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///internship.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-change-this-key')
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Database Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='In Progress')
    submissions = db.relationship('Submission', backref='project', lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    version = db.Column(db.Integer, default=1)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    plagiarism_score = db.Column(db.Float, nullable=True)
    evaluations = db.relationship('Evaluation', backref='submission', lazy=True)

class Rubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    criteria = db.relationship('Criterion', backref='rubric', lazy=True)

class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubric.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    max_points = db.Column(db.Integer, nullable=False)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)

# Mock plagiarism check
def check_plagiarism(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            score = int(hashlib.md5(content).hexdigest(), 16) % 100
            return score
    except Exception as e:
        print(f"Plagiarism check failed: {e}")
        return None

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/submit', methods=['GET', 'POST'])
def submit_project():
    if request.method == 'POST':
        title = request.form['title']
        student_id = request.form['student_id']
        file = request.files['file']
        
        if file:
            project = Project(title=title, student_id=student_id)
            db.session.add(project)
            db.session.commit()
            
            filename = f"{project.id}_v1_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            plagiarism_score = check_plagiarism(file_path)
            
            submission = Submission(project_id=project.id, file_path=file_path, plagiarism_score=plagiarism_score)
            db.session.add(submission)
            db.session.commit()
            
            flash(f'Project submitted successfully! Plagiarism score: {plagiarism_score}%', 'success')
            return redirect(url_for('index'))
    
    return render_template('submit.html')

@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project.html', project=project)

@app.route('/admin')
def admin_dashboard():
    total_projects = Project.query.count()
    completed_projects = Project.query.filter_by(status='Completed').count()
    completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
    projects = Project.query.all()
    return render_template('admin.html', total_projects=total_projects, 
                          completed_projects=completed_projects, 
                          completion_rate=completion_rate, projects=projects)

@app.route('/rubric/create', methods=['GET', 'POST'])
def create_rubric():
    if request.method == 'POST':
        name = request.form['name']
        criteria = request.form.getlist('criteria[]')
        max_points = request.form.getlist('max_points[]')
        rubric= Rubric(name=name)
        db.session.add(rubric)
        db.session.commit()
        
        for desc, points in zip(criteria, max_points):
            if desc and points:
                criterion = Criterion(rubric_id=rubric.id, description=desc, max_points=int(points))
                db.session.add(criterion)
        
        db.session.commit()
        flash('Rubric created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_rubric.html')

@app.route('/evaluate/<int:submission_id>', methods=['GET', 'POST'])
def evaluate_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    rubrics = Rubric.query.all()
    
    if request.method == 'POST':
        rubric_id = request.form['rubric_id']
        scores = request.form.getlist('scores[]')
        comments = request.form.getlist('comments[]')
        rubric = Rubric.query.get(rubric_id)
        criteria = Criterion.query.filter_by(rubric_id=rubric.id).all()
        for criterion, score, comment in zip(criteria, scores, comments):
            evaluation = Evaluation(
                submission_id=submission.id,
                criterion_id=criterion.id,
                score=int(score),
                comments=comment
            )
            db.session.add(evaluation)
        
        db.session.commit()
        flash('Evaluation submitted successfully!', 'success')
        return redirect(url_for('view_project', project_id=submission.project_id))
    
    return render_template('evaluate.html', submission=submission, rubrics=rubrics)

if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')