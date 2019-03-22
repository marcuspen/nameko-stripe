import stripe
from nameko.exceptions import ConfigurationError
from nameko.extensions import DependencyProvider

from nameko_stripe import constants


class Stripe(DependencyProvider):
    def __init__(self, api_key=None):
        self.client = None
        self.api_key = api_key

    def setup(self):
        config = self.container.config.get(constants.CONFIG_KEY, {})

        self.client = stripe

        self.client.set_app_info(**constants.APP_INFO)

        try:
            self.api_key = self.api_key or config["SECRET_KEY"]
        except KeyError as exc:
            raise ConfigurationError(
                "Please provide {} for stripe API communication".format(exc.args[0])
            ) from exc

        self.client.api_key = self.api_key
        if "LOG_LEVEL" in config:
            self.client.log = config["LOG_LEVEL"]

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
