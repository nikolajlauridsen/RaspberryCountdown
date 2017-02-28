"""
  A lot of the code in this file is taken from the google calendar api example
  link to example: https://developers.google.com/google-apps/calendar/quickstart/python
  The code has then been edited by me Nikolaj (28/2/17)
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

import httplib2
import datetime
import argparse
import os
import socket

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Raspberry LCD pomodoro timer'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'g_calendar.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_calendar_id():
    """Secret ids and keys is bad juju in source code
    It might not be encrypted, but at least it's not public."""
    try:
        calendarId = open('calendar_id.txt').readlines()
        return calendarId[0].strip('\n')   # Returns the first line containing
                                           # the key, minus the next line sign
    except FileNotFoundError:
        print('calendar_id.txt not found, saving to primary calendar')
        return 'primary'


class EventCreator:
    """Class for creating events on google calendar"""

    def __init__(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def create_event(self, summary, start, end, description=' '):
        # TODO: consider timezones
        start = datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%S')
        print(start + '\n' + end)
        timezone = 'Europe/Copenhagen'

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': timezone},
            'end': {
                'dateTime': end,
                'timeZone': timezone},
            'reminders': {
                'useDefault': False
            }
        }
        try:
            self.service.events().insert(calendarId=get_calendar_id(), body=event).execute()
        except socket.gaierror:
            print("Network error")
