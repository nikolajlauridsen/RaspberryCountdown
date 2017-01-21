"""
Restful API handling database interaction and pomodoro session statistics
Displays an index page for session statistics as well
database functions is taken from: http://flask.pocoo.org/docs/0.12/patterns/sqlite3/#
date: 18/1/17
Some has then been modiefied by: Nikolaj Lauridsen
"""
import sqlite3
from flask import Flask, jsonify, g, request, render_template
from time_functions import *
import settings

DATABASE = 'database.db'

TimeBuddy = Flask(__name__)


def init_db():
    """Initializes the database, creating all tables"""
    with TimeBuddy.app_context():
        db = get_db()
        with TimeBuddy.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def make_dicts(cursor, row):
    """Converts database queries to dictionaries"""
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    """Opens database connection and returns database object"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


@TimeBuddy.teardown_appcontext
def close_connection(exception):
    """Closes database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False, put=False):
    """Query the database, if put is False the function will fetch data
    if put is true it'll insert data"""
    db = get_db()

    try:
        cur = db.execute(query, args)
    except sqlite3.OperationalError:
        init_db()
        cur = db.execute(query, args)

    if put:
        db.commit()
        cur.close()
        return None
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def get_last_week():
    """Returns session data from the past 7 days"""
    query = "SELECT * FROM pomodoro" \
            " WHERE datetime(startTime, 'unixepoch') >= DATE('now', '-7 days')"
    weekly_sessions = query_db(query)
    return weekly_sessions


def get_last_month():
    """Returns session data from the past 30 days"""
    query = "SELECT * FROM pomodoro " \
            "WHERE datetime(startTime, 'unixepoch') >= DATE('now', '-1 month')"
    monthly_sessions = query_db(query)
    return monthly_sessions


@TimeBuddy.route('/api/sessions/', methods=['GET', 'POST'])
def sessions():
    """API endpoint for storing/receiving sessions"""
    if request.method == 'GET':
        session_data = query_db('SELECT * from pomodoro')
        return jsonify(session_data)

    elif request.method == 'POST':
        query_db('INSERT INTO pomodoro VALUES (?,?,?,?)',
                 [request.form['start'],
                  request.form['end'],
                  request.form['duration'],
                  request.form['cycles']], put=True)
        return """Session saved"""


@TimeBuddy.route('/api/sessions/week/', methods=['GET'])
def sessions_week():
    """Weekly endpoint for receiving sessions data from the past 7 days"""
    weekly_sessions = get_last_week()
    return jsonify(weekly_sessions)


@TimeBuddy.route('/api/sessions/month/', methods=['GET'])
def sessions_month():
    """Monthly endpoint for receiving sessions data from the past 30 days"""
    monthly_sessions = get_last_month()
    return jsonify(monthly_sessions)


@TimeBuddy.route('/index', methods=['GET'])
def index():
    """Index page to show statistics"""
    # Pack monthly data
    monthly_data = get_last_month()
    monthly = {'count': len(monthly_data),
               'average': seconds_to_timestamp(get_avg_duration(monthly_data))
               }

    # Pack weekly data
    weekly_data = get_last_week()
    weekly = {'count': len(weekly_data),
              'average': seconds_to_timestamp(get_avg_duration(weekly_data))
              }

    context = {
        'weekly': weekly,
        'monthly': monthly
    }
    return render_template('index.html', data=context)

if __name__ == '__main__':
    TimeBuddy.run(host=settings.host,
                  port=settings.port,
                  debug=settings.debug)
