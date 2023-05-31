from math import ceil
from datetime import date, timedelta, datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from support import login_required, db_input

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    return redirect("/book")


@app.route("/doctors")
@login_required
def doctors():
    return render_template("doctors.html")


@app.route("/hours")
@login_required
def hours():
    return render_template("hours.html")


@app.route("/access")
@login_required
def access():
    return render_template("access.html")


@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    """ fills the form for the appointments page """
    # User reached route via POST (by deleting appt)
    if request.method == "POST":
        raw_data = request.form.get("delete")
        d, t, pet, doc = raw_data.split("-")
        pet_id = db_input("SELECT id FROM pets WHERE name=?", (pet,))[0]["id"]
        doc_id = db_input("SELECT id FROM doctors WHERE name=?", (doc,))[0]["id"]
        prompt = "DELETE from BOOKINGS WHERE doctor_id=? "\
                 "AND pet_id=? AND date=? AND time=? AND user_id=?"
        db_input(prompt, (doc_id, pet_id, d, t, session["user_id"]))

        return redirect("/appointments")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        prompt = "SELECT date, time, pets.name AS pet, doctors.name AS doctor FROM bookings "\
                 "JOIN pets ON pets.id = pet_id JOIN doctors ON doctors.id=doctor_id "\
                 "WHERE user_id = 5 ORDER BY date ASC, time ASC"
        results = db_input(prompt)
        now = datetime.today().replace(second=0, microsecond=0)
        upcoming = [item for item in results if now <= datetime(
            now.year, *map(int, item["date"].split("/")), *map(int, item["time"].split(":")))]
        past = [item for item in results if item not in upcoming][::-1]
        u_appt = [(appt['date'], "at", appt['time'], "-", appt['pet'], "with", appt['doctor']) for appt in upcoming]
        p_appt = [(appt['date'], "at", appt['time'], "-", appt['pet'], "with", appt['doctor']) for appt in past]

        return render_template("bookings.html", u_appt=u_appt, p_appt=p_appt)


def get_avail(n, doctor, times, dates):
    """ gets availablity for the upcoming dates and times """
    availability = []
    symbols = {0: {'class': 'xxx', 'shape': '✕'},
               1: {'class': 'tri', 'shape': '△'},
               2: {'class': 'cir', 'shape': '◯'}}
    prompta = "SELECT COUNT(*) AS x FROM bookings WHERE date=? AND time=?"
    promptb = "SELECT COUNT(*) AS x FROM bookings JOIN doctors ON doctors.id"\
              "= doctor_id WHERE date=? AND time=? AND doctors.name=?"

    if n != 1:
        availability = [db_input(prompta, (d, t))[0]["x"] for t in times for d in dates]
    else:
        availability = [db_input(promptb, (d, t, doctor))[0]["x"] for t in times for d in dates]

    classes = [symbols[ceil(-x/n+2)]["class"] for x in availability]
    marks = [symbols[ceil(-x/n+2)]["shape"] for x in availability]
    return classes, marks


