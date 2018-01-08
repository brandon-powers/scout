from setuptools import setup

setup(name='Scout',
      version='0.1.0',
      description='A Google Calendar discovery tool',
      url='https://github.com/brandon-powers/scout',
      author='Brandon Powers',
      author_email='brandon.powers@listenfirstmedia.com',
      packages=['scout'],
      install_requires=[
        'google-api-python-client',
        'oauth2client',
        'google-auth-oauthlib',
        'pep8',
        'google-auth-httplib2',
        'python-dateutil',
        'matplotlib'
      ])
