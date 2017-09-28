from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2
import os
import json
import pytz
from dateutil.parser import parse
from datetime import datetime, timedelta

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'auth.json'
APPLICATION_NAME = 'scout'

def get_most_available_block(service, calendar_id, start_time, end_time):
    # break up date range to array of start/end date ranges for each day
    s = parse(start_time)
    e = parse(end_time)
    ranges = []
    while s.day <= e.day:
        _s = datetime(s.year, s.month, s.day, 13, 0, 0)
        start = pytz.utc.localize(_s).isoformat()
        end = pytz.utc.localize(_s + timedelta(hours=8)).isoformat()
        ranges.append((start, end))
        s += timedelta(days=1)

    real_max = timedelta()

    # for each day
    for r in ranges:

        # get events for that day
        eventsResult = service.events().list(
                calendarId=calendar_id, timeMin=r[0], timeMax=r[1], 
                singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        print('************')

        # get event_ranges for each event on given day
        event_ranges = []
        for d in events:
            start = d['start']
            if not start.get('dateTime'):
                continue
            start = parse(start['dateTime'])
            end = parse(d['end']['dateTime'])
            event_ranges.append((start, end))

        # use event_ranges to find max_range for that day
        max_diff = timedelta()
        for v in event_ranges:
            print(v[0].isoformat() + ' --- ' + v[1].isoformat())
            diff = v[1] - v[0]
            if max_diff < diff:
                max_diff = diff
        print('MAX: ' + str(max_diff))

        if real_max < max_diff:
            real_max = max_diff

        print('************')

    print('FOR ALL DAYS: ' + str(real_max))

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
    start_time = '2017-09-10'
    end_time = '2017-09-26'

    diff = get_most_available_block(service, calendar_id, start_time, end_time)

if __name__ == '__main__':
    main()
