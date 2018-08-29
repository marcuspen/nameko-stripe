import stripe
from nameko.extensions import DependencyProvider


APP_NAME = 'nameko-stripe'
APP_URL = 'https://github.com/marcuspen/nameko-stripe'
VERSION = '0.1.3'
APP_INFO = dict(name=APP_NAME, url=APP_URL, version=VERSION)

STRIPE_CONFIG_KEY = 'STRIPE'


class Stripe(DependencyProvider):

    def __init__(self):
        self.client = None

    def setup(self):
        config = self.container.config[STRIPE_CONFIG_KEY]
        self.api_key = config['api_key']
        self.log_level = config['log_level']

    def start(self):
        self.client = stripe
        self.client.log = self.log_level
        self.client.set_app_info(**APP_INFO)
        self.client.api_key = self.api_key

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
