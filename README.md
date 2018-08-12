# nameko-stripe

Stripe dependency for Nameko

## Installation

```
pip install nameko-stripe
```

## Usage

```python
from nameko.rpc import rpc
from nameko_stripe import Stripe


class MyService(object):
    name = "my_service"

    stripe = Stripe()

    @rpc
    def list_charges(self):
        return self.stripe.Charge.list()
```

You will need to insert your api_key and log level into your config.yaml:

```yaml
AMQP_URI: 'amqp://guest:guest@localhost'
STRIPE:
  api_key: abc123
  log_level: info
```
