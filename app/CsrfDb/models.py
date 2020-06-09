from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model): #inherits from db.Model, base for flask-SQLAlchemy
    
    id = db.Column(db.Integer, primary_key=True) #id = primary key
    email = db.Column(db.String(64), index=True, unique=True) #defined as strings, max length = ().
    password_hash = db.Column(db.String(128)) #not storing plaintext pwd, hashing first.

    def __repr__(self):
        return '<User {}>'.format(self.email) #how to print database

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) #<^=pwd hashing logic

class Profile(UserMixin, db.Model):

    def __repr__(self):
        return '<Profile {}>'.format(self.first_name + " " + self.last_name) #how to print database
    
    def set_id(self, user_id):
        self.user_id = user_id
    
    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(64))
