import os
import json
from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from functions import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DEBUG"] = True
app.secret_key = os.urandom(24)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
Session(app)

db = SQL("sqlite:///beet.db")


@app.route("/", methods=['GET'])
@login_required
def weekly_plan():
    """Weekly Plan Once Logged In"""

    methods_generated = db.execute('SELECT methods_generated FROM users WHERE id=?', session['user_id'])

    if not methods_generated[0]['methods_generated']:
        flash("No Recipes Currently Available, Please Generate/Select Recipes", "error")
        return redirect(url_for('generate'))

    weeklyRecipeCards = db.execute('SELECT id, title, meal_type, cuisine FROM added_recipes WHERE user_id=?', 
                               session['user_id'])
        
    return render_template("weeklyPlan.html", weeklyRecipeCards=weeklyRecipeCards)
    

@app.route("/recipe/<int:recipe_id>", methods=['GET'])
@login_required
def view_recipe(recipe_id):

    recipe = db.execute('SELECT title, meal_type, cuisine, method, ingredients FROM added_recipes WHERE id=? AND user_id=?', 
                        recipe_id, session['user_id'])
    
    if not recipe:
        flash("Recipe doesn't exist", "error")
        return redirect(url_for('weekly_plan'))
    else:
        recipe = recipe[0] # simplify keystrokes
    
    # deserialise ingredients and method from SQL storage
    recipe['ingredients'] = json.loads(recipe['ingredients'])
    recipe['method'] = json.loads(recipe['method'])

    return render_template("viewRecipe.html", recipe=recipe)


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
        
        return redirect(url_for('generate'))

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
    """User registers for an account"""
    # does not handle for list injection into SQL DB which would result in error

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

        return redirect(url_for('login'))
    
    else:
        return render_template("register.html")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """Lists user account options"""

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
    # code to display user recipe titles if they exist
    userDb_data = db.execute('SELECT titles_generated, methods_generated FROM users WHERE id=?', session['user_id'])

    if request.method == 'POST':
        survey_userData = db.execute('SELECT * FROM survey WHERE userid=?', session['user_id'])
        if not survey_userData:
            flash("Please complete the survey under /account/survey", "error")
            return redirect(url_for('generate'))
        
        # get method & ingredients lists for user
        if userDb_data[0]['titles_generated']:
            selected_recipe_id = json.loads(request.form.get('selected-recipes')) # convert string to list

            recipe_list = select_recipes(selected_recipe_id)
            recipe_methods = generate_recipe_methods(recipe_list, survey_userData)

            # in the off chance the api doesn't work and recipe_methods returns error of NoneType
            while recipe_methods is None or len(recipe_methods) == 0:
                recipe_methods = generate_recipe_methods(recipe_list, survey_userData)

            for recipe in recipe_methods:
                method_json = json.dumps(recipe['method']) # convert lists to JSON fields for SQL DB
                ingredients_json = json.dumps(recipe['ingredients'])
                db.execute('INSERT INTO added_recipes (title, meal_type, cuisine, method, ingredients, user_id) VALUES (?,?,?,?,?,?)', 
                        recipe['title'], recipe['meal_type'], recipe['cuisine'], method_json, ingredients_json, session['user_id'])
                print(recipe['title'])

            # delete data from recipes table once methods/ingredients have been chosen
            db.execute('DELETE FROM recipes WHERE user_id=?', session['user_id'])

            # display users weekly recipe plan
            return redirect("/") 

        # user has selected their 7 recipes for the week, redirect to weekly plan
        if userDb_data[0]['methods_generated']:
            db.execute('UPDATE users SET methods_generated=?', False)
            db.execute('DELETE FROM added_recipes WHERE user_id=?', session['user_id'])
        
        # if titles haven't been generated and the methods haven't been generated (both FALSE), generate 14 recipes
        if not userDb_data[0]['titles_generated'] and not userDb_data[0]['methods_generated']:

            recipes = generate_recipe_titles(survey_userData)
            
            if recipes:
                # load individual recipes into recipes database
                for recipe in recipes:
                    db.execute('INSERT INTO recipes (title, meal_type, cuisine, user_id) VALUES(?,?,?,?)', 
                            recipe['title'], recipe['meal_type'], recipe['cuisine'], session['user_id'])
                
                # update users DB so that we know they have generated 14 recipes previously
                userDb_data = db.execute('SELECT titles_generated, methods_generated FROM users WHERE id=?', session['user_id'])
                recipes_db = db.execute('SELECT id, title, cuisine, meal_type FROM recipes WHERE user_id=?', session['user_id'])
                return render_template('generate.html', recipes_db=recipes_db, userDb_data=userDb_data)
            else:
                flash("Error generating recipes, try again", "error")
                return redirect(url_for('generate'))

        return render_template('generate.html', userDb_data=userDb_data)
    
    else:
        userDb_data = db.execute('SELECT titles_generated, methods_generated FROM users WHERE id=?', session['user_id'])
        recipes_db = db.execute('SELECT id, title, cuisine, meal_type FROM recipes WHERE user_id=?', session['user_id'])
        return render_template('generate.html', userDb_data=userDb_data, recipes_db=recipes_db)
        

