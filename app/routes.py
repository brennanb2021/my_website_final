from flask import request, render_template, flash, redirect, url_for, session, make_response, send_from_directory
from app import app, db
from app.CsrfDb.forms import LoginForm, RegistrationForm, EditPasswordForm, EditAccountForm
from uuid import uuid4
from app.CsrfDb.models import User, Profile
import datetime
import re
import os

from app.newsScraper.mainAction import mainAction
import plotly.graph_objects as go
from plotly.offline import plot as plotlyOfflinePlot

from app.pairingApp.group import runPairer
from werkzeug.utils import secure_filename


'''
csrf database
'''
sessionTokens = {} #sessiontoken:user object
csrfTokens = {} #csrfToken:boolean
#cookie = when someone logs in --> cookie sticks around

#different urls that application implements
#v=decorators, modifies function that follows it. Creates association between URL and fxn.
@app.route('/', methods=['GET']) #GET?
@app.route('/index', methods=['GET']) 
def index():

    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if sessionID in sessionTokens: #valid session token -- user already logged in
        return redirect(url_for('view', id=sessionTokens[sessionID].id))

    
    token = uuid4()
    csrfTokens[str(token)] = True #give user a session token

    form = LoginForm()
    title="Sign in"
    return render_template('index.html', form=form, csrf=token, title=title)


@app.route('/register', methods=['GET'])
def register():
    # Attempts to register a email/password pair; 
    form = RegistrationForm()

    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if sessionID in sessionTokens: #valid session token -- user already logged in
        return redirect(url_for('view', id=sessionTokens[sessionID].id))
    
    token = uuid4()
    csrfTokens[str(token)] = True #give user a session token
    
    title="Register"
    return render_template('register.html', form=form, csrf=token, title=title)


@app.route('/register', methods=['POST'])
def registerPost():

    form = RegistrationForm()
    form1 = request.form

    #check session token
    token = form1.get('csrfToken')
    if not (token in csrfTokens): #if the issued token from the previous page is not in dict
        flash("Invalid Form Request", 'requestError') #they didn't go thru the website
        return redirect(url_for('register')) #begone
    del csrfTokens[token] #remove this token from the dict
    
    success = True
    if form1.get("email") != None: #if they are making a new account
        if User.query.filter_by(email=form1.get('email')).first() != None: #email taken
            success = False
            flash(u'Email taken. Please enter a different email.', 'emailError')
        if form1.get('email') == '':
            success = False
            flash(u'Please enter an email.', 'emailError')
        else:
            regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #if it isn't a valid email address
            if(not(re.search(regex,form1.get('email')))):
                flash('Invalid email address', 'emailError')
                success = False
        if form1.get('first_name') == '':
            success = False
            flash(u'Please enter a first name.', 'first_nameError')
        if form1.get('last_name') == '':
            success = False
            flash(u'Please enter a last name.', 'last_nameError')
        if form1.get('password') == '':
            success = False
            flash(u'Please enter a password.', 'passwordError')
        if form1.get('password2') == '':
            success = False
            flash(u'Please reenter your password.', 'password2Error')
        if success: #did enter everything
            if form1.get('password') != form1.get('password2'): #passwords don't match
                success = False
                flash(u'Passwords do not match.', 'password2Error')
    else:
        if form1.get('password') == '':
            success = False
            flash(u'Please enter a password.', 'passwordError')
        if form1.get('password2') == '':
            success = False
            flash(u'Please reenter your password.', 'password2Error')
        if success: #did enter everything
            if form1.get('password') != form1.get('password2'): #passwords don't match
                success = False
                flash(u'Passwords do not match.', 'password2Error')
    
    if success: #success, registering new user
        if form1.get("email") != None: #if they are making a new account
            user = User(email=form1.get('email'))
            db.session.add(user) #add to database
            user.set_password(form1.get('password'))
            profile = Profile(first_name=form1.get('first_name'), last_name=form1.get('last_name'), user_id=User.query.filter_by(email=form1.get('email')).first().get_id(), date=datetime.datetime.now().isoformat())
            db.session.add(profile)
            db.session.commit()
        else: #they came from view to change their password
            User.query.filter_by(id=sessionTokens[request.cookies.get("user")].id).first().set_password(form1.get('password')) #set hashed pwd
            db.session.commit()
        return redirect(url_for('index')) #success: get request to index page
    else:
        token = form1.get('csrfToken')
        token = uuid4()
        csrfTokens[str(token)] = True #give user a session token
        if request.cookies.get("user") in sessionTokens: #they came from profile page
            return redirect(url_for('index'))
        title="Register"
        return render_template('register.html', form=form, csrf=token, title=title) #back to register


