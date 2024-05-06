from datetime import datetime
import os
import re

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import json
from sqlalchemy import text

from helpers import apology, login_required, admin_required

from updateChurches import getEntitiesWithoutLink

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# Different sql database that works?
db_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_path}'
db = SQLAlchemy(app)

# matches the functionality of the function I used before
def dbExecute(sqlCode, *args):
    result = None

    # If we only have the sql code, run it.
    # If we have multiple arguments, if we have one dict we can just pass it, otherwise, we need to change the ? to using a dict we create.
    if len(args) != 0:
        if type(args[0]) == dict:
            result = db.session.execute(text(sqlCode), args[0])
        else:
            d = {}
            for i in range(len(args)):
                sqlCode = sqlCode.replace("?", ":named" + str(i), 1)
                d["named" + str(i)] = args[i]
            result = db.session.execute(text(sqlCode), d)
    else:
        result = db.session.execute(text(sqlCode))

    try:
        # Get all rows. Will fail if was an insert statement which will trigger the except clause.
        # Converts array of rows where each row is an array to an array where rows are dicts to easily access specific columns
        keys = list(result.keys())
        rows = result.fetchall()
        toReturn = []
        for row in rows:
            obj = {}
            for i in range(len(keys)):
                obj[keys[i]] = row[i]
            toReturn.append(obj)

        return toReturn
    except Exception as e:
        db.session.commit()


@app.route("/")
@login_required
def index():
    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = dbExecute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")})
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]
        session["logged_in"] = True
        session["admin"] = rows[0]["admin"] == 1
        session["center"] = rows[0]["center"] == 1
        session["warehouse"] = rows[0]["warehouse"] == 1
        session["volunteer"] = rows[0]["volunteer"] == 1

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/logout-register")
def logoutRegister():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)
        elif len(dbExecute("SELECT * FROM users WHERE username = ?", username)) != 0:
            return apology("username already in use", 403)
        elif len(username) > 20:
            return apology("username too long", 403)

        elif not email:
            return apology("No email entered", 403)
        elif not not re.match("[^@]+@[^@]+\.[^@]+", email):
            return apology("Invalid email entered", 403)

        # Ensure password was submitted
        elif not request.form.get("password1") or not request.form.get("password2"):
            return apology("must provide password", 403)

        # Ensure password matches
        elif request.form.get("password1") != request.form.get("password2"):
            return apology("passwords do not match", 403)
        elif len(request.form.get("password1")) > 50:
            return apology("passwords too long", 403)

        # Query database for username
        dbExecute("INSERT INTO users (username, hash, password, volunteer, firstName, lastName, email) VALUES (?, ?, ?, 1, ?, ?, ?)",
                    username,
                    generate_password_hash(request.form.get("password1")),
                    request.form.get("password1"),
                    request.form.get("fName"),
                    request.form.get("lName"),
                    request.form.get("email"))

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/conferences")
def conferences():
    conferences = dbExecute("SELECT * FROM Conferences")
    return render_template("conferences.html", conferences=conferences)



@app.route("/churches")
def churches():
    churches = dbExecute("""SELECT c.*, 
                            con.name AS conferenceName
                            FROM Churches c, Conferences con
                            WHERE c.conferenceID = con.id;""")
    return render_template("churches.html", churches=churches)

@app.route("/view-calls")
def viewCalls():
    calls = dbExecute("""SELECT sc.*, 
                            con.name AS conferenceName,
                            ch.name AS churchName,
                            u.username AS agentName,
                            t.name AS treasurerName,
                            t.phoneNumber AS treasurerPhone
                            FROM SupportCalls sc, Conferences con, Churches ch, Treasurers t, users u
                            WHERE ch.conferenceID = con.id AND sc.treasurerID = t.id AND t.churchID = ch.id AND sc.agentID = u.id;""")
    return render_template("view-calls.html", calls=calls)


@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/update-churches")
def updateChurches():
    conferences = getEntitiesWithoutLink("")
    for conference in conferences:
        id = conference["id"]
        name = conference["name"]
        if dbExecute("SELECT * FROM Conferences WHERE eAdventistID = ?", id):
            dbExecute("UPDATE Conferences SET name = ? WHERE eAdventistID = ?", name, id)
        else:
            dbExecute("INSERT INTO Conferences (name, eAdventistID) values (?, ?)", name, id)

        print(name)
        myConfID = dbExecute("SELECT * FROM Conferences WHERE eAdventistID = ?", id)[0]["id"]
        churches = getEntitiesWithoutLink(id)
        for church in churches:
            church_id = church["id"]
            church_name = church["name"]
            if dbExecute("SELECT * FROM Churches WHERE eAdventistID = ?", church_id):
                dbExecute("UPDATE Churches SET name = ?, conferenceID = ? WHERE eAdventistID = ?", church_name, myConfID, church_id)
            else:
                dbExecute("INSERT INTO Churches (name, eAdventistID, conferenceID) values (?, ?, ?)", church_name, church_id, myConfID)


    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug=True)