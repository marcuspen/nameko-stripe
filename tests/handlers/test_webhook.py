from unittest.mock import Mock, call

import pytest
from nameko.exceptions import ConfigurationError

from nameko_stripe import webhook_handler
from nameko_stripe.handlers.webhook import WebhookHandler


def test_unit_webhook_handler_missing_config_key():

    webhook_handler = WebhookHandler()
    webhook_handler.container = Mock(config={})

    with pytest.raises(ConfigurationError) as exc:
        webhook_handler.setup()

    assert str(exc.value) == "Please provide SECRET_KEY for stripe API communication"


@pytest.mark.parametrize("setting", ("SECRET_KEY", "ENDPOINT_SECRET"))
def test_unit_webhook_handler_missing_secrets(stripe_config, setting):

    stripe_config["STRIPE"].pop(setting)

    webhook_handler = WebhookHandler()
    webhook_handler.container = Mock(config=stripe_config)

    with pytest.raises(ConfigurationError) as exc:
        webhook_handler.setup()

    assert str(exc.value) == "Please provide {} for stripe API communication".format(
        setting
    )


def test_unit_webhook_handler_passed_settings():

    path = "/foo/bar/"
    api_key = "sk_test_****"
    endpoint_secret = "whsec_****"

    webhook_handler = WebhookHandler(
        path, api_key=api_key, endpoint_secret=endpoint_secret
    )
    webhook_handler.container = Mock(config={})
    webhook_handler.setup()

    assert webhook_handler.api_key == api_key
    assert webhook_handler.endpoint_secret == endpoint_secret
    assert webhook_handler.url == path


def test_webhook_handler(stripe_config, make_webhook, send_webhook):

    tracker = Mock()

    class Service:
        name = "service"

        @webhook_handler
        def handle_stripe_webhooks(self, webhook):
            tracker(webhook)

    webhook = make_webhook()

    response = send_webhook(Service, webhook)

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call(webhook)


def test_webhook_handler_passed_secrets(make_webhook, send_webhook):

    tracker = Mock()

    api_key = "sk_test_****"
    endpoint_secret = "whsec_****"

    class Service:
        name = "service"

        @webhook_handler(api_key=api_key, endpoint_secret=endpoint_secret)
        def handle_stripe_webhooks(self, webhook):
            tracker(webhook)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, endpoint_secret=endpoint_secret)

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call(webhook)


def test_webhook_handler_passed_path(stripe_config, make_webhook, send_webhook):

    tracker = Mock()

    class Service:
        name = "service"

        @webhook_handler("/foo/bar")
        def handle_stripe_webhooks(self, webhook):
            tracker(webhook)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, path="/foo/bar")

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call(webhook)


def test_webhook_handler_returning(stripe_config, make_webhook, send_webhook):
    class Service:
        name = "service"

        @webhook_handler
        def handle_stripe_webhooks(self, webhook):
            return 418, "The kettle is on"

    webhook = make_webhook()

    response = send_webhook(Service, webhook)

    assert response.status_code == 418
    assert response.text == "The kettle is on"


def test_webhook_handler_signature_verification_failure(
    stripe_config, make_webhook, send_webhook
):

    tracker = Mock()

    class Service:
        name = "service"

        @webhook_handler
        def handle_stripe_webhooks(self, webhook):
            tracker(webhook)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, endpoint_secret="wrong")

    assert response.status_code == 401
    assert response.reason == "UNAUTHORIZED"
    assert "Signature verification failed" in response.text


def test_webhook_handler_event_parsing_failure(
    stripe_config, make_webhook, send_webhook
):

    tracker = Mock()

    class Service:
        name = "service"

        @webhook_handler
        def handle_stripe_webhooks(self, webhook):
            tracker(webhook)

    webhook = "} not a JSON {"

    response = send_webhook(Service, webhook)

    assert response.status_code == 400
    assert response.reason == "BAD REQUEST"
    assert "Cannot parse Stripe webhook" in response.text


def test_webhook_handler_unhandled_exception(stripe_config, make_webhook, send_webhook):
    class Boom(Exception):
        pass

    class Service:
        name = "service"

        @webhook_handler
        def handle_stripe_webhook(self, webhook):
            raise Boom("Boom!")

    webhook = make_webhook()

    response = send_webhook(Service, webhook)

    assert response.status_code == 500
    assert response.reason == "INTERNAL SERVER ERROR"
    assert "Boom!" in response.text
