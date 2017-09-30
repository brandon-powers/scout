## Scout

The goal behind this project was to utilize the Google Calendar API and perform discovery tasks, with the intention of using the insights gained to increase productivity & mindfulness. This goal is both for the individual, as well as for a workplace as a whole.

The proof of concept for Scout was developed during a two week slack-a-thon (hack-a-thon, but not 24/48 hours; hence, the slacking) at ListenFirst Media, where I work. 

### Project Organization

scout/
├── scout
│   ├── config
│   │   └── auth.json
│   ├── __init__.py
│   └── scout.py
├── README.md
└── setup.py

**scout**: Python package for Scout

**config**: holds the credentials for the Scout user; is apart of the .gitignore, so as to keep secrets, secret
