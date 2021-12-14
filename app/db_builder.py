'''
Mango: Aryaman Goenka, Sadid Ethun, Haotian Gan
Softdev
P00: ArRESTed Development
2021-12-12
'''

import sqlite3   #enable control of an sqlite database

DB_FILE="Mangos.db"
db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create


def dbseteup():
    c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

    c.execute("DROP TABLE IF EXISTS Entries")
    command = "CREATE TABLE Entries (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT, Text TEXT, UserID INTEGER)"

    c.execute("DROP TABLE IF EXISTS Users")
    command = "CREATE TABLE Users (ID INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT, Password TEXT)"
    c.execute(command)      # test SQL stmt in sqlite3 shell, save as string
    # run SQL statement

    db.commit() #save changes
    db.close()  #close database

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

def add_entry(title, entry_text, user_id):
    """Adds an entry into the entries table, stores the text, title, and the user id of the associated account"""
    c = db.cursor()
    c.execute(f'INSERT INTO entries (title, entry_text, user_id) VALUES (?, ?, ?)', (title, entry_text, user_id))
    db.commit() 

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

def get_entry(entry_id):
    """Returns a list based on the entry id with values of the id, text, title, and assosciated user id"""
    c = db.cursor()
    result = list(c.execute(f'select entry_id, entry_text, title, user_id from entries where entry_id == ?', (entry_id, )))
    if(len(result) == 0): #if there is no entry with the id 
        return None
    return [{
        "entry_id": entry_id,
        "entry_text": entry_text,
        "title": title,
        "user_id": user_id
    } for (entry_id, entry_text, title, user_id) in result][0] #returning only the selected entry

def get_entries_of_user(user_id, offset, limit):
    """Returns a list of lists with user entries from the offset to the limit"""
    c = db.cursor()
    result = list(c.execute(f'select entry_id, entry_text, title, user_id from entries where user_id == ? order by entry_id limit ? offset ? ', (user_id, limit, offset)))
    return [{
        "entry_id": entry_id,
        "entry_text": entry_text,
        "title": title,
        "user_id": user_id
    } for (entry_id, entry_text, title, user_id) in result] #all the entries of a user

def get_username_from_id(user_id):
    """returns the username given the user id"""
    c = db.cursor()
    result = list(c.execute(f'SELECT username from users where user_id == ?', (user_id, )))[0][0]
    return result

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