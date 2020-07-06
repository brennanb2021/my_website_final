from flask import Flask
import os
from flask_socketio import SocketIO, emit
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app) 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes
from app.CsrfDb import models
