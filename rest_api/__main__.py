"""
Restful API handling database interaction and pomodoro session statistics
Displays an index page for session statistics as well
database functions is taken from: http://flask.pocoo.org/docs/0.12/patterns/sqlite3/#
date: 18/1/17
Some has then been modiefied by: Nikolaj Lauridsen
NOTE: This is NOT a module for TimeBuddy, it's an entity on it's own
that facilitate features in TimeBuddy

  Copyright (C) 2017  Nikolaj Lauridsen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3
import time
from datetime import datetime
from flask import Flask, jsonify, g, request, render_template, url_for,\
    redirect, send_from_directory
from utils import *
import settings
import os

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


@TimeBuddy.route('/favicon.ico')
def favicon():
    """This is needed for some old browsers"""
    return send_from_directory(os.path.join(TimeBuddy.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


def query_db(query, args=(), one=False, commit=False):
    """Query the database, if commit is False the function will fetch data
    if commit is true it'll insert data"""
    db = get_db()

    try:
        cur = db.execute(query, args)
    except sqlite3.OperationalError:
        init_db()
        cur = db.execute(query, args)

    if commit:
        db.commit()
        cur.close()
        return None
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def get_last_day():
    query = "SELECT * FROM pomodoro" \
            " WHERE DATETIME(startTime, 'unixepoch') >= DATE('now', '-1 days')"
    daily_sessions = query_db(query)
    return daily_sessions


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


def get_activity_breakdown(activity_data, span=7):
    activity_names = query_db("SELECT name from activities")
    breakdown = []

    for activity in activity_names:
        activity = {'name': activity["name"],
                    'duration': 0,
                    'count': 0}
        breakdown.append(activity)

    activity_data = activity_data

    for datapoint in activity_data:
        for activity in breakdown:
            if datapoint['activity'] == activity['name']:
                activity['duration'] += datapoint['duration']
                activity['count'] += 1
                activity['avgdaily'] = seconds_to_timestamp(
                    (activity['duration'] / span))
    formatted_data = []
    duration_sum = 0
    total_count = 0
    for activity in breakdown:
        if activity['count'] > 0:
            try:
                activity['avgduration'] = activity['duration']/activity['count']
            except ZeroDivisionError:
                activity['avgduration'] = 0
            activity['durationString'] = seconds_to_timestamp(activity['duration'])
            activity['avgduration'] = seconds_to_timestamp(activity['avgduration'])
            duration_sum += activity['duration']
            total_count += activity['count']
            formatted_data.append(activity)
        else:
            pass

    if len(formatted_data) > 0:
        try:
            avg_duration = seconds_to_timestamp(duration_sum/total_count)
        except ZeroDivisionError:
            avg_duration = seconds_to_timestamp(0)
        context = {
            'total_count': total_count,
            'duration_sum': seconds_to_timestamp(duration_sum),
            'avg_duration': avg_duration,
            'breakdown': formatted_data
        }
        return context
    else:
        return {}


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

    # Tasks with no sessions are uninteresting and needs to be filtered out
    # deleting a dictionary from a list is kind of a hassle though,
    # so the list is copied instead.
    formatted_breakdown = []
    for task in breakdown:
        # Don't copy task if it has no sessions
        if task["sessions"] > 0:
            try:
                # Now that we're looping through the tasks we might as well
                # calculate some averages as well
                task['cyclesprses'] = round(task['cycles']/task['sessions'], 2)
                task['avgduration'] = task['duration']/task['sessions']
            except ZeroDivisionError:  # Belt and suspenders is the new black.
                task['cyclesprses'] = 0
                task['avgduration'] = 0
            # Let's convert seconds to timestamps now that we're at it.
            task['durationString'] = seconds_to_timestamp(int(task["duration"]))
            task['avgduration'] = seconds_to_timestamp(int(task['avgduration']))
            # Append the new task dict to formatted_breakdown
            formatted_breakdown.append(task)
        else:
            # Skip tasks with no sessions
            pass
    # Return the formatted breakdown
    return formatted_breakdown


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
                  request.form['task']], commit=True)
        return """Session saved"""


@TimeBuddy.route('/api/tasks/', methods=['GET', 'POST'])
def tasks_api():
    """Get all tasks as json or insert a new task"""
    if request.method == 'GET':
        if request.form['active'] == "1":
            tasks_data = query_db('SELECT * FROM tasks WHERE active > 0')
        elif request.form['active'] == "0":
            tasks_data = query_db('SELECT * FROM tasks WHERE active < 1')
        else:
            tasks_data = query_db('SELECT * FROM tasks')
        return jsonify(results=tasks_data)

    elif request.method == 'POST':
        # All tasks starts off as active
        query_db('INSERT INTO tasks VALUES (?, ?, 1)',
                 [int(time.time()), request.form['name']], commit=True)
        return redirect(url_for(endpoint='tasks'))


