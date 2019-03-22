from mock import Mock, patch, call

import pytest

from nameko_stripe import Stripe
from nameko_stripe.constants import VERSION, APP_NAME, APP_URL


@pytest.fixture
def mock_stripe():
    with patch("nameko_stripe.dependency_provider.stripe") as stripe:
        yield stripe


@pytest.fixture
def stripe_dependency(stripe_config):
    dependency = Stripe()
    dependency.container = Mock()
    dependency.container.config = stripe_config

    return dependency


def test_setup(stripe_config, stripe_dependency, mock_stripe):
    stripe_dependency.setup()

    assert stripe_dependency.client == mock_stripe
    assert stripe_dependency.client.api_key == stripe_config["STRIPE"]["SECRET_KEY"]
    assert stripe_dependency.client.set_app_info.call_args_list == [
        call(name=APP_NAME, url=APP_URL, version=VERSION)
    ]


def test_setup_log_level(stripe_config, stripe_dependency, mock_stripe):
    stripe_config["STRIPE"]["LOG_LEVEL"] = "debug"

    stripe_dependency.setup()

    assert stripe_dependency.client.log is "debug"


def test_stop(stripe_dependency):
    stripe_dependency.setup()
    stripe_dependency.start()
    stripe_dependency.stop()

    assert stripe_dependency.client is None


def test_kill(stripe_dependency):
    stripe_dependency.setup()
    stripe_dependency.start()
    stripe_dependency.kill()

    assert stripe_dependency.client is None


def test_get_dependency(stripe_dependency, mock_stripe):
    stripe_dependency.setup()
    stripe_dependency.start()
    client = stripe_dependency.get_dependency(Mock())

    assert client == mock_stripe
