## Scout

The goal behind this project was to utilize the Google Calendar API and perform discovery tasks, with the intention of using the insights gained to increase productivity & mindfulness. This goal is both for the individual, as well as for a workplace as a whole.

The proof of concept for Scout was developed during a two week slack-a-thon (hack-a-thon, but not 24/48 hours; hence, the slacking) at ListenFirst Media, where I work.

UPDATE: Scout is in the process of being adapted at the moment to serve slightly new functionality. Stay tuned, changes to come.

### Project Organization

```
scout/
├── Makefile
├── README.md
├── requirements.txt
├── scout
│   ├── config
│   │   ├── aggregate_event_types.json
│   │   ├── calendar_groups.json
│   │   ├── client_secrets.json
│   │   └── credentials.json
│   ├── __init__.py
│   └── scout.py
└── setup.py
```

**scout**: Python package for Scout

**config**: holds the credentials for the Scout user; is apart of the .gitignore, so as to keep secrets, secret

## Installation

First, you need to create a project and download the json credentials file on the Google Calendar API dashboard, here: https://console.developers.google.com/flows/enableapi?apiid=calendar. Instructions on *how* to do this can be found here, in the "Step 1" section: https://developers.google.com/google-apps/calendar/quickstart/python.

Second, move and rename that downloaded file to the config/ directory naming it *client_secrets.json*.

Third, you'll need to download the requirements.

```
$ pip install -r requirements.txt
# $ make install
```

That's about it--you should be all set to go. Try `scout -h` and test a command. Follow the authorization workflow to begin using Scout and store credentials locally for further use.

## Functionality

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

## Tasks TODO:

1. Convert to python 3.6.\*
2. Use pipenv (and maybe pyenv) to better set up environment
3. Add unit testing with unittest library
4. Remove unnecessary dependencies, identify core dependencies & fix Makefile
5. Refactor, clean up
