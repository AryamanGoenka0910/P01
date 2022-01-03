'''
Mango: Aryaman Goenka, Sadid Ethun, Haotian Gan
Softdev
P00: ArRESTed Development
2021-12-12
'''
import re
import sqlite3
import db_builder
from flask import Flask, render_template, request, session, redirect, url_for
import json
import requests
import random
import recipes
import base64
import usda_api
app = Flask(__name__)
app.secret_key = 'Mango'


# Utility function to check if there is a session
def logged_in():
    return session.get('username') is not None

@app.route('/', methods=['GET', 'POST'])
def landing():
    # Check for session existence
    #db_builder.dbsetup()
    if logged_in():
      username = session['username']
      user_id = db_builder.get_id_from_username(username)
      return render_template('home.html', username=username, user_id=user_id, random_users=db_builder.get_random_users())
    else:
      # If not logged in, show login page
      return render_template('intro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    method = request.method
    # Check for session existance
    if method == 'GET':
      if logged_in():
        return redirect(url_for('landing'))
      else:
        # If not logged in, show login page
        return render_template('login.html', error=False)

    if method == 'POST':

      # Get information from request.form since it is submitted via post
      username = request.form['username']
      password = request.form['password']
      error = db_builder.login(username, password)

    if error:
        # If incorrect, give feedback to the user
        return render_template('login.html', error=error)
    else:
        # Store user info into a cookie
        session['username'] = username
        return redirect(url_for('landing'))


@app.route('/register', methods=['GET','POST'])
def register():
    method = request.method
    # Check for session existence
    if method == "GET":
        if logged_in():

            return redirect(url_for('landing'))
        else:
            # If not logged in, show regsiter page
            return render_template('register.html', error_message="")

    if method == "POST":
        new_username = request.form["new_username"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        error_message = ""
        if not new_username:
            error_message = "Error: No username entered!"
        elif not new_password:
            error_message = "Error: No password entered!"
        elif confirm_password != new_password:
            error_message = "Error: Passwords do not match!"

        if error_message:
            return render_template("register.html", error_message=error_message)

        error_message = db_builder.signup(new_username, new_password)

        if error_message:
            return render_template("register.html", error_message=error_message)
        else:
            session['username'] = new_username
            return redirect(url_for('landing'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    # Once again check for a key before popping it
    if logged_in():
        session.pop('username')

    # After logout, return to login page
    return redirect(url_for('landing'))


####BLOG FUNCTIONS#####
#######################




@app.route('/user/<string:username>/user_profile', methods=['GET'])
def display_user_profile(username):
    if not logged_in:
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(username)
    templateArgs = {
        
        "user_personal_info": db_builder.get_user_info(user_id),
        "username": username,
        "user_id": user_id,
        
    }
    
    return render_template("edit_profile.html", **templateArgs)

@app.route('/user/<string:username>/saved_recipes', methods=['GET'])
def display_user_favoriteRecipes(username):
    if not logged_in:
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(username)
    templateArgs = {
        "favorite_recipes" : db_builder.get_favorite_recipes(user_id, 0, 50),
        "user_personal_info": db_builder.get_user_info(user_id),
        "user_post_count": db_builder.get_user_post_count(user_id),
        "user_favorite_recipe_count": db_builder.get_favorite_recipe_count(user_id),
        "username": username,
        "user_id": user_id,
        "lookingAtOwnBlog": session.get('username') == username
    }
    
    return render_template("favorite_recipes.html", **templateArgs)

@app.route('/user/<string:username>/user_comments', methods=['GET'])
def display_user_comments(username):
    if not logged_in:
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(username)
    templateArgs = {
        "user_comments": db_builder.get_comments(user_id, 0, 50),
        "user_personal_info": db_builder.get_user_info(user_id),
        "user_post_count": db_builder.get_user_post_count(user_id),
        "user_favorite_recipe_count": db_builder.get_favorite_recipe_count(user_id),
        "username": username,
        "user_id": user_id,
        "lookingAtOwnBlog": session.get('username') == username
    }
    
    return render_template("user_comments.html", **templateArgs)

@app.route('/user/<string:username>/user_posts', methods=['GET'])
def display_user_posts(username):
    if not logged_in:
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(username)
    
    templateArgs = {
        "print": print,
        "openModalOnLoad": request.args.get('openModalOnLoad', None),
        "db_builder": db_builder,
        "user_posts" : db_builder.get_posts(user_id, 0, 50),
        "user_personal_info": db_builder.get_user_info(user_id),
        "user_post_count": db_builder.get_user_post_count(user_id),
        "user_favorite_recipe_count": db_builder.get_favorite_recipe_count(user_id),
        "username": username,
        "user_id": user_id,
        "lookingAtOwnBlog": session.get('username') == username,
        "viewer_user_id": db_builder.get_id_from_username(session.get('username'))
    }
   
    
    return render_template("user_posts.html", **templateArgs)

@app.route('/api/update_user_info', methods=['POST'])
def update_user_info():
    if not logged_in(): 
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(session.get('username'))
    username = session.get('username')
    bio = request.form.get('bio', "")
    display_name = request.form.get('display_name', "")
    original = db_builder.get_user_info(user_id)
    db_builder.update_user_info(user_id, original['preferred_cuisines'], original['diet'], original['intolerances'], display_name, bio, original['profile_picture'])
    return redirect(f"/user/{username}/saved_recipes")

@app.route('/api/make_comment', methods=['POST'])
def make_comment():
    if not logged_in(): 
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(session.get('username'))
    db_builder.create_comment(user_id, request.json['post_id'], request.json['comment'])
    print((user_id, request.json['post_id'], request.json['comment']))
    return {
        "successful": True
    }

@app.route('/api/delete_comment', methods=['POST'])
def delete_comment():
    if not logged_in(): 
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(session.get('username'))
    db_builder.delete_comment(user_id, request.json['comment_id'])
    return {
        "successful": True
    }
    
    
    
    
@app.route('/api/update_user_profile_picture', methods=['POST'])
def update_user_profile_picture():
    if not logged_in(): 
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(session.get('username'))
    username = session.get('username')
    image_link = request.files.get('profile_picture') #Not actually a link. This is actually a file. 
    image_string = base64.b64encode(image_link.read()).decode('ascii')
    original = db_builder.get_user_info(user_id)
    db_builder.update_user_info(user_id, original['preferred_cuisines'], original['diet'], original['intolerances'], original['display_name'], original['bio'], f"data:{image_link.mimetype};base64,{str(image_string)}")
    return redirect(f"/user/{username}/saved_recipes")

@app.route('/api/make_post', methods=['POST'])
def make_post():
    if not logged_in():
        return redirect(url_for('landing'))
    user_id = db_builder.get_id_from_username(session.get('username'))
    username = session.get("username")
    image_link = request.files.get('image_link') #Not actually a link. This is actually a file. 
    image_string = base64.b64encode(image_link.read()).decode('ascii')
    
    post_description = request.form.get("post_description")
    
    db_builder.create_post(user_id, None, f"data:{image_link.mimetype};base64,{str(image_string)}", post_description)
    return redirect(f"/user/{username}/user_posts")

@app.route('/api/delete_post', methods=['POST'])
def delete_post():
    if not logged_in():
        return redirect(url_for('landing'))
    username = session.get('username')
    user_id = db_builder.get_id_from_username(username)
    post_id = request.form.get('post_id')
    db_builder.delete_post(user_id, post_id)
    return redirect(f'/user/{username}/user_posts')

@app.route('/api/is_recipe_favorited', methods=['POST'])
def is_recipe_favorited():
    user_id = request.json['user_id']
    recipe_id = request.json['recipe_id']
    return {
        'favorited': db_builder.is_recipe_favorited(user_id, recipe_id)
    }

@app.route('/api/is_post_favorited', methods=['POST'])
def is_post_favorited():
    print(request.json)
    user_id = request.json['user_id']
    post_id = request.json['post_id']
    return {
        'favorited': db_builder.is_post_favorited(user_id, post_id)
    }

@app.route('/api/favorite_recipe', methods=['POST'])
def favorite_recipe():
    print(request.data)
    user_id = request.json['user_id']
    recipe_id = request.json['recipe_id']
    db_builder.favorite_recipe(user_id, recipe_id, recipes.getRecipeInformation(recipe_id))
    return {"message": "Successfully favorited recipe"}
    

@app.route('/api/unfavorite_recipe', methods=['POST'])
def unfavorite_recipe():
    print(request.data)
    user_id = request.json['user_id']
    recipe_id = request.json['recipe_id']
    db_builder.unfavorite_recipe(user_id, recipe_id)
    return {"message": "Successfully unfavorited recipe"}
    
@app.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_page(recipe_id):
    if not logged_in():
        return redirect(url_for('landing'))
    recipe = recipes.getRecipeInformation(recipe_id)
    templateArgs = {
        'usda_api': usda_api,
        'recipe': recipe,
        'username': session.get('username'),
        'user_id': db_builder.get_id_from_username(session.get('username'))
    }
    
    return render_template('recipe_page.html', **templateArgs)
    

 

@app.route('/restaurants', methods=['GET', 'POST'])
def restaurant():
    login = False
    if logged_in():
        login = True
    else:
        login = False

    random_cats = ['pizza', 'indpak', 'japanese', 'chinese', 'vegan', 'restuarants']
    x = random.randrange(0,5)

    my_headers = {'Authorization' : 'Bearer gJIaQ2GgBZJRE1iV61MUNNMIw8v_Q4x1aAKYFnq6TZrNQHsCwi1b8bpuDZ_MmWUk9paI5MDAYFtfkcrE_HCZZMQhf4L1yc0heQ4coxKhhELU7Cqdy2XUsAaik0C7YXYx'}
    r = requests.get(f'https://api.yelp.com/v3/businesses/search?location=NYC&categories={random_cats[x]}', headers=my_headers)
    # print(r.json())
    return render_template('restaurants.html', data=r.json()['businesses'], logged_in=login)

@app.route('/restaurants/search', methods=['GET', 'POST'])
def restaurants_search():
    login = False
    if logged_in():
        login = True
    else:
        login = False
    
    method = request.method
    if method == 'GET':
        s = request.args['location']
        c = request.args['cuisine']
    if method == 'POST':
        s = request.form['location']
        c = request.form['cuisine']
   
    s = s.lower()
    
    if c == "All":
        c = 'restaurants'
    else:
        c = c.lower()
    my_headers = {'Authorization' : 'Bearer gJIaQ2GgBZJRE1iV61MUNNMIw8v_Q4x1aAKYFnq6TZrNQHsCwi1b8bpuDZ_MmWUk9paI5MDAYFtfkcrE_HCZZMQhf4L1yc0heQ4coxKhhELU7Cqdy2XUsAaik0C7YXYx'}
    # r = requests.get(f"https://api.yelp.com/v3/businesses/search?location=NYC&categories=restuarants&term={s}", headers=my_headers)
    r = requests.get(f"https://api.yelp.com/v3/businesses/search?location={s}&categories={c}", headers=my_headers)
    if s != "":
        return render_template('restaurants.html', data=r.json()['businesses'], logged_in=login) 
    else:
        r = requests.get("https://api.yelp.com/v3/businesses/search?location=NYC&categories=restaurants", headers=my_headers)
        return render_template('restaurants.html', data=r.json()['businesses'], logged_in=login) 

@app.route('/restaurants/view', methods=['GET', 'POST'])
def restaurants_view():
    i = request.args.get('id')
    my_headers = {'Authorization' : 'Bearer gJIaQ2GgBZJRE1iV61MUNNMIw8v_Q4x1aAKYFnq6TZrNQHsCwi1b8bpuDZ_MmWUk9paI5MDAYFtfkcrE_HCZZMQhf4L1yc0heQ4coxKhhELU7Cqdy2XUsAaik0C7YXYx'}
    r = requests.get(f"https://api.yelp.com/v3/businesses/{i}", headers=my_headers)
    # print(r.json())
    return render_template('view_restaurant.html', res=r.json())

@app.route('/recipes/search', methods=['GET', 'POST'])
def recipes_search():
    if not logged_in():
        redirect(url_for("landing"))
    user_id = db_builder.get_id_from_username(session.get("username"))
    if(request.method == 'GET'):
        return render_template('recipes.html', user_id=user_id, username=session.get("username"))
    if(request.method == 'POST'):
        query = request.form.get("search")
        return render_template('recipes.html', recipes=recipes.searchRecipes(query), 
        user_id=user_id, username=session.get("username"))


if __name__ == '__main__':
    app.debug = True
    app.run()