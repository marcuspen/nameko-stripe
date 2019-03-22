from unittest.mock import Mock, call

import pytest
from nameko.exceptions import ConfigurationError

from nameko_stripe import event_handler
from nameko_stripe.handlers.event import EventHandler


def test_unit_event_handler_missing_config_key():

    event_handler = EventHandler("source.chargeable")
    event_handler.container = Mock(config={})

    with pytest.raises(ConfigurationError) as exc:
        event_handler.setup()

    assert (
        str(exc.value) ==
        "Please provide SECRET_KEY for stripe API communication"
    )


@pytest.mark.parametrize("setting", ("SECRET_KEY", "ENDPOINT_SECRET"))
def test_unit_event_handler_missing_secrets(stripe_config, setting):

    stripe_config["STRIPE"].pop(setting)

    event_handler = EventHandler("source.chargeable")
    event_handler.container = Mock(config=stripe_config)

    with pytest.raises(ConfigurationError) as exc:
        event_handler.setup()

    assert (
        str(exc.value) ==
        "Please provide {} for stripe API communication".format(setting)
    )


def test_unit_event_handler_passed_settings():

    path = "/foo/bar/"
    api_key = "sk_test_****"
    endpoint_secret = "whsec_****"

    event_handler = EventHandler(
        "source.chargeable",
        path=path,
        api_key=api_key,
        endpoint_secret=endpoint_secret
    )
    event_handler.container = Mock(config={})
    event_handler.setup()

    assert event_handler.api_key == api_key
    assert event_handler.endpoint_secret == endpoint_secret
    assert event_handler.url == path


def test_event_handler(stripe_config, make_webhook, send_webhook):

    tracker = Mock()

    class Service:
        name = "service"

        @event_handler("source.chargeable")
        def handle_stripe_event(self, event_type, event_payload):
            tracker(event_type, event_payload)

    webhook = make_webhook()

    response = send_webhook(Service, webhook)

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call("source.chargeable", webhook)


def test_event_handler_multiple_handlers(stripe_config, make_webhook, send_webhook):

    handle_source_chargeable_tracker = Mock()
    handle_source_failed_tracker = Mock()
    handle_source_events_tracker = Mock()

    class Service:
        name = "service"

        @event_handler("source.chargeable")
        def handle_source_chargeable(self, event_type, event_payload):
            handle_source_chargeable_tracker(event_type, event_payload)

        @event_handler("source.failed")
        def handle_source_failed(self, event_type, event_payload):
            handle_source_failed_tracker(event_type, event_payload)

        @event_handler("source.chargeable")
        @event_handler("source.failed")
        def handle_source_events(self, event_type, event_payload):
            handle_source_events_tracker(event_type, event_payload)

    webhook = make_webhook()

    response = send_webhook(Service, webhook)

    assert response.status_code == 200
    assert response.text == "OK"

    assert (
		handle_source_chargeable_tracker.call_args ==
        call("source.chargeable", webhook)
    )
    assert handle_source_failed_tracker.call_count == 0
    assert (
        handle_source_events_tracker.call_args ==
        call("source.chargeable", webhook)
    )


def test_event_handler_passed_secrets(make_webhook, send_webhook):

    tracker = Mock()

    api_key = "sk_test_****"
    endpoint_secret = "whsec_****"

    class Service:
        name = "service"

        @event_handler(
            "source.chargeable",
            api_key=api_key,
            endpoint_secret=endpoint_secret
        )
        def handle_stripe_event(self, event_type, event_payload):
            tracker(event_type, event_payload)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, endpoint_secret=endpoint_secret)

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call("source.chargeable", webhook)


def test_event_handler_passed_path(stripe_config, make_webhook, send_webhook):

    tracker = Mock()

    class Service:
        name = "service"

        @event_handler("source.chargeable", "/foo/bar")
        def handle_stripe_event(self, event_type, event_payload):
            tracker(event_type, event_payload)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, path="/foo/bar")

    assert response.status_code == 200
    assert response.text == "OK"

    assert tracker.call_args == call("source.chargeable", webhook)


def test_event_handler_signature_verification_failure(
    stripe_config, make_webhook, send_webhook
):

    tracker = Mock()

    class Service:
        name = "service"

        @event_handler("source.chargeable")
        def handle_stripe_event(self, event_type, event_payload):
            tracker(event_type, event_payload)

    webhook = make_webhook()

    response = send_webhook(Service, webhook, endpoint_secret="wrong")

    assert response.status_code == 401
    assert response.reason == "UNAUTHORIZED"
    assert "Signature verification failed" in response.text


def test_event_handler_event_parsing_failure(
    stripe_config, make_webhook, send_webhook
):

    tracker = Mock()

    class Service:
        name = "service"

        @event_handler("source.chargeable")
        def handle_stripe_event(self, event_type, event_payload):
            tracker(event_type, event_payload)

    webhook = "} not a JSON {"

    response = send_webhook(Service, webhook)

    assert response.status_code == 400
    assert response.reason == "BAD REQUEST"
    assert "Cannot parse Stripe webhook" in response.text
