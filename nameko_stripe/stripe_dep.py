import stripe
from nameko.extensions import DependencyProvider

from nameko_stripe import APP_NAME, APP_URL, VERSION


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

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
