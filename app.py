import os

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
        print(session)

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

    if request.method == 'POST': # user completes the survey

        return redirect("/")
    
    else:
        return render_template("survey.html")