#!/usr/bin/env python

"""
TODO:
    4. write tests for current functionality + TDD for any new code
    5. improve docs using Python convention (need to read PEP docs)
    6. improve/learn more about Python / pip package structure
    7. flesh out some new features/functionality for Scout & it's design, scope, & goals

Current functionality:
    1. workplace discovery:
        constraints: START (9AM), END (5PM)
        args: startDate --> endDate
        return: [name, startTime --> endTime] of most available in the given date range, for each calendar the root user has at least freeBusy access

    2. individual discovery:
        same as workplace discovery, but returns a single time range for the root user
        return: name, startTime --> endTime
"""

from apiclient import discovery

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from dateutil.parser import parse
from datetime import datetime, timedelta

import httplib2
import os
import json
import pytz
import argparse

parser = argparse.ArgumentParser(
            description='A Google Calendar discovery tool',
            prog='scout', usage='%(prog)s [-w | -i]',
            epilog='See documentation at https://github.com/brandon-powers/scout for more help.'
        )
discovery_flags = parser.add_argument_group('discovery')
w_help = 'output the most available block of time for each calendar you' \
         'have access to, given a date range & daily hour range'
discovery_flags.add_argument('-w', '--workplace_discovery', action='store_true', help=w_help)
i_help = 'output the most available block of time for your primary calendar' \
         ', given a date range & daily hour range'
discovery_flags.add_argument('-i', '--individual_discovery', action='store_true', help=i_help)
args = parser.parse_args()

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'config/auth.json'
APPLICATION_NAME = 'scout'

class Scout():
    def __init__(self):
        self.service = self.auth()

    def auth(self):
        """
        Example docstring -->

        Runs through the OAuth flow

        :param self [Object] instance of object
        :return [boolean] success or failure
        """
        # flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        # home_dir = os.path.expanduser('~')
        # credential_dir = os.path.join(home_dir, '.credentials')
        # if not os.path.exists(credential_dir):
        #     os.makedirs(credential_dir)

        credential_dir = os.path.abspath('config')
        credential_path = os.path.join(credential_dir, 'auth_token.json')
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store) #, flags)
            print('Storing credentials to ' + credential_path)

        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        return service

    def workplace_discovery(self, date_range, hour_range):
        ids = []
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                ids.append(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        ids.append('primary')
        start_date = date_range[0]
        end_date = date_range[1]

        for calendar_id in ids:
            if 'listenfirstmedia' in calendar_id:
                diff = self.get_most_available_block(calendar_id, start_date, end_date)
                print('| NAME: ' + calendar_id + ' \t\t| TIME_BLOCK: ' +
                      diff[0].strftime('%B %d, %Y') + ' on ' + diff[0].strftime('%A') +
                      ' from ' + diff[0].strftime('%H:%M') + ' to ' + diff[1].strftime('%H:%M') +
                      ', which is ' + str(diff[1] - diff[0]) + ' hours')

    def individual_discovery(self, date_range, hour_range):
        print('individual_discovery')

    def get_most_available_block(self, calendar_id, start_date, end_date):
        # break up date range to array of start/end date ranges for each day
        s = parse(start_date)
        e = parse(end_date)
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
            eventsResult = self.service.events().list(
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

def main():
    scout = Scout()
    if args.workplace_discovery:
        scout.workplace_discovery(('2017-09-25', '2017-09-29'), None)

if __name__ == '__main__':
    main()
