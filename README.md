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

- keep *scout* name, just repurpose it as a measurement tool. It kind of still fits the above description.
- define behavior of this application; what does it do? use cases, etc.
  - list all calendars you have access to
  - given a particular calendar id & date range, output reports/measurements of busyness of each work week (M-F, 8AM-6PM, make configurable)
    * the amount of detail here will change based on the access control (acl) role the end-user has
      # n. <access-control-role>

      1. freeBusyReader:
        week X:
          # no enum option, only individual event timings
          [event] <id> was in a "busy" state for n time

      2. >= reader:
        week X:
          # have an enum with meeting names, output time for each kind of meeting, then a total
          # 1. have optional enums that combine particular event names and have aggregate stats
          # i.e. -> meetings={Sprint meeting, Daily standup, Weekly Ingest}, hiring={Phone Interview, etc.}
          # 2. if not a part of an enum, a particular event will be grouped as is and reported; if part of enum, will have additionally aggregation at end of individual report

          [event] <id> was in a "Sprint Meeting" state for n time
          [event] <id> was in a "Daily Standup" state for n time
          [aggregate] <id> was in a "meetings" state for n time
  - ability to perform above function for all calendar id's returned from list, check access control role before hand

## Toolkit

- python 3.6
- pipenv
- unittest
- google api python client
- oauthlib + request-oauthlib
