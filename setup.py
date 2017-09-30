from setuptools import setup

setup(name='Scout',
      version='0.1.0',
      description='A Google Calendar discovery tool',
      url='https://github.com/brandon-powers/scout',
      author='Brandon Powers',
      author_email='brandon.powers@listenfirstmedia.com',
      packages=['scout'],
      install_requires=[
          'google-auth',
          'google-api-python-client'
      ])
