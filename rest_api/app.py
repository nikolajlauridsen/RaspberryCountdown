"""
Restful API handling database interaction and pomodoro session statistics
Displays an index page for session statistics as well
database functions is taken from: http://flask.pocoo.org/docs/0.12/patterns/sqlite3/#
date: 18/1/17
Some has then been modiefied by: Nikolaj Lauridsen
NOTE: This is NOT a module for TimeBuddy, it's an entity on it's own
that facilitate features in TimeBuddy
"""
import sqlite3
import time
from datetime import datetime
from flask import Flask, jsonify, g, request, render_template, url_for, redirect
from utils import *
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


def get_task_breakdown(session_data):
    """
    Creates a list of task dictionaries
    Dictionaries are structured as so:
    task = {
            "name": "name string",
            "duration": "duration int",
            "sessions": "sessions" int,
            "cycles": "cycles int"
    }
    """
    task_data = query_db("SELECT name FROM tasks")
    breakdown = []

    # Build the task dictionaries
    for task in task_data:
        task = {"name": task["name"],
                "duration": 0,
                "sessions": 0,
                "cycles": 0}
        breakdown.append(task)

    # Add the info
    for session in session_data:
        for task in breakdown:
            if session["task"] == task["name"]:
                task["duration"] += session["duration"]
                task["sessions"] += 1
                task["cycles"] += session["cycles"]
    return breakdown


@TimeBuddy.route('/api/sessions/', methods=['GET', 'POST'])
def sessions():
    """API endpoint for storing/receiving sessions"""
    if request.method == 'GET':
        session_data = query_db('SELECT * from pomodoro')
        return jsonify(results=session_data)

    elif request.method == 'POST':
        query_db('INSERT INTO pomodoro VALUES (?,?,?,?,?)',
                 [request.form['start'],
                  request.form['end'],
                  request.form['duration'],
                  request.form['cycles'],
                  request.form['task']], put=True)
        return """Session saved"""


@TimeBuddy.route('/api/tasks/', methods=['GET', 'POST'])
def tasks_api():

    if request.method == 'GET':
        if request.form['active']:
            tasks_data = query_db('SELECT * FORM tasks WHERE active > 0')
        else:
            tasks_data = query_db('SELECT * FROM tasks')
        return jsonify(results=tasks_data)

    elif request.method == 'POST':
        # All tasks starts off as active
        query_db('INSERT INTO tasks VALUES (?, ?, 1)',
                 [int(time.time()), request.form['name']], put=True)
        return redirect(url_for(endpoint='tasks'))


@TimeBuddy.route('/api/tasks/delete', methods=['POST'])
def deactivate_task():
    query_db("UPDATE tasks SET active=0 WHERE name=(?)",
             [request.form['name']], put=True)
    return redirect(url_for(endpoint='tasks'))


@TimeBuddy.route('/api/sessions/week/', methods=['GET'])
def sessions_week():
    """Weekly endpoint for receiving sessions data from the past 7 days"""
    weekly_sessions = get_last_week()
    return jsonify(results=weekly_sessions)


@TimeBuddy.route('/api/sessions/month/', methods=['GET'])
def sessions_month():
    """Monthly endpoint for receiving sessions data from the past 30 days"""
    monthly_sessions = get_last_month()
    return jsonify(results=monthly_sessions)


@TimeBuddy.route('/index/', methods=['GET'])
def index():
    """Index page to show statistics"""
    # Pack monthly data
    monthly_data = get_last_month()
    m_duration_sum = get_duration_sum(monthly_data)
    try:
        m_sum = m_duration_sum/30
        daily_month = m_duration_sum/len(monthly_data)
    except ZeroDivisionError:
        m_sum = 0
        daily_month = 0

    monthly = {'count': len(monthly_data),
               'average': seconds_to_timestamp(daily_month),
               'daily': seconds_to_timestamp(m_sum),
               'total': seconds_to_timestamp(m_duration_sum)
               }

    # Pack weekly data
    weekly_data = get_last_week()
    w_duration_sum = get_duration_sum(weekly_data)
    try:
        w_avg = w_duration_sum / 7
        daily_week = w_duration_sum/len(weekly_data)
    except ZeroDivisionError:
        w_avg = 0
        daily_week = 0

    weekly = {'count': len(weekly_data),
              'average': seconds_to_timestamp(daily_week),
              'daily': seconds_to_timestamp(w_avg),
              'total': seconds_to_timestamp(w_duration_sum)
              }

    # Pack task data
    task_data = get_task_breakdown(weekly_data)
    for task in task_data:
        task["duration"] = seconds_to_timestamp(int(task["duration"]))

    calendar_id = "https://calendar.google.com/calendar/embed?src=" + \
                  get_calendar_id() + "&ctz=Europe/Copenhagen"

    context = {
        'weekly': weekly,
        'monthly': monthly,
        'tasks': task_data,
        'calendar_id': calendar_id,
        'title': 'TimeBuddy',
        'tagline': 'Statistics'
    }
    return render_template('index.html', data=context)


@TimeBuddy.route('/tasks/', methods=['GET'])
def tasks():
    task_data = query_db('SELECT * FROM tasks WHERE active > 0')
    for task in task_data:
        task["date"] = datetime.utcfromtimestamp(int(task["date"])).strftime('%d-%m-%Y')
    context = {'tasks': task_data,
               'title': 'Tasks',
               'tagline': 'Control panel'}
    return render_template('tasks.html', data=context)

if __name__ == '__main__':
    TimeBuddy.run(host=settings.host,
                  port=settings.port,
                  debug=settings.debug)
