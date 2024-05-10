from datetime import datetime
import os
import re
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is not True:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def sortByID(item):
        return item["id"]

def validateMonthOrGetCurrent(month):
    if month:
        # Define the pattern for MM-YYYY format
        pattern = r"^(0[1-9]|1[0-2])-(\d{4})$"

        # Check if the string matches the pattern
        if not re.match(pattern, month):
            return None
    else:
        # Get current date
        current_date = datetime.now()

        # Format date as MM-YYYY
        month = current_date.strftime("%m-%Y")
    return month