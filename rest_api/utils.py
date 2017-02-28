"""
Various time related functions used in calculating statistics

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


def get_duration_sum(session_data):
    summation = 0

    for session in session_data:
        summation += session["duration"]
    return summation


def seconds_to_timestamp(seconds):
    """Convert seconds into a neatly formatted string.
    Format: HH:MM:SS
    Returns: Timestamp string."""
    hrs = seconds //3600
    mins = (seconds % 3600) // 60
    s = (seconds % 3600) % 60
    return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))


def get_calendar_id():
    """Secret ids and keys is bad juju in source code
    It might not be encrypted, but at least it's not public."""
    try:
        calendarId = open('calendar_id.txt').readlines()
        return calendarId[0].strip('\n')   # Returns the first line containing
                                           # the key, minus the next line sign
    except FileNotFoundError:
        return ""
