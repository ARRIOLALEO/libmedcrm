from flask import Flask , g, render_template, request, session
from helpers import  login_require
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# here we define our objet bd that help us to conect to the database
DATABSE  =  'cmslibmed.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_require
def main():
    return render_template("main.html")

# we also need to add all the doctos
@app.route('/doctors', methods=["GET","POST"])
@login_require
def doctors():
    if request.method == "GET":
        return 'here go the doctos'

# we need to see the filter for month or per week we will add search from one time to another

@app.route('/search', methods=['GET', "POST"])
@login_require
def search():
    if request.method == "GET":
        return 'here we will have our search'

@app.route('/report')
@login_require
def reports():
    return 'here we will get the reports'
    
# this is our login app

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #ensure username was submited
        if not request.form.get("username"):
            return "you need to add a username"
       # here we check if we have a password
        if not request.form.get("password"):
            return "you need to write your password"

       #im need to connect to the data base ana select the user
        with sqlite3.connect("cmslibmed.db") as con:
            cur = con.cursor()
            user_exist = cur.execute("SELECT * FROM users WHERE user= (?)", request.form("username"))
            if len(user_exist) != 1:
                return "this user dosent exits"

           # now we need to check the user password it is the same
            if not check_password_hash(user_exist[0]['pasword'], request.form.get("password")):
               return "the password doesnt mach"
            session["user_id"] = user_exist[0]['id']

    else:
        return render_template("login.html")

# add send sms will be great to add to the system