@app.route("/repopulate", methods=["GET", "POST"])
@login_required
def repopulate():
    """ fills the form for the booking page """
    times = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00',
             '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30']
    dates = [(date.today() + timedelta(days=i)).strftime('%m/%d') for i in range(5)]
    pet_list = db_input("SELECT * FROM pets WHERE owner_id = ?", (session["user_id"],))
    pets = [pet["name"] for pet in pet_list]
    doc_list = db_input("SELECT * FROM doctors")
    doctors = [doc["name"] for doc in doc_list]

    # User reached route via POST (by changing the dropdown)
    if request.method == "POST":
        select = request.form.get("selected_option")
        if select == "No Preference":
            classes, marks = get_avail(len(doctors), select, times, dates)
        else:
            classes, marks = get_avail(1, select, times, dates)

        return render_template("book.html", times=times, dates=dates, pets=pets, doctors=doctors, classes=classes, marks=marks, select=select)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        classes, marks = get_avail(len(doctors), None, times, dates)
        return render_template("book.html", times=times, dates=dates, pets=pets, doctors=doctors, classes=classes, marks=marks, select="None")


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    """Book new appointment (Home for logged-in users)"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #! check dr and pet, get buttonclicked add appt to database
        # Get form fields
        doctor = request.form.get("doctor")
        pet = request.form.get("pet")
        # Ensure doctor was provided
        if not doctor:
            flash(f"Please select which doctor")
            return redirect("/repopulate")
        # Ensure new value was provided
        elif not pet:
            flash(f"Please select which pet")
            return redirect("/repopulate")
        # Get clicked button & separate date and time
        slot = request.form.get("book-slot")
        slot_d, slot_t = slot.split("-")

        if doctor == "No Preference":
            listofdocs = [x['id'] for x in db_input("SELECT id FROM doctors")]
            prompt = "SELECT doctor_id AS d, COUNT(doctor_id) AS c FROM bookings WHERE date=? GROUP BY doctor_id ORDER BY c ASC"
            results = {d["d"]: d["c"] for d in db_input(prompt, (slot_d,))}
            output = [(doc, results.get(doc, 0)) for doc in listofdocs]
            doc_id = min(output, key=lambda x: x[1])[0]
        else:
            doc_id = db_input("SELECT id FROM doctors WHERE name=?", (doctor,))[0]["id"]
        pet_id = db_input("SELECT id FROM pets WHERE name=? AND owner_id=?", (pet, session["user_id"]))[0]["id"]
        values = (pet_id, session["user_id"], doc_id, slot_d, slot_t)
        db_input("INSERT INTO bookings(pet_id, user_id, doctor_id, date, time) VALUES (?,?,?,?,?)", values)

        # Redirect user to booking page with flash message
        flash("Appointment Booked")
        return redirect("/appointments")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/repopulate")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update User Information (Required when first registered)"""
    # Get user info from database
    user = db_input("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get form fields
        content = request.form.get("content")
        current = user[0][content.split()[0].lower()]
        old = request.form.get("old-x")
        new = request.form.get("new-x")
        # Ensure old value was provided
        if not old:
            flash(f"Original {content} Required")
            return render_template("update.html", content=content, current=current)
        # Ensure new value was provided
        elif not new:
            flash(f"New {content} Required")
            return render_template("update.html", content=content, current=current)
        # Ensure new value confirmation is correct
        elif new != request.form.get("conf-x"):
            flash(f"New {content}s Do Not Match")
            return render_template("update.html", content=content, current=current)
        # Ensure username has not been already taken
        if not check_password_hash(current, generate_password_hash(old)):
            flash(f"Old {content} Does Not Match")
            return render_template("update.html", content=content, current=current)
        # Encrypt password
        if content == "Password":
            new = generate_password_hash(new)
        db_input(f"UPDATE users SET {content.split()[0].lower()}=? WHERE id = ?", (new, session["user_id"]))
        # Redirect user to booking page with flash message
        flash(f"{content} Updated")
        return redirect("/settings")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        content = request.args["content"]
        current = user[0][content.split()[0].lower()]
        return render_template("update.html", content=content, current=current)


@app.route("/pet_update", methods=["GET", "POST"])
@login_required
def pet_update():
    """Update User Information (Required when first registered)"""
    # Get current list of pets
    pet_list = db_input("SELECT * FROM pets WHERE owner_id = ?", (session["user_id"],))
    pets = [pet["name"] for pet in pet_list]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        pet_name = request.form.get("new-pet")
        db_input("INSERT INTO pets (name, owner_id) VALUES (?, ?)", (pet_name, session["user_id"]))

        # Redirect user to booking page with flash message
        flash("Pet Added")
        return redirect("/settings")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("pets.html", pets=pets)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """View User Information to Update (Required when first registered)"""
    # Get information for user
    current_user = db_input("SELECT * FROM users WHERE id = ?", (session["user_id"],))[0]
    pet_list = db_input("SELECT * FROM pets WHERE owner_id = ?", (session["user_id"],))
    petnames = [pet["name"] for pet in pet_list]
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for pet delete
        delete = request.form.get("delete")
        if delete:
            db_input("DELETE FROM pets WHERE owner_id=? AND name=?", (session["user_id"], delete))
            return redirect("/settings")
        # Check for other button click
        content = request.form.get("clicked")
        if content == "Pets":
            # Redirect user to pet update page
            return redirect("/pet_update")
        else:
            # Redirect user to update page
            return redirect(url_for(".update", content=content))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        name = current_user["user"]
        email = current_user["email"]
        return render_template("settings.html", name=name, email=email, petnames=petnames)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Username Required")
            return render_template("login.html")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password Required")
            return render_template("login.html")
        # Query database for username
        rows = db_input("SELECT * FROM users WHERE user = ?", (request.form.get("username"),))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Invalid Username/Password")
            return render_template("login.html")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to booking page
        flash("Login Successful")
        return redirect("/book")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get form data
        pw = request.form.get("password")
        username = request.form.get("username")
        # Ensure username was provided
        if not username:
            flash("Username Required")
            return render_template("register.html")
        # Ensure password was provided
        elif not pw:
            flash("Password Required")
            return render_template("register.html")
        # Ensure password confirmation is correct
        elif pw != request.form.get("re-password"):
            flash("Passwords Do Not Match")
            return render_template("register.html")
        # Get db data based on form
        users = db_input("SELECT * FROM users WHERE user = ?", (username,))
        # Ensure username has not been already taken
        if users:
            flash("Username Unavailable")
            return render_template("register.html")
        # Add to the database
        data = (username, generate_password_hash(pw))
        db_input("INSERT INTO users (user, password) VALUES (?, ?)", data)
        user_id = db_input("SELECT id FROM users WHERE user = ?", (username,))[0]["id"]
        # Remember the new user
        session["user_id"] = user_id
        # Redirect user to settings page
        flash("Signed In: Please add your pet's name")
        return redirect("/settings")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")