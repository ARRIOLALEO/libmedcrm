from flask import Flask , g, render_template, request, session, redirect
from helpers import  login_require
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from flask_session import Session
from tempfile import mkdtemp
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cmslibmed.db")

app = Flask(__name__)
# here we define our objet bd that help us to conect to the database
DATABSE  =  'cmslibmed.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#her we configure our sessions
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
@login_require
def main():
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        all_orders = cur.execute("select * FROM orders  INNER JOIN clients  ON clients.id=orders.id_client INNER JOIN doctors ON orders.doctor=doctors.id INNER JOIN paramedics ON paramedics.id = orders.paramedic INNER JOIN drivers ON drivers.id=orders.driver INNER JOIN dispachers ON dispachers.id=orders.dispacher")
        customers = all_orders.fetchall()
        print(customers[0])
        return render_template("main.html",customers=customers)

# we also need to add all the doctos
@app.route('/doctors', methods=["GET","POST"])
@login_require
def doctors():
    if request.method == "GET":
        with sqlite3.connect("cmslibmed.db") as conn:
            cur = conn.cursor()
            doctors = cur.execute("SELECT * FROM doctors");
            all_doctors = doctors.fetchall()
            return render_template("doctos.html" , doctors=all_doctors)
    else:
        doctor_name = request.form.get("name")
        doctor_espc = request.form.get("especiality")
        doctor_phone = request.form.get("phone")
        doctor_address = request.form.get("address")
        if not doctor_name or not doctor_espc or not doctor_phone or not doctor_address:
            return "something is missin"
        else:
            with sqlite3.connect("cmslibmed.db") as conn:
                cur = conn.cursor()
                doctor_exist = cur.execute("SELECT * FROM doctors WHERE phone=(?)",(doctor_phone,))
                there_is_doctor = doctor_exist.fetchall()
                if not there_is_doctor:
                    cur.execute("INSERT INTO doctors(name, especiality, phone, adress) VALUES(?, ?, ? ,?)",
                            (doctor_name, doctor_espc, doctor_phone, doctor_address))
                    return redirect("/doctors")
                else:
                    return "the doctor alredy exist on the data base the same phone"




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
        if not request.form.get("user"):
            return "you need to add a username"
       # here we check if we have a password
        if not request.form.get("password"):
            return "you need to write your password"

       #im need to connect to the data base ana select the user
        with sqlite3.connect("cmslibmed.db") as con:
            cur = con.cursor()
            user_exist = cur.execute("SELECT * FROM user")
            password = request.form.get("password")
            response = user_exist.fetchall()
            if not check_password_hash(response[0][2], password):
               return "the password doesnt mach"
            session["user_id"] = response[0][0]
            return redirect("/")

    else:
        return render_template("login.html")

# add send sms will be great to add to the system

@app.route('/clients', methods=["GET", "POST"])
@login_require
def clients():
    if request.method == "POST":
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            exist_client = cur.execute("SELECT * FROM clients WHERE phone=(?)" ,(request.form.get("phone"),))
            was_found = exist_client.fetchall()
            if len(was_found) == 0:
                get_doctors = cur.execute("SELECT * FROM doctors")
                all_doctors = get_doctors.fetchall()
                get_paramedics = cur.execute("SELECT * FROM paramedics")
                all_paramedics = get_paramedics.fetchall()
                get_drivers = cur.execute("SELECT * FROM drivers")
                all_drivers = get_drivers.fetchall()
                get_dispachers = cur.execute("SELECT * FROM dispachers")
                all_dispachers = get_dispachers.fetchall()
                return render_template("addcleint.html",
                        doctors=all_doctors, paramedics=all_paramedics, drivers=all_drivers, dispachers = all_dispachers)
            else:
                return "customer was found and we can add a new order"
    else:
        return render_template("searchcustomer.html")