@app.route('/view', methods=['GET'])
def view():
    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if not(checkUserLoggedIn(sessionID)):
        return redirect(url_for('index'))

    id = sessionTokens[sessionID].id #if they go to the url without inputting an id, set it to the id of the user currently logged in
    id = request.args.get("id")
    
    token = uuid4()
    csrfTokens[str(token)] = True #give user a session token

    formPwd = EditPasswordForm()
    formFnLn = EditAccountForm()

    profile = Profile.query.filter_by(user_id=id).first() #get the correct profile by inputting user id

    profile_page_is_logged_in = (profile.user_id == sessionTokens[sessionID].id)
    #^if the user looking at this person's profile page is currently logged in, let them logout from or delete their account.
    title="Profile Page"
    return render_template('view.html', title=title, logged_in=profile_page_is_logged_in, profile=profile, formPwd=formPwd, formFnLn=formFnLn, csrf=token)
    #user logged in: show profile page.


@app.route('/view', methods=['POST'])
def viewPost():
    
    form1 = request.form 
    #check session token
    token = form1.get('csrfToken')
    if not (token in csrfTokens): #if the issued token from the previous page is not in dict
        flash("Invalid Form Request", 'requestError') #they didn't go thru the website
        return redirect(url_for('index')) #begone
    del csrfTokens[token] #remove this token from the dict
    
    success = True
    if form1.get('email') == "": #no email entered
        success = False
        flash(u'Please enter an email', 'emailError')
    if form1.get('password') == "": #no password entered
        flash(u'Please enter a password', 'passwordError')
        success = False
    if success: #they entered an email and password - now check them
        if User.query.filter_by(email=form1.get('email')).first() == None: #email entered but not found
            success = False
            flash(u'User does not exist. If you are a new user, click the registration button above.', 'emailError')
        elif not User.query.filter_by(email=form1.get('email')).first().check_password(form1.get('password')): #email and password do not match
            flash(u'Incorrect password', 'passwordError')
            success = False
    if success: 
        user = User.query.filter_by(email=form1.get('email')).first()
        id = user.id
        resp = make_response(redirect(url_for('mainPage'))) #get view should send to main page
        sessionToken = str(uuid4())
        sessionTokens[sessionToken] = user #change current user
        resp.set_cookie('user', sessionToken) #set session token in a cookie
        return resp
    else:
        return redirect(url_for('index')) #failure

@app.route('/members', methods=['GET'])
def members(): #show all accounts currently registered

    if request.cookies.get("user") in sessionTokens: #a user is logged in
        users = User.query.all()
        display = []
        for user in users:
            profile = Profile.query.filter_by(user_id=user.id).first() #get the correct profile by inputting user id
            if profile != None:
                item = dict(first_name=profile.first_name, last_name=profile.last_name, email=user.email, id=user.get_id())
                display.append(item)

        user_currently_logged_in = sessionTokens[request.cookies.get("user")]
        title="Accounts Registered"
        return render_template('members.html', title=title, display=display, logged_in_id=user_currently_logged_in.id)
    
    flash("You are not logged in.", 'requestError')
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    form1 = request.form
    
    #check session token
    token = form1.get('csrfToken')
    if not (token in csrfTokens): #if the issued token from the previous page is not in dict
        flash("Invalid Form Request", 'requestError') #they didn't go thru the website
        return redirect(url_for('index'))
    del csrfTokens[token] #remove this token from the dict

    sessionID = request.cookies.get('user') #get the session token
    #means they hit logout btn
    if sessionID in sessionTokens:
        del sessionTokens[sessionID] #remove this user's session token from the dict

    return redirect(url_for('index'))

@app.route('/deleteProfile', methods=['POST']) #need to check security
def deleteProfile():
    form1 = request.form

    #check session token
    token = form1.get('csrfToken')
    if not (token in csrfTokens): #if the issued token from the previous page is not in dict
        flash("Invalid Form Request", 'requestError') #they didn't go thru the website
        return redirect(url_for('index'))
    del csrfTokens[token] #remove this token from the dict

    sessionID = request.cookies.get('user') #get the session token
    Profile.query.filter_by(user_id=sessionTokens[sessionID].id).delete()
    User.query.filter_by(id=sessionTokens[sessionID].id).delete()
    db.session.commit()

    if sessionID in sessionTokens:
        del sessionTokens[sessionID] #remove this user's session token from the dict (log them out)

    return redirect(url_for('index'))


