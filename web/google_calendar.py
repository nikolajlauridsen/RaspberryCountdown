import httplib2
import datetime
import argparse
import os

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


class EventCreator:
    """Class for creating events on google calendar"""

    def __init__(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def create_event(self, summary, start, end):
        # TODO: consider timezones
        start = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%S')
        print(start + '\n' + end)
        timezone = 'Europe/Berlin'

        event = {
            'summary': summary,
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
        self.service.events().insert(calendarId='primary', body=event).execute()
