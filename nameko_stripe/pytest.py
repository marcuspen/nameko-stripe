import json
import time

import pytest
import stripe

from nameko_stripe import constants


@pytest.fixture
def stripe_config(web_config):
    config = web_config.copy()
    config.update(
        {
            "STRIPE": {
                "SECRET_KEY": "sk_test_EWX...FbN",
                "ENDPOINT_SECRET": "whsec_6Yi...Igu",
            }
        }
    )
    return config


@pytest.fixture
def make_webhook():
    def make(**fields):
        payload = {
            "created": 1326853478,
            "livemode": False,
            "id": "evt_00000000000000",
            "type": "source.chargeable",
            "object": "event",
            "request": None,
            "pending_webhooks": 1,
            "api_version": "2017-08-15",
            "data": {},
        }
        payload.update(fields)
        return payload

    return make


@pytest.fixture
def send_webhook(stripe_config, make_webhook, runner_factory, web_session):
    def send(service_cls, webhook=None, endpoint_secret=None, path=None):

        webhook = webhook or make_webhook()
        endpoint_secret = endpoint_secret or stripe_config["STRIPE"]["ENDPOINT_SECRET"]
        path = path or constants.DEFAULT_EVENT_PATH

        timestamp = int(time.time())
        payload = json.dumps(webhook)
        scheme = stripe.WebhookSignature.EXPECTED_SCHEME
        payload_to_sign = "%d.%s" % (timestamp, payload)
        signature = stripe.WebhookSignature._compute_signature(
            payload_to_sign, endpoint_secret
        )
        signature_header = "t=%d,%s=%s" % (timestamp, scheme, signature)

        runner = runner_factory(stripe_config, service_cls)
        runner.start()

        return web_session.post(
            path,
            data=json.dumps(webhook),
            headers={"Stripe-Signature": signature_header},
        )

    return send