@app.route('/changeAccountInformation', methods=['POST']) #need to check security
def changeAccountInformation():
    form1 = request.form 

    #check session token
    token = form1.get('csrfToken')
    if not (token in csrfTokens): #if the issued token from the previous page is not in dict
        flash("Invalid Form Request", 'requestError') #they didn't go thru the website
        return redirect(url_for('index'))
    del csrfTokens[token] #remove this token from the dict

    sessionID = request.cookies.get('user') #get the session token

    success = True
    if form1.get('first_name') == "": #no email entered
        success = False
        flash(u'Please enter an first name', 'firstNameError')
    if form1.get('last_name') == "": #no password entered
        flash(u'Please enter a last name', 'lastNameError')
        success = False
    if not(success):
        return redirect(url_for('view', id=sessionTokens[sessionID].id))
    Profile.query.filter_by(user_id=sessionTokens[sessionID].id).first().set_first_name(form1.get('first_name'))
    Profile.query.filter_by(user_id=sessionTokens[sessionID].id).first().set_last_name(form1.get('last_name'))
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/mainPage', methods=['GET'])
def mainPage():
    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if not(checkUserLoggedIn(sessionID)):
        return redirect(url_for('index'))

    id = sessionTokens[sessionID].id #get id of user logged in

    profile = Profile.query.filter_by(user_id=id).first() #get the correct profile by inputting user id

    profile_page_is_logged_in = (profile.user_id == sessionTokens[sessionID].id)
    #^if the user looking at this person's profile page is currently logged in, let them logout from or delete their account.
    title="Main Page"
    return render_template('mainPage.html', title=title, profile=profile)
    #user logged in: show profile page.


'''
News scraper
'''
@app.route('/newsScraper', methods=['GET'])
def newsScraperGet():
    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if not(checkUserLoggedIn(sessionID)):
        return redirect(url_for('index'))
    
    with open('./app/templates/scraperPage.html','w') as fCopy: #reset file
        fCopy.write("")
    with open('./app/newsScraper/htmlNonDynamic.html','r') as fCopy:
        with open('./app/templates/scraperPage.html','a') as f:
            f.write(fCopy.read())

    return render_template('scraperPage.html')

@app.route('/newsScraper', methods=['POST'])
def newsScraperPost():
    form1 = request.form
    
    typed1 = None
    typed2 = None
    source1 = None
    source2 = None
    keywords = form1.get('keywords')
    sources = []
    if form1.get('sources1') != "":
        sources.append(form1.get('sources1')) #get the sources from the html form
        source1 = form1.get('sources1')

    if form1.get('sources2') != "":
        sources.append(form1.get('sources2'))
        source2 = form1.get('sources2')

    if len(sources) == 0:
        flash("No sources chosen")
        return redirect('/') #begone
    
    if keywords == "":
        flash("No keywords entered")
        return redirect('/') #begone
    
    dictData = mainAction(keywords, sources)
    if dictData[0] == False:
        flash(dictData[1], "divideBy0")
        redirect(url_for('newsScraperGet'))

    source1Dict = None
    source2Dict = None

    if source1 != None:
        typed1 = dictData[0]["type"] #articles or headlines
        source1Dict = dictData[0] #source 1 is something
    
    if source2 != None:
        if source1 == None: #user entered only the second source
            typed2 = dictData[0]["type"] #articles or headlines
            source2Dict = dictData[0] #source 2 is something and no source 1
        else:
            if source1 == source2: # the user put the same source for both
                typed2 = typed1
                source2Dict = source1Dict
            else:
                typed2 = dictData[1]["type"] #source 1 and source 2 are different, set them to dictData[0] and [1]
                source2Dict = dictData[1]
    
    keywordStr = ""
    keywords = keywords.split(", ")
    for keyword in keywords:
        keywordStr+=keyword + ", " #keywordstr to display on the website
    
    keywordStr = keywordStr[:len(keywordStr)-2]

    
    dataGraph = {}
    if source1 != None:
        dataGraphDict1 = {}
        for i in list(source1Dict.keys()):
            if " " in i:
                dataGraphDict1[i] = source1Dict[i] #add source1 to dataGraph dictionary
        dataGraph["source1Name"] = source1
        dataGraph["labels1"] = list(dataGraphDict1.keys())
        dataGraph["source1Vals"] = list(dataGraphDict1.values()) #turn key/value dictionaries into separate lists and add to dict
        
    if source2 != None:
        dataGraphDict2 = {}
        for i in list(source2Dict.keys()):
            if " " in i:
                dataGraphDict2[i] = source2Dict[i] #add source2 to dict
        dataGraph["source2Vals"] = list(dataGraphDict2.values())
        dataGraph["source2Name"] = source2
        dataGraph["labels2"] = list(dataGraphDict2.keys())


    with open('./app/templates/scraperPage.html','w') as fCopy: #reset file
        fCopy.write("")
    
    #Open the scraperPage.html in templates and append the images of the plots to it (get the text, edit the text, and return the text.)
    with open('./app/newsScraper/htmlNonDynamic.html','r') as f:
        addThisHtml = f.read()
    
    div = plotGraph(dataGraph, keywordStr) #plot graph with plotly
    addThisHtml = addThisHtml.replace('-Add graph here-', div)

    with open('./app/templates/scraperPage.html','a') as f:
        f.write(addThisHtml)
    
    return render_template('scraperPage.html', source1=source1, source2=source2, keywords=keywordStr, keywordArr=keywords,
            finishedReading=True, source1Dict=source1Dict, source2Dict=source2Dict, typed1=typed1, typed2=typed2)

