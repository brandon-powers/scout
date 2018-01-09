## Scout

The goal behind this project was to utilize the Google Calendar API and perform discovery tasks, with the intention of using the insights gained to increase productivity & mindfulness. This goal is both for the individual, as well as for a workplace as a whole.

The proof of concept for Scout was developed during a two week slack-a-thon (hack-a-thon, but not 24/48 hours; hence, the slacking) at ListenFirst Media, where I work.

### Project Organization

```
scout/
├── scout
│   ├── config
│   │   └── auth.json
│   ├── __init__.py
│   └── scout.py
├── README.md
└── setup.py
```

**scout**: Python package for Scout

**config**: holds the credentials for the Scout user; is apart of the .gitignore, so as to keep secrets, secret

## TODO

- list all calendars
- given a calendar id and a date range, for each work week in the date range, output sum of time taken by each type of event (based on 'summary')
  * allow configuration of aggregate event types; if one or more events in that aggregate event type is detected, output the aggregate sum of time taken by each type of event in the aggregate
  * aggregate event types only work if 'reader' access is available
  * allow configuration of the 'work week': startDay, endDay, startTime, endTime
- given a file path to a list of calendar ids [or a comma-separated list], perform action above for each calendar id
- default output: STDOUT; allow output flags for custom output of data in csv or json form

```
$ scout --list-calendars [--csv | --json]

id: brandon.powers@listenfirstmedia.com
id: mike.stanley@listenfirstmedia.com

$ scout --list-calendars -v [--csv | --json]

id: brandon.powers@listenfirstmedia.com
timeZone: America/New_York
accessRole: freeBusyReader

id: mike.stanley@listenfirstmedia.com
timeZone: America/New_York
accessRole: reader

$ scout --discover {<comma-separated-ids> | -g <calendar_group>} [-s <startDateTime> -e <endDateTime>] [--csv | --json]

# example: calendar_groups.json
{
  "dev": [
    "brandon.powers@listenfirstmedia.com",
    "mike.stanley@listenfirstmedia.com"
  ]
}

# example: aggregate_event_types.json
{
  "meetings": [
    "Daily Standup",
    "Sprint Meeting",
    "Weekly Ingest"
  ]
}

configuration files:
  1. client_secrets.json
  2. credentials.json
  3. aggregate_event_types.json
  4. calendar_groups.json

example output:
  startDateTime to endDateTime:
    id0:
      [event] <id> was in a "Sprint Meeting" state for n time
      [event] <id> was in a "Daily Standup" state for n time
      [aggregate] <id> was in a "meetings" state for n time

    id1:
      [event] <id> was in a "Sprint Meeting" state for n time
      [event] <id> was in a "Daily Standup" state for n time
      [aggregate] <id> was in a "meetings" state for n time

    id2:
      ...
```

## Desired Toolkit

- python 3.6
- pipenv
- unittest
- google api python client
- google oauth libs
