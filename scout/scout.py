#!/usr/bin/env python

from apiclient import discovery
from oauth_credentials import OAuthCredentials
from dateutil import parser as PA
import datetime
import json
import csv
import argparse

class Scout():
    """This class offers Google Calendar utilities with multiple output formats.

    The two different actions this class implements:
        * event discovery
        * calendar listing

    It also offers support for the following output formats:
        * stdout
        * csv
        * json

    See documentation at https://github.com/brandon-powers/scout for more help.'
    """

    OUTPUT_FORMATS = ['stdout', 'csv', 'json']

    def __init__(self):
        """Initializes the API client and default output format."""
        credentials = OAuthCredentials().get_credentials()
        self.client = self.get_client(credentials)
        self.set_output_format('stdout')

    def get_client(self, credentials):
        """Returns the Google Calendar API client."""
        return discovery.build('calendar', 'v3', credentials=credentials)

    def set_output_format(self, output_format):
        """Sets the output format of the object."""
        try:
            if output_format in self.OUTPUT_FORMATS:
                self.output_format = output_format
            else:
                raise ValueError
        except ValueError:
            print('Error: invalid output format')

    def discover_calendars(self, calendar_ids, start, end):
        """Discovers the event stats for a given set of calendars and date range."""
        stats = {}
        for calendar_id in calendar_ids:
            stats[calendar_id] = {}
            calendar_events = self.discover_events_for_calendar(calendar_id, start, end)
            for event in calendar_events:
                # Note: if these fields are missing, the assumption is the event is an
                # all day event--these are not counted towards the total_time
                if event['start'].get('dateTime') and event['end'].get('dateTime'):
                    start_time = PA.parse(event['start']['dateTime'])
                    end_time = PA.parse(event['end']['dateTime'])
                    total_time = end_time - start_time

                if event.get('summary'):
                    summary = event['summary']
                else:
                    summary = 'busy'

                if stats[calendar_id].get(summary):
                    stats[calendar_id][summary] += total_time
                else:
                    stats[calendar_id][summary] = total_time

        self.output_discovery(stats, start, end)
        return stats

    def discover_events_for_calendar(self, calendar_id, start, end):
        """Discovers the event stats for a single calendar in a date range."""
        calendar_events = []
        page_token = None
        while True:
            events = self.client.events().list(timeMin=start, timeMax=end, singleEvents=True, calendarId=calendar_id, pageToken=page_token, maxResults=100).execute()
            calendar_events.append(events['items'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        calendar_events = [y for x in calendar_events for y in x]
        return calendar_events

    def output_discovery(self, stats, start, end):
        """
        """
        if self.output_format == 'stdout':
            self.output_discovery_to_stdout(stats, start, end)
        elif self.output_format == 'csv':
            self.output_discovery_to_csv(stats, start, end)
        elif self.output_format == 'json':
            self.output_discovery_to_json(stats, start, end)

    def output_discovery_to_stdout(self, stats, start, end):
        """
        """
        for calendar_id, stat in stats.iteritems():
            sum_aggregate = datetime.timedelta()
            for event, event_length in stat.iteritems():
                sum_aggregate += event_length
                print('[event] ' + self.stringify(calendar_id) + ' was in the ' + self.stringify(event) + ' state for ' + self.stringify(event_length.total_seconds()) + ' seconds.')
            print('[aggregate] ' + self.stringify(calendar_id) + ' was busy for ' + self.stringify(sum_aggregate.total_seconds()) + ' seconds.\n')

    def output_discovery_to_csv(self, stats, start, end):
        """
        """
        with open('outfile.csv', 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['type', 'calendar_id', 'name', 'seconds', 'start', 'end'])
            for calendar_id, stat in stats.iteritems():
                sum_aggregate = datetime.timedelta()
                for event, event_length in stat.iteritems():
                    sum_aggregate += event_length
                    writer.writerow(['event', self.stringify(calendar_id), self.stringify(event), event_length.total_seconds(), self.stringify(start), self.stringify(end)])
                writer.writerow(['aggregate', self.stringify(calendar_id), 'sum', sum_aggregate.total_seconds(), self.stringify(start), self.stringify(end)])

    def output_discovery_to_json(self, stats, start, end):
        """
        """
        with open('outfile.json', 'w') as outfile:
            res = {}
            for calendar_id, stat in stats.iteritems():
                calendar_info = []
                sum_aggregate = datetime.timedelta()
                for event, event_length in stat.iteritems():
                    sum_aggregate += event_length
                    calendar_info.append({
                        'type': 'event',
                        'calendar_id': self.stringify(calendar_id),
                        'name': self.stringify(event),
                        'time': event_length.total_seconds(),
                        'start': self.stringify(start),
                        'end': self.stringify(end)})
                calendar_info.append({
                    'type': 'aggregate',
                    'calendar_id': self.stringify(calendar_id),
                    'name': 'sum',
                    'time': sum_aggregate.total_seconds(),
                    'start': self.stringify(start),
                    'end': self.stringify(end)})
                res[calendar_id] = calendar_info
            json.dump(res, outfile)

    def list_calendars(self):
        """
        """
        calendars = []
        page_token = None
        while True:
            calendar_list = self.client.calendarList().list(pageToken=page_token).execute()
            calendars.append(calendar_list['items'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        calendars = [y for x in calendars for y in x]
        self.output_calendars(calendars)
        return calendars

    def output_calendars(self, calendars):
        """
        """
        calendars = map(lambda x: {'calendar_id': x['id'], 'access_role': x['accessRole']}, calendars)

        if self.output_format == 'stdout':
            self.output_calendars_to_stdout(calendars)
        elif self.output_format == 'csv':
            self.output_calendars_to_csv(calendars)
        elif self.output_format == 'json':
            self.output_calendars_to_json(calendars)

    def output_calendars_to_stdout(self, calendars):
        """
        """
        print(json.dumps(calendars, indent=4))

    def output_calendars_to_csv(self, calendars):
        """
        """
        with open('outfile.csv', 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['calendar_id', 'access_role'])
            for calendar in calendars:
                writer.writerow([calendar['calendar_id'], calendar['access_role']])

    def output_calendars_to_json(self, calendars):
        """
        """
        with open('outfile.json', 'w') as outfile:
            json.dump(calendars, outfile)

    def stringify(self, s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        else:
            return str(s)


usage = '\n$ scout --list-calendars [--csv | --json] ' \
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

scout = Scout()
if args.csv:
    scout.set_output_format('csv')
elif args.json:
    scout.set_output_format('json')

if args.list_calendars:
    scout.list_calendars()
elif args.discover:
    if args.calendar_group != '':
        with open('config/calendar_groups.json', 'r') as f:
            ids = json.load(f)[args.calendar_group]
        scout.discover_calendars(ids, args.start, args.end)
