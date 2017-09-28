from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2
import os
import json
from datetime import datetime, timedelta

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'auth.json'
APPLICATION_NAME = 'scout'

def get_most_available_block(service, calendar_id, start_time, end_time):
    # break up date range to array of start/end date ranges for each day
    s = datetime.strptime(start_time, '%Y-%m-%d')
    e = datetime.strptime(end_time, '%Y-%m-%d')
    ranges = []
    while s.day <= e.day:
        _s = datetime(s.year, s.month, s.day, 13, 0, 0)
        start = _s.strftime('%Y-%m-%dT%H:%M:%SZ')
        end = (_s + timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%SZ')
        ranges.append((start, end))
        s += timedelta(days=1)

    # get events
    for r in ranges:
        eventsResult = service.events().list(
                calendarId=calendar_id, timeMin=r[0], timeMax=r[1], 
                singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        print('************')
        for d in events:
            print(json.dumps(d, indent=4))
        print('************')

    return events

def get_credentials():
    auth_dir = os.path.abspath('config')
    path = os.path.join(auth_dir, CLIENT_SECRET_FILE)
    store = Storage(path)
    credentials = store.get()

    # TODO: bug here
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + path)

    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar_id = 'primary'
    start_time = '2017-09-20'
    end_time = '2017-09-26'

    diff = get_most_available_block(service, calendar_id, start_time, end_time)

if __name__ == '__main__':
    main()
