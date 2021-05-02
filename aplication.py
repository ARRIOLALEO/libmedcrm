from flask import Flask , render_template, request, session
from helpers import  login_require

app = Flask(__name__)
@app.route('/')
@login_require
def main():
    return render_template("main.html")

# we also need to add all the doctos
@app.route('/doctors', methods=["GET","POST"])
def doctors():
    if request.method == "GET":
        return 'here go the doctos'

# we need to see the filter for month or per week we will add search from one time to another

@app.route('/search', methods=['GET', "POST"])
def search():
    if request.method == "GET":
        return 'here we will have our search'

@app.route('/report')
def reports():
    return 'here we will get the reports'
    
# this is our login app

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
         return 'this is something that needs to be done now to check the database'
    else:
        return render_template("login.html")

# add send sms will be great to add to the system

