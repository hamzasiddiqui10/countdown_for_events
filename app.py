from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)


def init_db():
    # Create DB tables inside application context to avoid "Working outside of application context"
    with app.app_context():
        db.create_all()


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password required')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return render_template('register.html')
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Signed in successfully')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Signed out')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    events = Event.query.filter_by(user_id=user.id).order_by(Event.event_time).all()
    return render_template('dashboard.html', events=events, user=user)


@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if request.method == 'POST':
        name = request.form['name'].strip()
        when = request.form['event_time']
        if not name or not when:
            flash('Both name and time are required')
            return render_template('event_form.html')
        # datetime-local gives 'YYYY-MM-DDTHH:MM'
        try:
            dt = datetime.fromisoformat(when)
        except Exception:
            flash('Invalid date/time format')
            return render_template('event_form.html')
        ev = Event(user_id=current_user().id, name=name, event_time=dt)
        db.session.add(ev)
        db.session.commit()
        flash('Event created')
        return redirect(url_for('dashboard'))
    return render_template('event_form.html')


@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    ev = Event.query.get_or_404(event_id)
    if ev.user_id != current_user().id:
        abort(403)
    if request.method == 'POST':
        name = request.form['name'].strip()
        when = request.form['event_time']
        if not name or not when:
            flash('Both name and time are required')
            return render_template('event_form.html', event=ev)
        try:
            dt = datetime.fromisoformat(when)
        except Exception:
            flash('Invalid date/time format')
            return render_template('event_form.html', event=ev)
        ev.name = name
        ev.event_time = dt
        db.session.commit()
        flash('Event updated')
        return redirect(url_for('dashboard'))
    return render_template('event_form.html', event=ev)


@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    ev = Event.query.get_or_404(event_id)
    if ev.user_id != current_user().id:
        abort(403)
    db.session.delete(ev)
    db.session.commit()
    flash('Event deleted')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    # Ensure DB exists
    init_db()
    app.run(debug=True)
