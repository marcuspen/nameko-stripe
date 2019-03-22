import logging

import stripe
from nameko.exceptions import ConfigurationError
from nameko.web.handlers import HttpRequestHandler
from werkzeug.exceptions import BadRequest, HTTPException, Unauthorized


from nameko_stripe import constants


logger = logging.getLogger(__name__)


class WebhookHandler(HttpRequestHandler):
    def __init__(self, path=None, api_key=None, endpoint_secret=None, **kwargs):
        self.api_key = api_key
        self.endpoint_secret = endpoint_secret
        super(WebhookHandler, self).__init__("POST", path, **kwargs)

    def setup(self):

        config = self.container.config.get(constants.CONFIG_KEY, {})

        try:
            self.api_key = self.api_key or config["SECRET_KEY"]
            self.endpoint_secret = self.endpoint_secret or config["ENDPOINT_SECRET"]
        except KeyError as exc:
            raise ConfigurationError(
                "Please provide {} for stripe API communication".format(exc.args[0])
            ) from exc

        if not self.url:
            self.url = config.get("DEFAULT_PATH", constants.DEFAULT_EVENT_PATH)

        super(WebhookHandler, self).setup()

    def parse_event(self, request):
        try:
            return stripe.Webhook.construct_event(
                request.data.decode("utf8"),
                request.headers.get("Stripe-Signature"),
                self.endpoint_secret,
                api_key=self.api_key,
            )
        except stripe.error.SignatureVerificationError as exc:
            logger.warning("Signature verification error", exc_info=True)
            raise Unauthorized("Signature verification failed")
        except Exception:
            logger.warning("Cannot parse Stripe webhook", exc_info=True)
            raise BadRequest("Cannot parse Stripe webhook")

    def get_entrypoint_parameters(self, request):

        event = self.parse_event(request)

        args = (event,)
        kwargs = request.path_values

        return args, kwargs

    def response_from_result(self, result):
        if not result:
            result = (200, "OK")  # default to 200, stripe ignores response data
        return super(WebhookHandler, self).response_from_result(result)

    def response_from_exception(self, exc):
        if isinstance(exc, HTTPException):
            raise exc  # Nameko should not catch these
        return super(WebhookHandler, self).response_from_exception(exc)


webhook_handler = WebhookHandler.decorator
