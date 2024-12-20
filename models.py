from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pytz

db = SQLAlchemy()

class UploadSession(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata'))) 
    filename = db.Column(db.String(255), nullable=False) 
    parameters = db.relationship('Parameter', backref='session', lazy=True, cascade="all, delete")

class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('upload_session.id'), nullable=False)
    parameter_name = db.Column(db.String(255), nullable=False)
    parameter_value = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Parameter {self.parameter_name}>'
