from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os.path

class OAuthCredentials():
    def __init__(self):
        self.credentials_path = 'config/credentials.json'
        self.client_secrets_path = 'config/client_secrets.json'

    def get_credentials(self):
        if self.credentials_exist():
            return self.read_existing_credentials()
        else:
            return self.retrieve_new_credentials()

    def credentials_exist(self):
        return os.path.isfile(self.credentials_path)

    def read_existing_credentials(self):
        with open(self.credentials_path, 'r') as f:
            config = json.load(f)

        return Credentials(
                token=config['token'],
                refresh_token=config['refresh_token'],
                id_token=config['id_token'],
                token_uri=config['token_uri'],
                client_id=config['client_id'],
                client_secret=config['client_secret'],
                scopes=config['scopes'])

    def retrieve_new_credentials(self):
        flow = Flow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=['https://www.googleapis.com/auth/calendar'],
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        auth_url, _ = flow.authorization_url(prompt='consent')

        print('Please go to this URL: {}'.format(auth_url))
        code = raw_input('Enter the authorization code: ')

        flow.fetch_token(code=code)
        credentials = flow.credentials
        self.write_credentials(credentials)
        return credentials

    def write_credentials(self, credentials):
        with open(self.credentials_path, 'w') as f:
            config = self.json(credentials)
            f.write(json.dumps(config))

    def json(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'id_token': credentials.id_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}