def select_recipes(recipe_id): # Parse selected recipe ids to DB to get title, meal_type & cuisine data for method generation function
    #print(selected_recipe_id)
    recipe_list = []

    for id in recipe_id:
        #print(id)
        recipe = db.execute('SELECT title, meal_type, cuisine FROM recipes WHERE user_id=? AND id=?', session['user_id'], id)
        if recipe:
            recipe_list.append(recipe[0])

    return recipe_list


def generate_recipe_titles(survey_userData):
    title_prompt_input = (
        "Generate 14 unique recipe titles that adhere to the following criteria:\n\n"
        f"The recipes should match the following dietary requirements: {json.loads(survey_userData[0]['dietary'])}.\n"
        f"The recipes should be based on the following cuisine(s): {json.loads(survey_userData[0]['cuisine'])}.\n"
        f"Each recipe should be designed to serve {survey_userData[0]['servings']} people.\n"
        "For each recipe, indicate whether it is best suited for breakfast, lunch, or dinner.\n"
        "Please return only the JSON array of objects and not even the quotation marks at the start or end of the output where each object contains three fields: "
        "'title' (the recipe title), 'cuisine' (the meals cuisine) and 'meal_type' (the corresponding meal type: breakfast, lunch, or dinner), and nothing else."
        )

    # send openai API request & store the content as json within recipes variable
    try:
        api_response = call_openai_api(title_prompt_input)
        recipes = json.loads(api_response['choices'][0]['message']['content'])
        db.execute('UPDATE users SET titles_generated=?, methods_generated=? WHERE id=?', True, False, session['user_id'])
        return recipes
    except Exception as e:
        flash("Error generating recipes. Please try again", "error")
        db.execute('UPDATE users SET titles_generated=?, methods_generated=? WHERE id=?', False, False, session['user_id'])
        return None


def generate_recipe_methods(recipes_input, survey_userData):

    method_prompt_input = (
        "Generate detailed recipes for the following 7 unique recipe titles. Each recipe should include a method and a list of ingredients, adhering to the following criteria:\n\n"
        f"List of dictionaries including recipe titles and the associated meal types & cuisine of that recipe: {recipes_input}\n"
        f"Dietary Requirements: The recipes should match the following dietary requirements: {json.loads(survey_userData[0]['dietary'])}.\n"
        f"Servings: Each recipe should be designed to serve {survey_userData[0]['servings']} people.\n"
        "Meal Types: Each recipe should indicate whether it is best suited for breakfast, lunch, or dinner.\n"
        "For each recipe, return a JSON array of objects where each object contains the following fields:\n"
        "title (the recipe title),\n"
        "cuisine (the cuisine of the meal),\n"
        "meal_type (whether the recipe is best suited for breakfast, lunch, or dinner),\n"
        "ingredients (a list of ingredients needed for the recipe, with quantities specified),\n"
        "method (a step-by-step method to prepare the recipe with australian SI system (celsius etc)).\n"
        "Please ensure the output is formatted as a JSON array of objects and do not include any extraneous text outside of the JSON structure.\n"
        "Do not even include the quotation marks or the text 'json' at the start or end of the output"
    )

    try:
        api_response = call_openai_api(method_prompt_input)
        recipes = json.loads(api_response['choices'][0]['message']['content'])
        db.execute('UPDATE users SET titles_generated=?, methods_generated=? WHERE id=?', False, True, session['user_id'])
        return recipes
    except Exception as e:
        flash("Error generating recipes. Please try again", "error")
        db.execute('UPDATE users SET titles_generated=?, methods_generated=? WHERE id=?', True, False, session['user_id'])
        return None


def call_openai_api(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        flash('OpenAI API Error', 'error')
        return {"error": f"Request failed with status code {response.status_code}"}