import stripe
from nameko.extensions import DependencyProvider

from nameko_stripe import constants


class Stripe(DependencyProvider):

    def __init__(self):
        self.client = None

    def setup(self):
        config = self.container.config[constants.CONFIG_KEY]
        self.api_key = config['SECRET_KEY']
        if 'LOG_LEVEL' in config:
            self.log_level = config['LOG_LEVEL']

    def start(self):
        self.client = stripe
        self.client.log = self.log_level
        self.client.set_app_info(**constants.APP_INFO)
        self.client.api_key = self.api_key

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
