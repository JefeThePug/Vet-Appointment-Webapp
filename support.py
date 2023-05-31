import sqlite3
from flask import redirect, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def dict_factory(cursor, row):
    """Convert result of sqlite3 command into a dictionary"""
    d = {}
    for i, column in enumerate(cursor.description):
        d[column[0]] = row[i]
    return d


def db_input(prompt, args=None):
    """ Configure SQLite3 database and run command """
    conn = sqlite3.connect('reservations.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    if args:
        c.execute(prompt, args)
    else:
        c.execute(prompt)
    conn.commit()
    results = c.fetchall()
    conn.close()
    return list(results)
