from app import app
#from app.models import User

if __name__ == '__main__': #on flask run include: -p 5372 after to run it on port 5372.
    app.run(port=33507)
    #if run w/ basicServer.py instead of flask run