@TimeBuddy.route('/api/tasks/toggle', methods=['POST'])
def toggle_task():
    """Toggle the active status of a task"""
    query_db("UPDATE tasks SET active=(?) WHERE name=(?)",
             [request.form['status'], request.form['name']], commit=True)
    return redirect(url_for(endpoint='tasks'))


@TimeBuddy.route('/api/tasks/delete', methods=['POST'])
def delete_task():
    """Deletes a task and all sessions associated with it"""
    # Only delete a task if it's inactive
    task = query_db("SELECT active FROM tasks WHERE name=(?)",
                    [request.form['name']], one=True)
    if task['active'] == 0:
        # First delete all the session data belonging to the task
        query_db("DELETE FROM pomodoro WHERE task=(?)",
                 [request.form['name']], commit=True),
        # Then delete the task itself
        query_db("DELETE FROM tasks WHERE name=(?)",
                 [request.form['name']], commit=True)
        # Redirect the user back
        return redirect(url_for(endpoint='tasks'))
    else:
        return """Task still active, please deactivate it first"""


@TimeBuddy.route('/api/activities/', methods=['GET', 'POST'])
def activities_api():
    """Endpoint for creating activities, basically the same as tasks"""
    if request.method == 'GET':
        if request.form['active'] == "1":
            activities_data = query_db("SELECT * FROM activities WHERE active > 0")
        elif request.form['active'] == "0":
            activities_data = query_db("SELECT * FROM activities WHERE active < 1")
        else:
            activities_data = query_db("SELECT * FROM activities")
        return jsonify(results=activities_data)

    elif request.method == 'POST':
        query_db("INSERT INTO activities VALUES (?, ?, 1)",
                 [int(time.time()), request.form['name']], commit=True)
        return redirect(url_for(endpoint='activities'))


@TimeBuddy.route('/api/activities/toggle', methods=['POST'])
def toggle_activity():
    query_db("UPDATE activities SET active=(?) WHERE name=(?)",
             [request.form['status'], request.form['name']], commit=True)
    return redirect(url_for(endpoint='activities'))


@TimeBuddy.route('/api/activities/delete', methods=['POST'])
def delete_activity():
    """Deletes a activity and all sessions associated with it"""
    # Only delete a activity if it's inactive
    activity = query_db("SELECT active FROM activities WHERE name=(?)",
                        [request.form['name']], one=True)
    if activity['active'] == 0:
        # First delete all the session data belonging to the activity
        query_db("DELETE FROM timetrack WHERE activity=(?)",
                 [request.form['name']], commit=True),
        # Then delete the activity itself
        query_db("DELETE FROM activities WHERE name=(?)",
                 [request.form['name']], commit=True)
        # Redirect the user back
        return redirect(url_for(endpoint='activities'))
    else:
        return """Activity still active, please deactivate it first"""


