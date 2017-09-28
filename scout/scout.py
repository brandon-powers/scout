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
        start = pytz.utc.localize(_s).astimezone(pytz.timezone('US/Eastern'))
        end = pytz.utc.localize(_s + timedelta(hours=8)).astimezone(pytz.timezone('US/Eastern'))
        ranges.append((start, end))
        s += timedelta(days=1)


    # for each day
    real_max = timedelta()
    real_s = real_e = None
    for r in ranges:

        # get events for that day
        eventsResult = service.events().list(
                calendarId=calendar_id, timeMin=r[0].isoformat(), timeMax=r[1].isoformat(),
                singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        # get event_ranges for each event on given day
        event_ranges = []
        event_ranges.append((r[0], r[0]))
        for d in events:
            st = d['start']
            if not st.get('dateTime'):
                continue
            st = parse(st['dateTime'])
            en = parse(d['end']['dateTime'])
            event_ranges.append((st, en))
        event_ranges.append((r[1], r[1]))

        # use event_ranges to find max_range for that day
        max_diff = timedelta()
        s = e = None
        i = 1
        while i < len(event_ranges):
            if event_ranges[i-1][1] < event_ranges[i][0]:
                diff = event_ranges[i][0] - event_ranges[i-1][1]
                if max_diff < diff:
                    max_diff = diff
                    s = event_ranges[i-1][1]
                    e = event_ranges[i][0]
            i += 1
        
        if real_max < max_diff:
            real_max = max_diff
            real_s = s
            real_e = e
    return (real_s, real_e)

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

    ids = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            ids.append(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    ids.append('primary')
    start_time = '2017-09-25'
    end_time = '2017-09-29'

    for calendar_id in ids:
        if 'listenfirstmedia' in calendar_id:
            diff = get_most_available_block(service, calendar_id, start_time, end_time)
            print('| NAME: ' + calendar_id + ' \t\t| TIME_BLOCK: ' +
                  diff[0].strftime('%B %d, %Y') + ' on ' + diff[0].strftime('%A') +
                  ' from ' + diff[0].strftime('%H:%M') + ' to ' + diff[1].strftime('%H:%M') +
                  ', which is ' + str(diff[1] - diff[0]) + ' hours')

if __name__ == '__main__':
    main()
