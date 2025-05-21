from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .models import db, User, Startup, FundingRound # Adjusted imports
from .forms import RegistrationForm, LoginForm, StartupForm # Import StartupForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # It's important to set a secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app) # Initialize db with the app

login_manager = LoginManager(app)
login_manager.login_view = 'login' # The route function name for the login page
login_manager.login_message_category = 'info' # Optional: category for flashed messages

from flask import request # Added request

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data) # Use the model's method
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data): # Use the model's method
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/create_startup', methods=['GET', 'POST'])
@login_required
def create_startup():
    if current_user.role != 'entrepreneur':
        flash('Only entrepreneurs can create startups.', 'danger')
        return redirect(url_for('index'))
    
    form = StartupForm()
    if form.validate_on_submit():
        startup = Startup(name=form.name.data,
                          description=form.description.data,
                          funding_goal=form.funding_goal.data,
                          owner=current_user) # Associates with the current_user
        db.session.add(startup)
        db.session.commit()
        flash('Your startup has been created!', 'success')
        return redirect(url_for('index')) # Redirect to index for now
        # Later, redirect to a page like 'startup_detail' or 'user_dashboard'
        # return redirect(url_for('startup_detail', startup_id=startup.id))
    
    return render_template('create_startup.html', title='Create Startup', form=form)

@app.route('/startups')
@login_required
def startup_list():
    startups = Startup.query.all()
    return render_template('startup_list.html', title='Browse Startups', startups=startups)

@app.route('/startup/<int:startup_id>')
@login_required
def startup_detail(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    return render_template('startup_detail.html', title=startup.name, startup=startup)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Ensure tables are created based on models.py
    app.run(debug=True)
