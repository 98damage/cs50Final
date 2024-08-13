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

    session.clear() # forget user_id 

    if request.method == 'POST': # user has tried to login
        return redirect("/")

    else:   # GET request
        return render_template("login.html")
    
    
@app.route("/register", methods=['GET', 'POST'])
def register():

    if request.method == 'POST': # user registers an account

        userReg = request.form.get('username')

        if not userReg: # force user to enter value
            flash('Username is required', 'error')
            return redirect(url_for('register'))
        
        passReg = request.form.get('password')
        
        if not passReg or passReg != request.form.get('confirmation'):
            flash('Password Required / Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        userDb = db.execute('SELECT username FROM users WHERE username=?', userReg)

        if userDb:
            if userDb[0]['username'] == userReg:
                flash('Username Already Taken', 'error')
                return redirect(url_for('register'))
            
        db.execute('INSERT INTO users (username, hash) VALUES(?,?)', userReg, generate_password_hash(passReg, method='pbkdf2', salt_length=16))

        userid = db.execute('SELECT id FROM users WHERE username=?', userReg)
        session['id'] = userid[0]['id']

        return redirect(url_for('survey')) # redirect user to SURVEY??? ############# FIX THIS #####################
    
    else:
        return render_template("register.html")


@app.route("/survey", methods=['GET', 'POST'])
@login_required
def survey():

    if request.method == 'POST': # user completes the survey

        return redirect("/")
    
    else:
        return render_template("survey.html")