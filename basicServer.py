from app import app
from flask_socketio import SocketIO, emit 
#from app.models import User

if __name__ == '__main__': #on flask run include: -p 5372 after to run it on port 5372.
    socketio.run(app, debug=True)
    #if run w/ basicServer.py instead of flask run