'''
Mango: Aryaman Goenka, Sadid Ethun, Haotian Gan
Softdev
P01: ArRESTed Development
2021-12-12
'''

import sqlite3   
import random 
import json

DB_FILE="Mangos.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)

def setup():
  c = db.cursor()

  # Login Table:
  command = "CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT)"
  c.execute(command)   


  # User Personal Info Table:
    ## preferredCuisines, and intolerances are lists. Diet is a single string.
      ### intolerances are things that the user cannot eat (i.e soy, egg, diary)
      ### we'll use this data to filter search results
    ## Supported cuisines are: https://spoonacular.com/food-api/docs#Cuisines
    ## Supported intolerances are: https://spoonacular.com/food-api/docs#Intolerances
    ## Supported diets are on the spoonacular api docs

  command = "CREATE TABLE IF NOT EXISTS user_personal_info (user_id INTEGER NOT NULL, preferredCuisines TEXT DEFAULT '[]', diet TEXT DEFAULT '', intolerances TEXT DEFAULT '[]', displayName TEXT DEFAULT '', personalPageDescription TEXT DEFAULT '')"
  c.execute(command) 

  # User Favorite Resturants:
    # To do

  # User Favorite Recipes: 
    # Recipes can be organized into their own folders, just like songs on spotify. 
  command = "CREATE TABLE IF NOT EXISTS user_favorite_recipe (user_id INTEGER NOT NULL, spoonacular_recipe_id INTEGER, spoonacularRecipeJSON TEXT, folder TEXT)"
  c.execute(command) 

  # User Recipe Folders:
    # This is used to keep track of how many folders a user has
  command = "CREATE TABLE IF NOT EXISTS user_folder (user_id, folder TEXT)"
  c.execute(command) 

  # User Favorite Posts:
  command = "CREATE TABLE IF NOT EXISTS user_favorite_post (user_id INTEGER NOT NULL, post_id INTEGER)"
  c.execute(command) 

  # User Posts:
  command = "CREATE TABLE IF NOT EXISTS user_post (user_id INTEGER NOT NULL, post_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, recipe_id INTEGER, image_link TEXT, post_description TEXT)"
  c.execute(command) 

  # Post Comments:
  command = "CREATE TABLE IF NOT EXISTS user_comment (comment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, post_id INTEGER NOT NULL, comment TEXT)"
  c.execute(command) 

  db.commit() 

setup()

# Authorization, username, and user_id functions

def credentialsExist(username, password):
  "If the username and password combination matches a database entry, this returns True. Otherwise, it returns False"
  c = db.cursor()
  c.execute("SELECT username FROM user WHERE username=? AND password=?", [username, password])
  result = c.fetchone()
  return bool(result)

def get_id_from_username(username):
  """returns the user id given the username"""
  c = db.cursor()
  c.execute("SELECT user_id from user where username == ?", [username])
  row = c.fetchone()
  if row:
    return row[0]
  raise Exception("No user_id for that username")
      
def get_username_from_id(user_id):
  """returns the username given the user_id"""
  c = db.cursor()
  c.execute(f'SELECT username from user where user_id == ?', [user_id])
  result = c.fetchone()
  if result:
    return result[0]
  raise Exception("No username for that user_id")

# Adds to the user database if the username is availible
# Returns an error message to display if there was an issue or an empty string otherwise
def signup(username, password):
    c = db.cursor()
    c.execute("SELECT username FROM user WHERE username=?", [username])
    result = c.fetchone()

    if result:
        return "Error: Username already exists"

    else:
        c.execute('INSERT INTO user (username, password) VALUES (?, ?)', [username, password])
        db.commit()
        c.execute('INSERT INTO user_personal_info (user_id, preferredCuisines, diet, intolerances, displayName, personalPageDescription) VALUES (?, ?, ?, ?, ?, ?)', 
                  [get_id_from_username(username), json.dumps([]), "", json.dumps([]), "", ""])
        db.commit()

        # Uses empty quotes since it will return false when checked as a boolean
        return ""




  
  


