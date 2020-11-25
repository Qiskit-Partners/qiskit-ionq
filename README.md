# Qiskit IonQ Provider

[![License](https://img.shields.io/github/license/qiskit-community/qiskit-aqt-provider.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)

**Qiskit** is an open-source SDK for working with quantum computers at the level of circuits, algorithms, and application modules.

This project contains a provider that allows access to **[IonQ]** ion trap quantum
systems.

The example python notebook (in `/example`) should help you understand basic usage.

## Installation

You can install the provider using pip:

```bash
pip install qiskit-ionq-provider
```

## Provider Setup

The IonQ Provider uses IonQ's REST API.

To instantiate the provider, make sure you have an access token then create a provider:

```python
from qiskit_ionq_provider import IonQProvider

provider = IonQProvider("superseekr!t-token")
```

### Credential Environment Variables

Alternatively, the IonQ Provider can discover your access token from environment variables:

```bash
export QISKIT_IONQ_API_TOKEN="superseekr!t-token"
```

Then invoke instantiate the provider without any arguments:

```python
from qiskit_ionq_provider import IonQProvider

provider = IonQProvider()
```

## Running Tests

This package uses the [pytest](https://docs.pytest.org/en/stable/) test runner.

To use pytest directly, just run:
```bash
pytest [pytest-args]
```

Alternatively, you may also use setuptools integration by running tests through `setup.py`, e.g.:

```bash
python setup.py test --addopts="[pytest-args]"
```

### Fixtures

Global pytest fixtures for the test suite can be found in the top-level [test/conftest.py](./test/conftest.py) file.

## IonQ API Access

If you would like to use IonQ as a Qiskit provider, please contact
sales@ionq.co to request more information about gaining access to the IonQ API.

## Documentation

To build the API reference and quickstart docs, run:

```bash
pip install -r requirements-docs.txt
make html
open build/html/index.html
```

## License

[Apache License 2.0].

[IonQ]: https://www.ionq.com/
[Apache License 2.0]: https://github.com/qiskit-community/qiskit-ionq-provider/blob/master/LICENSE.txt
