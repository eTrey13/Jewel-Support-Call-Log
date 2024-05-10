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

from helpers import *

from updateChurches import getEntitiesWithoutLink
from db_helpers import *

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
db.init_app(app)


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
    #show info of one conference
    conferenceID = request.args.get('conferenceID')
    if conferenceID:
        conference = dbExecute("""SELECT name AS conferenceName,
                            id AS conferenceID
                            FROM Conferences
                            WHERE id = ?;""", conferenceID)
        if not conference:
            return redirect("/conferences")
        conference = conference[0]


        month = validateMonthOrGetCurrent(request.args.get('month'))
        if not month:
            return redirect("/dashboard")
        
        calls = getSupportCallsWithOptionalFilters("conference", conferenceID, month=month)
        sumTotalTime = getSupportCallsTotalTimeWithOptionalFilters("conference", conferenceID, month=month)
    

        return render_template("conference-info.html", conference=conference, calls=calls, month=month, sumTotalTime=sumTotalTime, currentYear=datetime.now().year)

    
    conferences = dbExecute("SELECT * FROM Conferences")
    return render_template("conferences.html", conferences=conferences)

@app.route("/churches")
def churches():
    #show info of one church
    churchID = request.args.get('churchID')
    if churchID:
        church = dbExecute("""SELECT con.name AS conferenceName,
                            ch.name AS churchName,
                            ch.id AS churchID,
                            con.id AS conferenceID
                            FROM Conferences con, Churches ch
                            WHERE ch.conferenceID = con.id AND ch.id = ?;""", churchID)
        if not church:
            return redirect("/churches")
        church = church[0]

        treasurers = dbExecute("SELECT * FROM Treasurers WHERE churchID = ?", churchID)

        calls = getSupportCallsWithOptionalFilters("church", churchID)

        return render_template("church-info.html", church=church, treasurers=treasurers, calls=calls)

    #show all churches
    churches = dbExecute("""SELECT c.*, 
                            con.name AS conferenceName
                            FROM Churches c, Conferences con
                            WHERE c.conferenceID = con.id;""")
    return render_template("churches.html", churches=churches)

@app.route("/view-calls", methods=["GET", "POST"])
def viewCalls():
    if request.method == "POST":
        churchID = getChurchIdFromChurchAndConferenceName(request.form.get("conference"), request.form.get("church"))
        if churchID:
            return redirect(f"/view-calls?churchID={churchID}")
        conferenceID = getConferenceIdFromConferenceName(request.form.get("conference"))
        if conferenceID:
            return redirect(f"/view-calls?conferenceID={conferenceID}")
    
    calls = []
    churchID = request.args.get('churchID')
    conferenceID = request.args.get('conferenceID')
    selection = {}
    if churchID:
        calls = getSupportCallsWithOptionalFilters("church", churchID)
        church = dbExecute("""SELECT con.name AS conferenceName,
                            ch.name AS churchName,
                            ch.id AS churchID,
                            con.id AS conferenceID
                            FROM Conferences con, Churches ch
                            WHERE ch.conferenceID = con.id AND ch.id = ?;""", churchID)
        if not church:
            return redirect("/view-calls")
        selection = church[0]
    elif conferenceID:
        calls = getSupportCallsWithOptionalFilters("conference", conferenceID)
        conference = dbExecute("""SELECT name AS conferenceName,
                                id AS conferenceID
                                FROM Conferences
                                WHERE id = ?;""", conferenceID)
        if not conference:
            return redirect("/view-calls")
        selection = conference[0]
    else:
        calls = dbExecute("""SELECT sc.*, 
                            con.name AS conferenceName,
                            ch.name AS churchName,
                            u.username AS agentName,
                            t.name AS treasurerName,
                            t.phoneNumber AS treasurerPhone,
                            ch.id AS churchID
                            FROM SupportCalls sc, Conferences con, Churches ch, Treasurers t, users u
                            WHERE ch.conferenceID = con.id AND sc.treasurerID = t.id AND t.churchID = ch.id AND sc.agentID = u.id;""")
    calls.sort(key=sortByID, reverse=True)


    conferences = getObjectOfConferencesEachWithArrayOfItsChurches()
    return render_template("view-calls.html", calls=calls, selection=selection, conferences=conferences)