def plotGraph(dataGraph, keywordStr):
    data = []
    if dataGraph.__contains__("source1Name"):
        bar1 = go.Bar(name=dataGraph["source1Name"], x=dataGraph["labels1"], y=dataGraph["source1Vals"]) #add bars if they exist
        data.append(bar1)
        layout = go.Layout(barmode='group', title=("Polarity of " + dataGraph["source1Name"]), yaxis_title="%")
    if dataGraph.__contains__("source2Name"):
        bar2 = go.Bar(name=dataGraph["source2Name"], x=dataGraph["labels2"], y=dataGraph["source2Vals"])
        data.append(bar2)
        layout = go.Layout(barmode='group', title=("Polarity of " + dataGraph["source2Name"]), yaxis_title="%")
    
    # Change the bar mode and set layout
    if dataGraph.__contains__("source1Name") and dataGraph.__contains__("source2Name"):
        layout = go.Layout(barmode='group', title=("Polarity of " + dataGraph["source1Name"] + " vs " + dataGraph["source2Name"]), yaxis_title="%")
    
    div = plotlyOfflinePlot({"data":data, "layout":layout}, include_plotlyjs=False, output_type='div')
    return div
    #fig = go.Figure(data=data, layout=layout)
    #fig.show() #open in new tab

'''
grouping app
'''
@app.route('/pair', methods=['GET'])
def pairGet():
    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if not(checkUserLoggedIn(sessionID)):
        return redirect(url_for('index'))

    with open('./app/templates/pair.html','w') as fCopy: #reset file
        fCopy.write("")
    with open('./app/pairingApp/pairhtmlcopyNonDynamic.html','r') as fCopy:
        with open('./app/templates/pair.html','a') as f:
            f.write(fCopy.read())

    return render_template('pair.html')

@app.route('/pair', methods=['POST'])
def pairPost():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', "file error")
        return redirect(request.url)
    fileGet = request.files['file']
    if fileGet != "":
        fileGet = request.files['file']
    else:
        flash("No file selected", "file error")
        return redirect(url_for('pair'))
    
    with open('./app/templates/pair.html','w') as fCopy: #reset file
        fCopy.write("")
    with open('./app/pairingApp/pairhtmlcopyNonDynamic.html','r') as fCopy:
        with open('./app/templates/pair.html','a') as f:
            f.write(fCopy.read())
    
    list1 = runPairer(fileGet)
    everybodyConnections = list1[0]
    withPreferencesConnections = list1[1]
    
    return render_template('pair.html', everybodyConnections=everybodyConnections, withPreferencesConnections=withPreferencesConnections)
    

'''
Bullet Hell game
'''
@app.route('/bulletHell', methods=['GET'])
def runBulletHellGame():
    sessionID = request.cookies.get("user") #get the session token from the previous page cookies
    if not(checkUserLoggedIn(sessionID)):
        return redirect(url_for('index'))
    return render_template('bulletHellGame.html')

def checkUserLoggedIn(sessionID):
    
    #Checks if the user is actually logged in -- commented out for easier testing
    if not (sessionID in sessionTokens): #not a valid session token
        flash("You are not logged in.", 'requestError')
        return False
    

    return True