@app.route("/paramedics", methods=["GET", "POST"])
@login_require
def paramedics():
    if request.method == "POST":
        doctor_name     = request.form.get("name")
        doctor_spc      = request.form.get("especiality")
        doctor_phone    = request.form.get("phone")
        doctor_address  = request.form.get("address")
        if not doctor_name or not doctor_spc or not doctor_phone or not doctor_address:
            return "you need to fill all the fields"
        else:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                exist_paramedic = cur.execute("SELECT * FROM paramedics WHERE phone=(?)", (doctor_phone,))
                alredy_in_db = exist_paramedic.fetchall()
                if not alredy_in_db:
                    cur.execute("INSERT INTO paramedics(name, especiality, phone, address) VALUES(?, ?, ?, ?)",
                            (doctor_name, doctor_spc, doctor_phone, doctor_address, ))
                    return redirect("/paramedics") 
                else:
                    return  "somthing is happening here"
    else:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            paramedics_all = cur.execute("SELECT * FROM paramedics")
            paramedics = paramedics_all.fetchall()
            return render_template("paramedics.html",paramedics=paramedics)

@app.route("/drivers", methods=["GET","POST"])
@login_require
def drivers():
    if request.method == "POST":
        driver_name = request.form.get("name")
        driver_phone = request.form.get("phone")
        driver_address = request.form.get("address")
        if not driver_name or not driver_phone or  not  driver_address:
            return "here we have some issues"
        else:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                exist_driver = cur.execute("SELECT * FROM drivers WHERE phone=(?)",(driver_phone,))
                alredy_driver_in_db = exist_driver.fetchall()
                if not alredy_driver_in_db:
                    cur.execute("INSERT INTO drivers(name, phone, adress) VALUES(?, ?, ?)",(driver_name, driver_phone, driver_address ,))
                    return redirect("/drivers")
                else:
                    return "the driver alredy exist in the db"
    else:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            all_drivers_in_db = cur.execute("SELECT * FROM drivers")
            all_drivers = all_drivers_in_db.fetchall()
            return render_template("drivers.html",drivers=all_drivers)

@app.route("/dispachers", methods=["GET","POST"])
@login_require
def dispachers():
    if request.method == "POST":
        dispacher_name = request.form.get("name")
        dispacher_phone = request.form.get("phone")
        dispacher_address = request.form.get("address")
        if not dispacher_name or not dispacher_phone or not dispacher_address:
            return "some information is missing"
        else:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                exist_dispacher = cur.execute("SELECT * FROM  dispachers WHERE phone=(?)",(dispacher_phone, ))
                alredy_dispacher = exist_dispacher.fetchall()
                if not alredy_dispacher:
                    cur.execute("INSERT INTO dispachers(name, phone, address) VALUES(?, ?, ?)",
                            (dispacher_name, dispacher_phone, dispacher_address,))
                    return redirect("/dispachers")
                else:
                    return "this dispacher is alredy in the data base"

    else:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            all_dispachers = cur.execute("SELECT * FROM dispachers")
            return render_template("dispachers.html", dispachers=all_dispachers)


@app.route("/addorder",methods=["GET", "POST"])
@login_require
def addorder():
    if request.method == "POST":
        date_in = request.form.get("data")
        time_in = request.form.get("time")
        time_out = request.form.get("time2")
        name = request.form.get("name")
        age = request.form.get("age")
        address = request.form.get("address")
        tel = request.form.get("tel")
        information = request.form.get("information")
        diagnost = request.form.get("diagnost")
        prescription=request.form.get("prescription")
        recomendation=request.form.get("exodo")
        doctor= request.form.get("doctor")
        paramedic=request.form.get("paramedic")
        driver=request.form.get("driver")
        dispacher=request.form.get("dispacher")
        customer_type = request.form.get("type")
        if customer_type == "1":
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO clients(name, phone, address) VALUES(?, ?, ?)",(name, tel, address,))
                get_user =  cur.execute("SELECT id FROM clients WHERE phone =(?)",(tel,))
                the_user = get_user.fetchall()
                print(date_in)
                # here i will add to my oders the new oder
                cur.execute("INSERT INTO orders(datein, timein, timeout, id_client, age, description, diagnost, help, recomendation, doctor, paramedic, driver, dispacher) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(date_in, time_in, time_out, the_user[0][0], age, information, diagnost, prescription, recomendation, doctor, paramedic, driver, dispacher))
            return redirect("/")
        else:
            return "something is hapening"
