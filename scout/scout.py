#!/usr/bin/env python

from apiclient import discovery
from oauth_credentials import OAuthCredentials
from dateutil import parser as PA
import datetime
import json
import csv
import argparse

class Scout():
    OUTPUT_FORMATS = ['stdout', 'csv', 'json']

    def __init__(self):
        credentials = OAuthCredentials().get_credentials()
        self.client = self.get_client(credentials)
        self.set_output_format('stdout')

    def get_client(self, credentials):
        return discovery.build('calendar', 'v3', credentials=credentials)

    def set_output_format(self, output_format):
        try:
            if output_format in self.OUTPUT_FORMATS:
                self.output_format = output_format
            else:
                raise ValueError
        except ValueError:
            print('Error: invalid output format')

    def output(self, value, action, start, end):
        if self.output_format == 'stdout':
            if action == 'list_calendar':
                print(value)
            elif action == 'discover':
                for key, val in value.iteritems():
                    summ = datetime.timedelta()
                    for event, diff in val.iteritems():
                        summ += diff
                        print('[event] ' + str(key) + ' was in the ' + str(event) + ' state for ' + str(diff.total_seconds()) + ' seconds.')
                    print('[aggregate] ' + str(key) + ' was busy for ' + str(summ.total_seconds()) + ' seconds.\n')

        elif self.output_format == 'csv':
            if action == 'list_calendar':
                with open('outfile.csv', 'w') as outfile:
                    writer = csv.writer(outfile, lineterminator='\n')
                    verbose = type(value[0]) != unicode
                    if verbose:
                        writer.writerow(['calendar_id', 'access_role'])
                        for val in value:
                            writer.writerow([val['calendar_id'], val['access_role']])
                    else:
                        writer.writerow(['id'])
                        for val in value:
                            writer.writerow([val])
            elif action == 'discover':
                with open('outfile.csv', 'w') as outfile:
                    writer = csv.writer(outfile, lineterminator='\n')
                    writer.writerow(['type', 'calendar_id', 'name', 'seconds', 'end', 'start'])
                    for key, val in value.iteritems():
                        summ = datetime.timedelta()
                        for event, diff in val.iteritems():
                            summ += diff
                            writer.writerow(['event', str(key), str(event), diff.total_seconds(), str(start), str(end)])
                        writer.writerow(['aggregate', str(key), 'sum', summ.total_seconds(), str(start), str(end)])

        elif self.output_format == 'json':
            print('stub')

    def list_calendars(self, verbose):
        calendars = []
        page_token = None
        while True:
            calendar_list = self.client.calendarList().list(pageToken=page_token).execute()
            calendars.append(calendar_list['items'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        if verbose:
            output = map(lambda x: {'id': x['id'], 'accessRole': x['accessRole']}, calendars[0])
        else:
            output = map(lambda x: x['id'], calendars[0])
        self.output(output, 'list_calendar', None, None)
        return calendars

    def discover(self, ids, start, end):
        # calendar_group vs. comma-separated input is dealt
        # with outside of this function, with cli input
        sums = {}
        for calendar_id in ids:
            sums[calendar_id] = {}
            discovery = self.discover_for_one_id(calendar_id, start, end)
            for disc in discovery[0]:
                start_diff = PA.parse(disc['start']['dateTime'])
                end_diff = PA.parse(disc['end']['dateTime'])
                length = end_diff - start_diff

                if disc.get('summary'):
                    summary = disc['summary']
                else:
                    summary = 'busy'

                if sums[calendar_id].get(summary):
                    sums[calendar_id][summary] += length
                else:
                    sums[calendar_id][summary] = length
        self.output(sums, 'discover', start, end)
        return sums

    def discover_for_one_id(self, calendar_id, start, end):
        res = []
        page_token = None
        while True:
            events = self.client.events().list(timeMin=end, timeMax=start, singleEvents=True, calendarId=calendar_id, pageToken=page_token, maxResults=100).execute()
            res.append(events['items'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return res

usage = '\n$ scout --list-calendars [-v] [--csv | --json] ' \
        '\n$ scout --discover {<comma-separated-ids> | -g <calendar_group>} ' \
        '[-s <startDateTime> -e <endDateTime>] [--csv | --json]'
epilog = 'See documentation at https://github.com/brandon-powers/scout for more help.'
parser = argparse.ArgumentParser(
            description='A Google Calendar discovery tool',
            prog='scout',
            usage=usage,
            epilog=epilog
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
discover_flags.add_argument('-g', '--calendar-group', default='', help=group_help)

start_help = 'specify a start date time i.e. YYYY-MM-DDTHH:mm:ssZ, 2018-01-08T00:03:00Z'
discover_flags.add_argument('-s', '--start', type=str, default=datetime.datetime.utcnow().isoformat() + 'Z', help=start_help)
end_help = 'specify an end date time i.e. YYYY-MM-DDTHH:mm:ssZ, 2018-01-08T00:03:00Z'
discover_flags.add_argument('-e', '--end', type=str, default=(datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat() + 'Z', help=end_help)

output_flags = parser.add_argument_group('output')
output_help_csv = 'output Scout data in csv format'
output_flags.add_argument('-c', '--csv', action='store_true', help=output_help_csv)
output_help_json = 'output Scout data in json format'
output_flags.add_argument('-j', '--json', action='store_true', help=output_help_json)
args = parser.parse_args()
print(args.start)
print(args.end)

scout = Scout()
if args.csv:
    scout.set_output_format('csv')
elif args.json:
    scout.set_output_format('json')

if args.list_calendars:
    scout.list_calendars(args.verbose)

if args.calendar_group != '':
    with open('config/calendar_groups.json', 'r') as f:
        ids = json.load(f)[args.calendar_group]
    scout.discover(ids, args.start, args.end)
