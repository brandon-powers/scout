#!/usr/bin/env python

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from apiclient import discovery
import datetime
import json
import os.path
import argparse

usage = '\n$ scout --list-calendars [-v] [--csv | --json]'
usage += '\n$ scout --discover {<comma-separated-ids> | -g <calendar_group>} [-s <startDateTime> -e <endDateTime>] [--csv | --json]'
parser = argparse.ArgumentParser(
            description='A Google Calendar discovery tool',
            prog='scout', usage=usage,
            epilog='See documentation at https://github.com/brandon-powers/scout for more help.'
        )

list_flags = parser.add_argument_group('list')

list_help = 'output the calendars you have access to'
list_flags.add_argument('-l', '--list-calendars', action='store_true', help=list_help)

verbose_help = 'display the access control role and time zone for each calendar listed'
list_flags.add_argument('-v', '--verbose', action='store_true', help=verbose_help)

discover_flags = parser.add_argument_group('discover')
discover_help = 'discover busyness of a set of calendars'
discover_flags.add_argument('-d', '--discover', action='store_true', help=discover_help)

group_help = 'specify a custom list of calendar ids to discover i.e. a calendar group'
discover_flags.add_argument('-g', '--calendar-group', action='store_true', help=group_help)

start_help = 'specify a start date time i.e. YYYYMMDDTHH:mm:ssZ, 20180108T00:03:00Z'
discover_flags.add_argument('-s', '--start', action='store_true', help=start_help)

end_help = 'specify an end date time i.e. YYYYMMDDTHH:mm:ssZ, 20180108T00:03:00Z'
discover_flags.add_argument('-e', '--end', action='store_true', help=end_help)

output_flags = parser.add_argument_group('output')
output_help_csv = 'output Scout data in csv format'
output_flags.add_argument('-c', '--csv', action='store_true', help=output_help_csv)

output_help_json = 'output Scout data in json format'
output_flags.add_argument('-j', '--json', action='store_true', help=output_help_json)
args = parser.parse_args()

class Scout():
    def __init__(self):
        self.client = self.get_client()
        self.output_format = 'stdout'

    def list_calendars(self, verbose):
        print('stub')

    def discover(self, ids, start, end):
        # calendar_group vs. comma-separated input is dealt
        # with outside of this function, with cli input
        print('stub')

    def set_output_format(output_format):
        try:
            if output_format in ['csv', 'json']:
                self.output_format = output_format
            else:
                raise ValueError
        except ValueError:
            print('invalid output format')

    def get_client(self):
        return discovery.build('calendar', 'v3', credentials=self.get_credentials())

    def get_credentials(self):
        if os.path.isfile('credentials.json'):
            return self.get_existing_credentials()
        else:
            return self.get_new_credentials()

    def get_existing_credentials(self):
        with open('credentials.json', 'r') as f:
            config = json.load(f)
        return Credentials(token=config['token'],
                refresh_token=config['refresh_token'],
                id_token=config['id_token'],
                token_uri=config['token_uri'],
                client_id=config['client_id'],
                client_secret=config['client_secret'],
                scopes=config['scopes'])

    def get_new_credentials(self):
        flow = Flow.from_client_secrets_file(
                'client_secrets.json',
                scopes=['https://www.googleapis.com/auth/calendar'],
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        auth_url, _ = flow.authorization_url(prompt='consent')
        print('Please go to this URL: {}'.format(auth_url))
        code = raw_input('Enter the authorization code: ')
        flow.fetch_token(code=code)
        credentials = flow.credentials
        with open('credentials.json', 'w') as f:
            config = {'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'id_token': credentials.id_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes}
            f.write(json.dumps(config))
        return credentials

    def get_calendars(self):
        calendars = []
        page_token = None
        while True:
            calendar_list = self.client.calendarList().list(pageToken=page_token).execute()
            calendars.append(calendar_list['items'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return calendars

    def get_events_for_calendar(self, calendar_id):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        then = (datetime.datetime.utcnow() - datetime.timedelta(days=14)).isoformat() + 'Z'
        res = []
        page_token = None
        while True:
            events = self.client.events().list(timeMin=then, timeMax=now, singleEvents=True, calendarId=calendar_id, pageToken=page_token, maxResults=100).execute()
            res.append(events['items'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return res

    def get_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        eventsResult = self.client.events().list(
                calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        for event in events:
            from dateutil import parser
            start = parser.parse(event['start']['dateTime'])
            end = parser.parse(event['end']['dateTime'])
            length = end - start
            title = event['summary']
            print(str(title) + ' -- ' + str(length))

# scout = Scout()
# calendars = scout.get_calendars()[0]
# print json.dumps(calendars[0], indent=4)
# for calendar in calendars:
#     events = scout.get_events_for_calendar(calendar['id'])[0]
#     if calendar['id'] == 'brandon.powers@listenfirstmedia.com':
#         print json.dumps(events, indent=4)
#     print(str(len(events)) + 'for -> ' + str(calendar['id']))