@TimeBuddy.route('/api/timetrack/', methods=['GET', 'POST'])
def timetrack():
    if request.method == 'GET':
        activity_data = query_db('SELECT * FROM timetrack')
        return jsonify(results=activity_data)

    elif request.method == 'POST':
        query_db('INSERT INTO timetrack VALUES (?, ? ,? ,? )',
                 [request.form['start'],
                  request.form['end'],
                  request.form['duration'],
                  request.form['activity']], commit=True)
        return """Activitytrack saved"""


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
    # Monthly tasks will be added to context by itself
    monthly_tasks = get_task_breakdown(monthly_data)
    # The sum of all the sessions duration
    m_duration_sum = get_duration_sum(monthly_data)

    # Calculate total cycle count based off monthly tasks
    month_cycle_count = 0
    for task in monthly_tasks:
        month_cycle_count += task['cycles']
    # Monthly session count is equal to the amount of data in monthly data
    # since 1 session = 1 data point
    month_sesh_count = len(monthly_data)

    try:
        # Try to calculate averages
        # Average daily time spent pomodoroing
        month_avg_daily = m_duration_sum/30
        # Average session duration
        duration_average_month = m_duration_sum/len(monthly_data)
        # Average amount of work cycles per sessions
        avg_monthly_cycles = round(month_cycle_count/month_sesh_count, 2)
    except ZeroDivisionError:
        # Don't blow up the universe
        avg_monthly_cycles = 0
        month_avg_daily = 0
        duration_average_month = 0

    # Pack it all neat like into its very own dictionary
    # Except for monthly_task since it's added by it's own
    monthly = {'count': month_sesh_count,
               'average': seconds_to_timestamp(duration_average_month),
               'daily': seconds_to_timestamp(month_avg_daily),
               'total': seconds_to_timestamp(m_duration_sum),
               'totalcycles': month_cycle_count,
               'cyclesprsession': avg_monthly_cycles
               }

    # Pack weekly data
    # This follows exactly the same procedure as monthly
    # I should really have made a function for this
    weekly_data = get_last_week()
    weekly_tasks = get_task_breakdown(weekly_data)
    w_duration_sum = get_duration_sum(weekly_data)

    weekly_cycles = 0
    for task in weekly_tasks:
        weekly_cycles += task['cycles']
    weekly_sessions = len(weekly_data)

    try:
        w_avg_daily = w_duration_sum / 7
        duration_average_week = w_duration_sum/weekly_sessions
        avg_weekly_cycles = round(weekly_cycles / weekly_sessions, 2)
    except ZeroDivisionError:
        w_avg_daily = 0
        duration_average_week = 0
        avg_weekly_cycles = 0

    weekly = {'count': weekly_sessions,
              'average': seconds_to_timestamp(duration_average_week),
              'daily': seconds_to_timestamp(w_avg_daily),
              'total': seconds_to_timestamp(w_duration_sum),
              'totalcycles': weekly_cycles,
              'cyclesprsession': avg_weekly_cycles
              }

    # Pack daily data
    daily_data = get_last_day()
    daily_tasks = get_task_breakdown(daily_data)

    d_duration_sum = get_duration_sum(daily_data)

    daily_cycles = 0
    for task in daily_tasks:
        daily_cycles += 1
    daily_sessions = len(daily_data)

    try:
        duration_avg_day = d_duration_sum/daily_sessions
        avg_cycles_day = round(daily_cycles / daily_sessions, 2)
    except ZeroDivisionError:
        duration_avg_day = 0
        avg_cycles_day = 0

    # Create daily dictionary
    daily = {'count': daily_sessions,
             'average': seconds_to_timestamp(duration_avg_day),
             'total': seconds_to_timestamp(d_duration_sum),
             'totalcycles': daily_cycles,
             'cyclesprsession': avg_cycles_day
             }

    # Generate the calendar ID based upon the link in calendar_id.txt
    calendar_id = "https://calendar.google.com/calendar/embed?src=" + \
                  get_calendar_id() + "&ctz=Europe/Copenhagen"


    query = "SELECT * FROM timetrack" \
            " WHERE datetime(startTime, 'unixepoch') >= DATE('now', '-30 days')"
    monthly_activities = query_db(query)
    monthly_activities = get_activity_breakdown(monthly_activities, span=30)

    query = "SELECT * FROM timetrack" \
            " WHERE datetime(startTime, 'unixepoch') >= DATE('now', '-7 days')"
    weekly_activities = query_db(query)
    weekly_activities = get_activity_breakdown(weekly_activities, span=7)

    query = "SELECT * from timetrack" \
            " WHERE DATETIME(startTime, 'unixepoch') >= DATE('now', '-1 days')"
    daily_activities = query_db(query)
    daily_activities = get_activity_breakdown(daily_activities, span=1)

    # Put the data into context
    context = {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'daily_tasks': daily_tasks,
        'weekly_tasks': weekly_tasks,
        'monthly_tasks': monthly_tasks,
        'monthly_activities': monthly_activities,
        'weekly_activities': weekly_activities,
        'daily_activities': daily_activities,
        'calendar_id': calendar_id,
        'title': 'TimeBuddy',
        'tagline': 'Statistics'
    }
    return render_template('index.html', data=context)


@TimeBuddy.route('/tasks/', methods=['GET'])
def tasks():
    """Task page for activating/deactivating/deleting tasks"""
    active_tasks = query_db('SELECT * FROM tasks WHERE active > 0')
    inactive_tasks = query_db('SELECT * FROM tasks WHERE active < 1')

    for task in active_tasks:
        task["date"] = datetime.utcfromtimestamp(int(task["date"])).strftime(
            '%d-%m-%Y')

    for task in inactive_tasks:
        task["date"] = datetime.utcfromtimestamp(int(task["date"])).strftime(
            '%d-%m-%Y')

    context = {'active_tasks': active_tasks,
               'inactive_tasks': inactive_tasks,
               'title': 'Pomodoro',
               'tagline': 'Task Control Panel'}

    return render_template('tasks.html', data=context)


@TimeBuddy.route('/activities/', methods=['GET'])
def activities():
    active_activities = query_db('SELECT * FROM activities WHERE active > 0')
    inactive_activities = query_db('SELECT * FROM activities WHERE active < 1')

    for activity in active_activities:
        activity["date"] = datetime.utcfromtimestamp(int(activity["date"])).strftime(
            '%d-%m-%Y')

    for activity in inactive_activities:
        activity["date"] = datetime.utcfromtimestamp(int(activity["date"])).strftime(
            '%d-%m-%Y')

    context = {'active_tasks': active_activities,
               'inactive_tasks': inactive_activities,
               'title': 'TimeTracker',
               'tagline': 'Activity Control Panel'}

    return render_template('activities.html', data=context)

if __name__ == '__main__':
    TimeBuddy.run(host=settings.host,
                  port=settings.port,
                  debug=settings.debug)
