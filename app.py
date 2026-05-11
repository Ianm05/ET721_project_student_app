from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize database
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --------------------
# DATABASE MODEL
# --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# --------------------
# USER LOADER
# --------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------
# ROUTES
# --------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash('Login successful!')
            return redirect(url_for('dashboard'))

        else:
            flash('Invalid username or password')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# --------------------
# TASK ROUTES
# --------------------

@app.route('/tasks')
@login_required
def tasks():

    user_tasks = Task.query.filter_by(user_id=current_user.id).all()

    return render_template('tasks.html', tasks=user_tasks)


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():

    if request.method == 'POST':

        title = request.form.get('title')
        category = request.form.get('category')

        new_task = Task(
            title=title,
            category=category,
            user_id=current_user.id
        )

        db.session.add(new_task)
        db.session.commit()

        flash('Task added successfully!')
        return redirect(url_for('tasks'))

    return render_template('add_task.html')


@app.route('/complete_task/<int:id>')
@login_required
def complete_task(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('tasks'))

    task.completed = True
    db.session.commit()

    flash('Task completed!')
    return redirect(url_for('tasks'))


@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('tasks'))

    db.session.delete(task)
    db.session.commit()

    flash('Task deleted!')
    return redirect(url_for('tasks'))


# --------------------
# BLOG ROUTES
# --------------------

@app.route('/blogs')
@login_required
def blogs():

    all_blogs = Blog.query.all()

    return render_template('blogs.html', blogs=all_blogs)


@app.route('/add_blog', methods=['GET', 'POST'])
@login_required
def add_blog():

    if request.method == 'POST':

        title = request.form.get('title')
        content = request.form.get('content')

        new_blog = Blog(
            title=title,
            content=content,
            user_id=current_user.id
        )

        db.session.add(new_blog)
        db.session.commit()

        flash('Blog created!')
        return redirect(url_for('blogs'))

    return render_template('add_blog.html')


@app.route('/delete_blog/<int:id>')
@login_required
def delete_blog(id):

    blog = Blog.query.get_or_404(id)

    if blog.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('blogs'))

    db.session.delete(blog)
    db.session.commit()

    flash('Blog deleted!')
    return redirect(url_for('blogs'))


# --------------------
# LOGOUT
# --------------------

@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash('Logged out successfully')
    return redirect(url_for('home'))


# --------------------
# CREATE DATABASE
# --------------------

with app.app_context():
    db.create_all()


# --------------------
# RUN APP
# --------------------

if __name__ == '__main__':
    app.run(debug=True)