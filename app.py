import os
import json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from functions import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DEBUG"] = True
app.secret_key = os.urandom(24)
Session(app)

db = SQL("sqlite:///beet.db")

@app.route("/", methods=['GET', 'POST']) # HOMEPAGE (AFTER USER LOGS IN)
@login_required
def index():
    
    if request.method == 'POST':
        return render_template("layout.html")
    
    else:
        return render_template("layout.html")
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Log user in"""

    if 'user_id' in session: # if user logged in, redirect the to homepage
        return redirect(url_for('index'))

    if request.method == 'POST': # user has tried to login

        if not request.form.get('username'): # if user hasn't entered username
            flash('Username if required', 'error')
            return render_template('login.html')
        
        elif not request.form.get('password'): # if user hasn't entered password
            flash('Password is required', 'error')
            return render_template('login.html')
        
        # get user data from users table
        userDb = db.execute('SELECT * FROM users WHERE username=?', request.form.get('username'))

        # check if password matches hash
        if len(userDb) != 1 or not check_password_hash(userDb[0]['hash'], request.form.get('password')):
            flash('Username or Password Incorrect', 'error')
            return render_template('login.html')
        
        session['user_id'] = userDb[0]['id']
        
        return redirect("/")

    else:   # GET request
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log the user out when logout pressed"""

    session.clear()
    flash('You have successfully been logged out', 'info')
    return redirect(url_for('login'))
    
    
@app.route("/register", methods=['GET', 'POST'])
def register():

    if request.method == 'POST': # user registers an account

        userReg = request.form.get('username')

        if not userReg: # force user to enter value
            flash('Username is required', 'error')
            return render_template('register.html')
        
        passReg = request.form.get('password')
        
        if not passReg or passReg != request.form.get('confirmation'):
            flash('Password Required / Passwords do not match', 'error')
            return render_template('register.html')
        
        userDb = db.execute('SELECT username FROM users WHERE username=?', userReg)

        if userDb:
            if userDb[0]['username'] == userReg:
                flash('Username Already Taken', 'error')
                return render_template('register.html')
            
        db.execute('INSERT INTO users (username, hash) VALUES(?,?)', userReg, generate_password_hash(passReg, method='pbkdf2', salt_length=16))

        flash('Successfully Registered!', 'success')

        return redirect(url_for('login')) # redirect user to SURVEY??? ############# FIX THIS #####################
    
    else:
        return render_template("register.html")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    return render_template('account.html')


@app.route("/account/survey", methods=['GET', 'POST'])
@login_required
def survey():
    # create list of dietary requirements to send to html through jinja
    dietary_requirements = [
        'Vegetarian',
        'Vegan',
        'Pescatarian',
        'Gluten-Free',
        'Dairy-Free',
        'Nut-Free',
        'Egg-Free',
        'Keto',
        'Paleo'
    ]

    cuisines = [
        'Italian',
        'Mexican',
        'Chinese',
        'Indian',
        'Japanese',
        'Greek',
        'Lebanese',
        'Vietnamese',
        'Turkish',
        'Korean',
        'Middle Eastern',
        'American',
        'Australian',
        'Moroccan',
        'Spanish',
        'Caribbean',
        'Mediterranean'
    ]

    if request.method == 'POST': # user completes the survey - save data to DB

        # get survey form data from user input
        selectedDietary = request.form.getlist('dietaryChoices')
        selectedCuisines = request.form.getlist('cuisineChoices')
        selectedServings = int(request.form.get('servings'))

        # validate HTML form 'values=""' have not been tampered with
        for item in selectedDietary:
            if item not in dietary_requirements:
                flash("Invalid Form Response", 'error')
                return redirect(url_for('survey'))
            
        for item in selectedCuisines:
            if item not in cuisines:
                flash('Invalid Form Response', 'error')
                return redirect(url_for('survey'))
            
        if selectedServings < 2 or selectedServings > 8:
            flash('Invalid Form Response', 'error')
            return redirect(url_for('survey'))

        # convert lists to JSON for SQL storage
        selectedDietary_json = json.dumps(selectedDietary)
        selectedCuisines_json = json.dumps(selectedCuisines)

        # if user has not selected at least one option from each question
        if not selectedCuisines or not selectedDietary or not selectedServings:
            flash('Please list at least one option for each question', 'error')
            return render_template('survey.html', dietary_requirements=dietary_requirements, cuisines=cuisines)
        
        # find user survey record
        userSurveyData = db.execute('SELECT * FROM survey WHERE userid=?', session['user_id'])

        # if record is empty, INSERT data into table
        if not userSurveyData:
            db.execute('INSERT INTO survey (cuisine, dietary, servings, userid) VALUES (?,?,?,?)', 
                       selectedCuisines_json, selectedDietary_json, selectedServings, session['user_id'])

        else:
            db.execute('UPDATE survey SET cuisine=?, dietary=?, servings=? WHERE userid=?', 
                       selectedCuisines_json, selectedDietary_json, selectedServings, session['user_id'])

        flash('New survey information recorded', 'info')
        return redirect(url_for('survey'))
    
    else:
        return render_template("survey.html", dietary_requirements=dietary_requirements, cuisines=cuisines)
    

@app.route("/generate", methods=['GET', 'POST'])
@login_required
def generate():

    if request.method == 'POST':
        return redirect(url_for('generate'))
    
    else:
        return render_template('generate.html')
        