@app.route("/new-call", methods=["GET", "POST"])
#@login_required TODO
def newCall():
    if request.method == "POST" and not request.form.get("selectedTreasurer"):
        treasurer = request.form.get("treasurer")
        if treasurer and not request.form.get("newTreasurer"):
            if dbExecute("SELECT * FROM Treasurers WHERE id = ?", treasurer):
                return redirect(f"/new-call?treasurer={treasurer}")
            else:
                return apology("Bad Request - Treasurer index not found", 400)
        else:
            name = request.form.get("name")
            phone = request.form.get("phone")
            email = request.form.get("email")
            if name and (phone or email):
                churchID = getChurchIdFromChurchAndConferenceName(request.form.get("conference"), request.form.get("church"))

                if not churchID:
                    return apology("Bad Request - Church not found", 400)

                otherInfo = request.form.get("otherContactInfo")
                dbExecute("INSERT INTO Treasurers (churchID, name, phoneNumber, email, otherContactInfo) VALUES (?, ?, ?, ?, ?)", churchID, name, phone, email, otherInfo)

                treasurerID = dbExecute("SELECT id FROM Treasurers WHERE churchID = ? AND name = ? AND phoneNumber = ? AND email = ? AND otherContactInfo = ?", churchID, name, phone, email, otherInfo)[0]["id"]

                return redirect(f"/new-call?treasurer={treasurerID}")
            
            return apology("Failed")
    else:        
        #selected a treasurer, send form to fill notes
        if request.args.get('treasurer'):
            treasurerID = request.args.get('treasurer')
            if not dbExecute("SELECT * FROM Treasurers WHERE id = ?", treasurerID):
                return redirect("/new-call")
            treasurer = dbExecute("""SELECT t.*, 
                                con.name AS conferenceName,
                                c.name AS churchName
                                FROM Churches c, Conferences con, Treasurers t
                                WHERE c.conferenceID = con.id AND t.churchID = c.id AND t.id = ?;""", treasurerID)
            return render_template("call-data.html", treasurer=treasurer[0])
        
        #went back, load with same selection
        selectedTreasurer = None
        if request.form.get("selectedTreasurer"):
            selectedTreasurer = dbExecute("""SELECT t.*, 
                                    con.name AS conferenceName,
                                    c.name AS churchName
                                    FROM Churches c, Conferences con, Treasurers t
                                    WHERE c.conferenceID = con.id AND t.churchID = c.id AND t.id = ?;""", request.form.get("selectedTreasurer"))[0]
        
        conferences = getObjectOfConferencesEachWithArrayOfItsChurches()

        treasurersArray = dbExecute("""SELECT t.*, 
                                con.name AS conferenceName,
                                c.name AS churchName
                                FROM Churches c, Conferences con, Treasurers t
                                WHERE c.conferenceID = con.id AND t.churchID = c.id;""")
        
        treasurers = {}

        # Iterate over the objects array
        for treasurer in treasurersArray:
            conf_church_name = treasurer['conferenceName'] + treasurer['churchName']
            
            # If the conference ID is not already a key in the dictionary, add it with an empty array
            if conf_church_name not in treasurers:
                treasurers[conf_church_name] = []
            
            # Append the object to the array corresponding to its conference ID
            treasurers[conf_church_name].append(treasurer)
        
        return render_template("new-call.html", conferences = conferences, treasurers=treasurers, treasurer=selectedTreasurer)

@app.route("/save-new-ticket", methods=["POST"])
#@login_required TODO
def saveNewTicket():
    treasurerID = request.form.get("treasurer")
    treasurer = dbExecute("""SELECT *
                            FROM Treasurers
                            WHERE id = ?;""", treasurerID)[0]
        
    if not treasurer:
        return apology("Bad Request - Treasurer index not found", 400)
    
    #if "user_id" not in session:
        #return apology("Bad Request - Agent index not found (not logged in)", 400)
    agentID = 1#session["user_id"] TODO

    startTime = request.form.get("startTime")
    endTime = request.form.get("endTime")
    notes = request.form.get("message")
    current_date = datetime.now().strftime("%d-%m-%Y")

    #TODO timezones?

    #validate time input
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not (re.match(pattern, startTime) and re.match(pattern, endTime)):
        return apology("Bad Request - Invalid time", 400)
    # Split the time strings into hours and minutes
    hours1, minutes1 = map(int, startTime.split(":"))
    hours2, minutes2 = map(int, endTime.split(":"))
    if hours1 > hours2:
        hours2 += 24
    # Calculate the total minutes for each time
    total_minutes1 = hours1 * 60 + minutes1
    total_minutes2 = hours2 * 60 + minutes2
    # Calculate the difference in minutes
    totalTime = total_minutes2 - total_minutes1


    dbExecute("INSERT INTO SupportCalls (treasurerID, agentID, startTime, endTime, notes, date, totalTime) VALUES (?, ?, ?, ? ,?, ?, ?)", treasurerID, agentID, startTime, endTime, notes, current_date, totalTime)

    #TODO link to ?churchID=x and show all tickets for that church including new one
    #return redirect("/churches")
    return redirect(f"/view-calls?churchID={treasurer['churchID']}")

@app.route("/dashboard")
def dashboard():
    agentID = 1#session["user_id"] TODO
    agent = dbExecute("SELECT * FROM Users WHERE id = ?;", agentID)[0]

    month = validateMonthOrGetCurrent(request.args.get('month'))
    if not month:
        return redirect("/dashboard")
        
    calls = getSupportCallsWithOptionalFilters("agent", agentID, month=month)
    sumTotalTime = getSupportCallsTotalTimeWithOptionalFilters("agent", agentID, month=month)
    
    return render_template("dashboard.html", agent=agent, calls=calls, month=month, sumTotalTime=sumTotalTime, currentYear=datetime.now().year)





@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/update-churches")
@admin_required
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