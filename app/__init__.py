'''
Mango: Aryaman Goenka, Sadid Ethun, Haotian Gan
Softdev
P00: ArRESTed Development
2021-12-12
'''
import sqlite3
import db_builder
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'Mango'

# Utility function to check if there is a session
def logged_in():
    return session.get('username') is not None

@app.route('/', methods=['GET', 'POST'])
def landing():
    # Check for session existance
    #db_builder.dbseteup()
    if logged_in():
        username = session['username']
        # return render_template('index.html', username=username, search=filter)
        user_id = db_builder.get_id_from_username(username)
        return render_template('home.html', username=username, user_id=user_id)
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

@app.route('/blog/<int:user_id>', methods=['GET', 'POST'])
def display_user_blog(user_id):
    """Displays all entires of a user. Tracks if the user is the same one that is logged in"""

    if not logged_in():
        # If not logged in, redirect to the main page
        return redirect(url_for('landing'))
    
    templateArgs = {
        "entries" : db_builder.get_entries_of_user(user_id, 0, 50), #see get_entries_of_user in database.py
        "username" : session.get('username'),#see get_username_from_id in database.py
        "lookingAtOwnBlog": db_builder.get_id_from_username(session.get('username')) == user_id #session authentication for the user
    }
    return render_template(
        'blog.html',
        **templateArgs
    )

@app.route('/entry/<int:entry_id>', methods=['GET', 'POST'])
def display_entry(entry_id):
    """Displays an entry of another user's blog to the user"""
    template_args = {}
    try:
        template_args = db_builder.get_entry(entry_id) #see get_entry in database.py
        template_args["username"] = db_builder.get_username_from_id(template_args["user_id"])
        template_args["original_author"] = session.get("user_id") == template_args["user_id"] #logic check if the user currently viewing a blog is viewing their own blog
    except Exception:
        return render_template("404.html")
    return render_template(
        'entry.html',
        **template_args
    )

@app.route('/blog/newBlogEntry', methods=['GET', 'POST'])
def create_new_entry():
    """Allows the user to create a new blog entry"""
    try:
        if(session.get("user_id") == None):
            return redirect("/") #if a non-logged in user gets here, redirect them to the login page
        if(request.method == 'POST'):
            user_id = session.get("user_id")
            new_entry_text = request.form.get('entry_text')
            new_title = request.form.get('title')
            if(new_title != ''): #can't have blank title
                db_builder.add_entry(new_title, new_entry_text, user_id) #see add_entry in database.py
            else:
                return redirect('/blog/newBlogEntry')

            #This assumes that the entry_id of the one we just added to the database, is the user's most recent entry
            assumed_entry_id = db_builder.getMostRecentEntry(user_id)["entry_id"]
            return redirect(f"/entry/{assumed_entry_id}")
        return render_template("newBlogEntry.html", user_id=session.get("user_id"))
    except Exception:
        return "Something went wrong on our end. Please try again later."

@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
def display_entry_edit(entry_id):
    """Allows a user to edit their own entry"""
    try:
        if(session.get("user_id") == None):
            return redirect("/")
        if request.method == 'POST':
            author_id = db_builder.get_entry(entry_id)["user_id"]
            if(not author_id == session.get("user_id")):
                return "Sorry, you can't modify this blog post if you aren't its author."
            new_entry_text = request.form.get('entry_text')
            new_title = request.form.get('title')
            db_builder.edit_entry(entry_id, new_entry_text, new_title)
            return redirect(f"/entry/{entry_id}")
        if request.method == 'GET':
            templateArgs = db_builder.get_entry(entry_id)
            return render_template('entry_edit.html', **templateArgs) #displays the text boxes with current text and title of the post already displayed
    except Exception:
        return render_template("404.html")

@app.route('/entry/delete', methods=['POST'])
def delete():
    """Removes a user's blog entry"""
    try: 
        if(session.get("user_id") == None):
            return redirect("/")
        entry_id = request.form["entry_id"]
        author_id = db_builder.get_entry(entry_id)["user_id"] #see get_entry in database.py
        user_id = session.get("user_id")
        if(not author_id == user_id):
            return "Sorry, you can't modify this blog post if you aren't its author."

        db_builder.delete_entry(entry_id) #see delete_entry in database.py
        return redirect(f"/blog/{user_id}")
    except Exception:
        return render_template("404.html")

if __name__ == '__main__':
    # db_builder.dbseteup()
    app.debug = True
    app.run()