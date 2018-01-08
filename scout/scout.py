#!/usr/bin/env python

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from apiclient import discovery
import datetime
import json
import os.path

class Scout():
    def __init__(self):
        self.client = self.get_client()

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
        page_token = None
        while True:
            calendar_list = self.client.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print calendar_list_entry['summary']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

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

    def plot(self):
        import matplotlib.pyplot as plt; plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt

        objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
        y_pos = np.arange(len(objects))
        performance = [10,8,6,4,2,1]

        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('Usage')
        plt.title('Programming language usage')

        plt.show()

scout = Scout()
scout.get_calendars()
scout.get_events()
scout.plot()
