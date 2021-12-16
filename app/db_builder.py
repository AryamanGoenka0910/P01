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

def dbsetup():
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

    c.execute("DROP TABLE IF EXISTS Entries")
    command = "CREATE TABLE Entries (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT, Text TEXT, UserID INTEGER)"
    c.execute(command) 

    c.execute("DROP TABLE IF EXISTS Users")
    command = "CREATE TABLE Users (ID INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT, Password TEXT)"
    c.execute(command)      # test SQL stmt in sqlite3 shell, save as string
    # run SQL statement

    db.commit() #save changes
    db.close()  #close database

# User Personal Info Table:
    ## preferredCuisines, and intolerances are lists. Diet is a single string.
      ### intolerances are things that the user cannot eat (i.e soy, egg, diary)
      ### we'll use this data to filter search results
    ## Supported cuisines are: https://spoonacular.com/food-api/docs#Cuisines
    ## Supported intolerances are: https://spoonacular.com/food-api/docs#Intolerances
    ## Supported diets are on the spoonacular api docs

  #command = "CREATE TABLE IF NOT EXISTS user_personal_info (user_id INTEGER NOT NULL, preferredCuisines TEXT DEFAULT '[]', diet TEXT DEFAULT '', intolerances TEXT DEFAULT '[]', displayName TEXT DEFAULT '', personalPageDescription TEXT DEFAULT '')"
  #c.execute(command) 

  # User Favorite Resturants:
    # To do

  # User Favorite Recipes: 
    # Recipes can be organized into their own folders, just like songs on spotify. 
  #command = "CREATE TABLE IF NOT EXISTS user_favorite_recipe (user_id INTEGER NOT NULL, spoonacular_recipe_id INTEGER, spoonacularRecipeJSON TEXT, folder TEXT)"
  #c.execute(command) 

  # User Recipe Folders:
    # This is used to keep track of how many folders a user has
  #command = "CREATE TABLE IF NOT EXISTS user_folder (user_id, folder TEXT)"
  #c.execute(command) 

  # User Favorite Posts:
  #command = "CREATE TABLE IF NOT EXISTS user_favorite_post (user_id INTEGER NOT NULL, post_id INTEGER)"
  #c.execute(command) 

  # User Posts:
  #command = "CREATE TABLE IF NOT EXISTS user_post (user_id INTEGER NOT NULL, post_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, recipe_id INTEGER, image_link TEXT, post_description TEXT)"
  #c.execute(command) 

  # Post Comments:
  #command = "CREATE TABLE IF NOT EXISTS user_comment (comment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, post_id INTEGER NOT NULL, comment TEXT)"
  #c.execute(command) 


# Authorization, username, and user_id functions
##

# Adds to the user database if the username is availible
# Returns an error message to display if there was an issue or an empty string otherwise
def signup(username, password):
    c = db.cursor()

    c.execute("""SELECT Username FROM Users WHERE Username=?""",[username])
    result = c.fetchone()

    if result:
        return "Error: Username already exists"

    else:
        c.execute('INSERT INTO Users VALUES (null, ?, ?)', (username, password))

        db.commit()
        db.close()
        # Uses empty quotes since it will return false when checked as a boolean
        return  ""

# Tries to check if the username and password are valid
def login(username, password):
    c = db.cursor()

    c.execute("""SELECT Username FROM Users WHERE Username=? AND Password=?""",[username, password])
    result = c.fetchone()

    if result:
        ##access this specifc user data
        return False

    else:
        return True

def edit_entry(entry_id, entry_text, title):
    """Updates the text and title of an entry, entry id is not altered"""
    c = db.cursor()
    c.execute(f'UPDATE entries SET entry_text = ?, title = ? where entry_id == ?', (entry_text, title, entry_id))
    db.commit()

def delete_entry(entry_id):
    """Removes an entry from the table based on the entry id"""
    c = db.cursor()
    c.execute(f'delete from entries where entry_id == ?', (entry_id))
    db.commit()

def get_id_from_username(username):
  """returns the user id given the username"""
  c = db.cursor()
  c.execute("SELECT ID from Users where Username == ?", [username])
  row = c.fetchone()
  result = ""
  if row is not None:
    result = row[0]
  return result
      
def get_username_from_id(user_id):
  """returns the username given the user_id"""
  c = db.cursor()
  c.execute(f'SELECT Username from Users where ID == ?', [user_id])
  row = c.fetchone()
  result = ""
  if row is not None:
    result = row[0]
  return result

## (edited)
def add_entry(title, entry_text, user_id):
    """Adds an entry into the entries table, stores the text, title, and the user id of the associated account"""
    c = db.cursor()
    c.execute('INSERT INTO Entries VALUES (null, ?, ?, ?)', (title, entry_text, user_id))
  
    #c.execute('INSERT INTO user_personal_info (user_id, preferredCuisines, diet, intolerances, displayName, personalPageDescription) VALUES (?, ?, ?, ?, ?, ?)', 
    #          [get_id_from_username(username), json.dumps([]), "", json.dumps([]), "", ""])
    db.commit()


## (edited)
def get_entry(entry_id):
    """Returns a list based on the entry id with values of the id, text, title, and assosciated user id"""
    c = db.cursor()

    result = list(c.execute(f'select ID, Text, Title, UserID from Entries where ID == ?', (entry_id)))
    if(len(result) == 0): #if there is no entry with the id 
        return None
    return [{
        "entry_id": entry_id,
        "entry_text": entry_text,
        "title": title,
        "user_id": user_id
    } for (entry_id, entry_text, title, user_id) in result][0] #returning only the selected entry

## (edited)
def get_entries_of_user(user_id, offset, limit):
    """Returns a list of lists with user entries from the offset to the limit"""
    c = db.cursor()
    result = list(c.execute(f'SELECT ID, Text, Title, UserID FROM Entries WHERE UserID == ? order by ID limit ? offset ? ', (user_id, limit, offset)))
    return [{
        "entry_id": entry_id,
        "entry_text": entry_text,
        "title": title,
        "user_id": user_id
    } for (entry_id, entry_text, title, user_id) in result] #all the entries of a user

def getMostRecentEntry(user_id):
    """Returns the users most recent entry by ordering all of their entries in id order, with the entry of the largest id at the top"""
    c = db.cursor()
    result = list(c.execute(f'select entry_id, entry_text, title, user_id from entries where user_id == ? order by entry_id DESC limit 1', (user_id, )))
    return [{
        "entry_id": entry_id,
        "entry_text": entry_text,
        "title": title,
        "user_id": user_id
    } for (entry_id, entry_text, title, user_id) in result][0] #returning first entry in reordered list

def get_random_users():
    """Returns either 10 random users or all users to display as recommended blogs on the homepage"""
    c = db.cursor()
    rows = list(c.execute('SELECT COUNT(*) FROM users'))[0][0] #length of users table
    population_count = 10 if rows >= 10 else rows
    user_ids = random.sample(range(1,rows+1), population_count) #takes 10 distinct random users
    usernames = [get_username_from_id(user_id) for user_id in user_ids]
    return [
        {
            'username': username,
            'user_id': user_id
        } 
    for (username, user_id) in zip(usernames, user_ids)]
  
  


