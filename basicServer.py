from app import app
#from app.models import User
from flask import Flask
import os
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes
from app.CsrfDb import models


if __name__ == '__main__': #on flask run include: -p 5372 after to run it on port 5372.
    app.run(port=33507)
    #if run w/ basicServer.py instead of flask run