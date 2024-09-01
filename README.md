# BEET Recipe Generation

#### Video Demo: [<URL HERE>](https://www.youtube.com/watch?v=go4B81hnJd8)

## Description:

### Project Overview:

Beet is a webapp that simplifies and optimises meal planning and cooking.
Users are asked to fill out a survey which includes dietary information about themselves and the people they live with.
The program retrieves this survey information from the users which then feeds into the OpenAI API, the user is presented with a range of options for their meals for the week that are suited to their requirements. The user can select out of a list of recipes what they want to cook for the week. The program then displays the 7 recipes the user has chosen which the users can then click into each recipe to view
the method and ingredients.

User authentication has been implemented, users can register for accounts, login and logout. Users can change their survey data anytime and generate new recipes anytime.

### App.py:

The file which handles the backend is _app.py_, written in python. Within this there are 8 @app.route decorators which each contain a sub function to handle GET and POST requests. There are four additional functions which are called upon within the app routes.

#### app.route("/plan"):

This function checks whether recipe methods have been generated or not, if not, the function will return a flashed error message and redirect the user to the /generate page to select their recipes for the week. If recipe methods & ingredients list have been selected, then they will be displayed in cards on the screen, where the user can then view each recipe individually to see the method and ingredients list, which redirects them to the next route.

#### app.route("/plan/recipe/int:recipe_id"):

This function checks if the recipe that the user has chosen exists, or rather is 'owned' by that user in the SQL DB. If true, the method and ingredients list are displayed on this page.

#### app.route("/login"):

This page lets the user log in. It takes a username and a password which is tested against the user table in beet.db. Werkzeug.security is used for all password hashing. Error messages are displayed if username or passwords are incorrect or if the user has entered neither of them. Once logged in the a session id is created for that specific user, this can later be called by session['user_id']. Once the user is logged in it will redirect them to thier weekly plan page. Most routes in the program come under the @login_required decorator.

#### app.route("/logout"):

The session data is cleared which logs the user out. The user is then redirected to the login page.

#### app.route("/register"):

This function allows the user to register for an account. Users must enter data into all fields otherwise an error will result. If the username is taken or the two password fields don't match then an error will result. If it's successful then the user will be redirected to the login page.

#### app.route("/account"):

The account page lists a link (button) to the survey page. There were future development ideas for this page that fell out of the scope of the project. I would've liked to implement the ability for users to update/change thier usernames and passwords. If this was a commercial product I'd like this page to also display different payment plans allowing users to generate more/less recipes based on the pricing of their plan.

#### app.route("/account/survey"):

This page lets the user select their options for their dietary, cuisine and serving amount requirements. This function has protection against HTML form manipulation through the dev options on the page. If a user were to change the names of any of the dietary requirements of cuisines or the serving amount then an invalid error will be displayed. If successful then the survey DB is updated with the new information. Since the dietary and cuisine information is pulled from the HTML as a list, it had to be converted to json for insertion into the DB.

#### app.route("/generate"):

The largest function, which I know should've been broken down into more helper functions for ease of reading/debugging. A good learning for future projects.

In the user table there are two boolean columns called 'titles_generated' and 'methods_generated' which I will reference as TG and MG from now on. If TG and MG were both 0, then the user had not generated recipe titles nor recipe methods/ingredients. Therefore when the user presses the generate recipes button on the /generate page the function generate_recipe_titles is called which takes the users survey data as an input, within this an API call is made using the openAI API. 14 unqiue recipe titles are returned in JSON which are then inserted into the recipes table. If no errors are thrown then the generate.html template is rendered with this recipe title data.

The 14 recipes are then displayed where the user can select up to 7 recipes. The script /static/buttonClick.js is implemented on this page, this script limits the user from selecting more than 7 recipes. Once 7 recipes are selected the user can click the 'Add recipes to weekly plan' button, which then performs another call to the OpenAI API, this function takes the users survey data as well as titles of each recipe generated for that user. It outputs the methods and ingredients for that recipe which can then be stored within the added_recipes table. The recipe titles within the table recipes are then deleted.

#### select_recipes(recipe_id):

This function is called under the generate function in the /generate route, it takes an input recipe_id. The recipe id's are passed from the generate.html page, where the user is selecting 7 of the 14 recipes that they want to cook for the week. If the recipe_id's match an entry in the recipes table, that recipe is appended to recipe_list. The function returns the list 'recipe_list'.

#### generate_recipe_titles(survey_userData):

This function takes the survey data as an input. It has the prompt for the OpenAI API as a variable of type string. The string has f strings in some of the lines which reference the survey data. JSON.loads is used on the dietary and cuisine data as it's pulled out of the DB.

A try except is employed to throw an exception if the API call fails. The function call_openai_api is called which takes the prompt as the input. If the API call is successful the data is pulled out of the message, the TG and MG values within the users table is updates and the function returns 'recipes', a list of dictionaries containing each recipe title and the associated data. If the exception is thrown, None is returned.

#### generate_recipe_methods(recipes_input, survey_userData):

This function works similarly to the above. It does take the titles of the recipes chosen by the user as input as well as the survey data. The prompt is different as we want OpenAI to return methods and ingredients for each recipe. The try and except call is similar to as above.

#### call_openai_api(prompt):

This function runs the API call. The code for this was implemented using the OpenAI API documentation.

## Templates Folder:

#### layout.html:

