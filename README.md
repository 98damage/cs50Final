# BEET Recipe Generation

#### Video Demo: <URL HERE>

## Description:

### Project Overview:

Beet is a webapp that simplifies and optimises meal planning and cooking.
Users are asked to fill out a survey which includes dietary information about themselves and the people they live with.
The program retrieves this survey information from the users which then feeds into the OpenAI API, the user is presented with a range of options for their meals for the week that are suited to their requirements. The user can select out of a list of recipes what they want to cook for the week. The program then displayes the 7 reecipes the user has chosen which the users can then click into each recipe to view
the method and ingredients.

User auth has been implemented, users can register for accounts, login and logout. Users can change their survey data anytime and generate new recipes anytime.

### App.py:

The file which handles the backend is _app.py_, written in python. Within this there are 8 @app.route decorators which each contain a sub function to handle GET and POST requests. There are four additional functions which are called upon within the app routes.

#### app.route("/plan"):

This function checks whether recipe methods have been generated or not

#### app.route("/plan/recipe/int:recipe_id"):

#### app.route("/login"):

#### app.route("/logout"):

#### app.route("/register"):

#### app.route("/account"):

#### app.route("/account/survey"):

#### app.route("/generate"):

#### select_recipes(recipe_id):

#### generate_recipe_titles(survey_userData):

#### generate_recipe_methods(recipes_input, survey_userData):

#### call_openai_api(prompt):

## Templates Folder:

#### account.html:

#### generate.html:

#### index.html:

#### layout.html:

#### login.html:

#### register.html:

#### survey.html:

#### viewRecipe.html:

#### weeklyPlan.html:

## Static Folder:

#### buttonClick.js:

#### styles.css:

#### Photos:

## Other Files:

#### SQL beet.db:

#### functions.py:

#### .env:
