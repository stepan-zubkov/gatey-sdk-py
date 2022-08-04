# Florgon Gatey SDK for Python (Official).

This is the official Python SDK for [Florgon Gatey](https://gatey.florgon.space)
Gatey Python SDK for API. Works with Florgon hosted, or self-hosted server.

---

## Getting Started

### Install

```
pip install --upgrade gatey-sdk
```

### Configuration

```python
import gatey_sdk
client = gatey_sdk.Client()
```

### Usage

```python
import gatey_sdk
client = gatey_sdk.Client()

# Will send message (capture).
client.capture_message("Hello Python Gatey SDK!")

# Will capture exception.
@client.catch
def f():
    raise ValueError

# Same as above.
try:
    raise ValueError
except Exception as e:
    client.capture_exception(e)
```

## Integrations

For now there is no native integrations.

## License

Licensed under the MIT license, see [`LICENSE`](LICENSE)
