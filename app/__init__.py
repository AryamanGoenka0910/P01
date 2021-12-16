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
    return session.get('username') != None

@app.route('/', methods=['GET', 'POST'])
def landing():
    # Check for session existence
    if logged_in():
      username = session['username']
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
      

      if db_builder.credentialsExist(username, password):
          # Store user username as session cookie. This uniquely identifies the user
          session['username'] = username
          return redirect(url_for('landing'))
      else:
          # If credentials match, give feedback to the user
          return render_template('login.html', error=error)
          

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


if __name__ == '__main__':
    app.debug = True
    app.run()