from mock import Mock, patch, call

import pytest
from ..stripe_dep import Stripe, VERSION, APP_NAME, APP_URL


@pytest.fixture
def mock_stripe():
    with patch('nameko_stripe.stripe_dep.stripe') as s:
        yield s


@pytest.fixture
def test_config():
    return {
        'STRIPE': {
            'api_key': 'abc123',
            'log_level': 'debug',
        }
    }


@pytest.fixture
def stripe_dependency(test_config):
    dependency = Stripe()
    dependency.container = Mock()
    dependency.container.config = test_config

    return dependency


def test_setup(stripe_dependency):
    stripe_dependency.setup()

    assert stripe_dependency.api_key == 'abc123'
    assert stripe_dependency.log_level == 'debug'


def test_start(stripe_dependency, mock_stripe):
    stripe_dependency.setup()
    stripe_dependency.start()

    assert stripe_dependency.client == mock_stripe
    assert stripe_dependency.client.log == 'debug'
    assert stripe_dependency.client.api_key == 'abc123'
    assert stripe_dependency.client.set_app_info.call_args_list == [
        call(name=APP_NAME, url=APP_URL, version=VERSION)
    ]


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