Layout.html is the foundation of the frontend. It references Bootstrap JS and CSS classes. Every other .html file extends this file using jinja. This file places a navbar on every page in the webapp. The user can select to navigate to their weekly plan, generate recipes and they can, login, logout and check their account settings using links and buttons on the navbar. The body tags handle flashed messages and the main tags handle the other html files which extend layout.html.

The code on lines 45 to 55 were also referencd from the PSET9/finance of the CS50 course.

#### account.html:

This file shows the user the account settings. From here the user can redirect to the survey page.

#### generate.html:

This page displays one of two options. The first option displays the 14 recipes in Bootstrap cards that the user has previosuly generated, which are there for them to select 7 for later use. This is executed if the TG column against the users account in the users table is 1 (True).

If the titles haven't been generated and TG is 0 in the users table, then 4 images of various meals are displayed and a button to generate recipes appears underath the images.

#### login.html:

The login page displays input tags asking the user to enter their username and password, with a submit button at the bottom of the form. There is also a hyperlink which takes a user to the register page.

#### register.html:

The register page is similar to the login page. Three input tags are used and the user is asked to enter a username, their password, and their password again to confirm there's no discrepancies between the two. A hyperlink is available on the page to take the user to the login page.

#### survey.html:

The survey page displays the different dietary and cuisine options for the user to select, they are selectable/unselectable through checkboxes. The serving amount is selectable with a slider that changes from the value 2 through 8. There is a submit button at the bottom of the form, when the data is submitted backend checks are conducted in app.py to ensure tampering with the HTML hasn't occurred.

#### weeklyPlan.html:

The weeklyPlan.html page displays the 7 recipes that the user selected from the generate.html page. From here the user can choose to view one of the 7 recipes in more detail, showing the method and ingredients for that recipe in the viewRecipe.html page. If recipes haven't been selected from the generate screen, or recipe titles haven't been generated, all attempts to open the weeklyPlan.html will result in redirects to the /generate route and generate.html.

#### viewRecipe.html:

This page displays the method and ingredients list for the recipe that the user chooses to view from the weeklyPlan.html page. The page is dynamically generated with a for loop where data such as the title, method and ingredients are fed through from app.py.

## Static Folder:

#### buttonClick.js:

This script contains the code which dynamically updates the button response on the generate screen, this is after the user has generated 14 recipe titles and is prompted to choose 7 to generate methods and ingredients lists for. The script has an event listener which checks when a button is clicked under each of the 14 recipes, buttons can be selected and deselected. When 7 buttons have been toggled, all other recipe buttons will grey out and become unclickable and the large submit button at the top of the screen will be able to be clicked.

#### styles.css:

The CSS file contains 11 classes. These were used throughout the frontend design of the project. The alert.xxx classes were used for message flashing.

#### Photos:

Four photos were displayed on the generate.html page. These sit above the generate button and are purely aesthetic.

## Other Files:

#### SQL beet.db:

For the project I implemented the use of sqlite3. I used the SQL imported from the CS50 library in app.py.

The database contains four tables: users, survey, recipes, added_recipes. The users table contains an id, the username, the password hash and two BOOLEAN columns: titles_generated and methods_generated which are used for backend checks as talked about above.

The survey table contains and id, cuisine, dietary, servings and a userid column. When the user enters their inputs on the /account/survey page, the data is stored in this table.

The recipes table is used as a temporary table to store the id, title, meal_type, cuisine and user_id. The data that is stored in this table is the data that is generated when the openAI call is generating the first 14 recipe titles for the user. Once the user selects 7 recipes and chooses to generate the methods and ingredients list for them the 14 recipes and their associated data are deleted from the recipes table based on the users id.

The added_recipes table stores the recipes which have had the method and ingredients list generated. The table stores an id, title, meal_type, cuisine, method, ingredients, favourite and user_id. If the user generates 14 more recipes to choose for their week, this data is wiped from the table. The favourite column is a feature that was meant to be implemented but is now out of scope.

**Below is the DB schema:**

```
sqlite> .tables

added_recipes recipes survey users

sqlite> .schema

CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
username TEXT NOT NULL,
hash TEXT NOT NULL,
titles_generated BOOLEAN DEFAULT FALSE,
methods_generated BOOLEAN DEFAULT FALSE);
CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX username ON users(username);

CREATE TABLE survey (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
cuisine TEXT NOT NULL,
dietary TEXT NOT NULL,
servings INTEGER NOT NULL,
userid INTEGER NOT NULL);

CREATE TABLE recipes (id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
meal_type TEXT,
user_id INTEGER,
cuisine TEXT,
FOREIGN KEY (user_id) REFERENCES users(id));

CREATE TABLE added_recipes (id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
meal_type TEXT,
cuisine TEXT,
method TEXT,
ingredients TEXT,
favourite BOOLEAN DEFAULT 0,
user_id INTEGER,
FOREIGN KEY (user_id) REFERENCES users(id));
```

#### functions.py:

This file contains the decorated function **login_required** which is used to ensure that only some pages can be viewed if the user is logged in. This function is taken from CS50.dev, specifically taken from PSET9/finance/helpers.py.

#### .env:

This file was brought in to hold my OpenAI API key. I then used .gitignore and stored .env in the file so that it would be uploaded to the public repository. I was having errors early on as github was not allowing me to push my work to the repository with the API key in app.py. So I preserved the security of my private API key and have kept it off of my github repository.
