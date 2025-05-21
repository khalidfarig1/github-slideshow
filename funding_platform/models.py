from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for stronger hashes
    role = db.Column(db.String(20), nullable=False)  # 'entrepreneur' or 'investor'
    
    startups = db.relationship('Startup', backref='owner', lazy=True)
    # investments relationship will be added later when Investment model is created
    # investments = db.relationship('Investment', backref='investor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Startup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    funding_goal = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    funding_rounds = db.relationship('FundingRound', backref='startup', lazy=True)
    # investments relationship will be added later
    # investments = db.relationship('Investment', backref='startup_funded', lazy=True)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Startup {self.name}>'

class FundingRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    round_name = db.Column(db.String(50), nullable=False)  # e.g., 'Seed', 'Series A'
    amount_raised = db.Column(db.Float, default=0.0)
    details = db.Column(db.Text, nullable=True)
    date_opened = db.Column(db.DateTime, default=datetime.utcnow)
    date_closed = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<FundingRound {self.round_name} for Startup {self.startup_id}>'

# Placeholder for Investment model, to be defined later
# class Investment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     amount = db.Column(db.Float, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
#     funding_round_id = db.Column(db.Integer, db.ForeignKey('funding_round.id'), nullable=True) # Optional, if investment is tied to a specific round
#     date_invested = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f'<Investment {self.amount} by User {self.user_id} in Startup {self.startup_id}>'
