from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2
import os
import json
import datetime

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'auth.json'
APPLICATION_NAME = 'scout'

def get_largest_diff(service, ids, start_time, end_time):
    if len(ids) <= 0:
        return None
    elif len(ids) == 1:
        # return most available block given 1 person(s) schedule

        # get events
        eventsResult = service.events().list(
                calendarId=ids[0], timeMin=start_time, timeMax=end_time, 
                singleEvents=True, orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        # naive solution: for each event, get max diff of it to every other event, then compare m max diffs?

        return events
    else:
        # return most available block given n person(s) schedule
        return None

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

    ids = ['primary']
    start_time = '2017-09-25T13:00:00Z'
    end_time = '2017-09-26T21:00:00Z'

    diff = get_largest_diff(service, ids, start_time, end_time)
    for d in diff:
        print(json.dumps(d, indent=4))

if __name__ == '__main__':
    main()
