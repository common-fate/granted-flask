# Contributing

## Getting setup

You'll need to install [Poetry](https://python-poetry.org/docs/).

Install dependencies:

```bash
poetry install
```

Run tests:

```bash
poetry run pytest
```

Open a shell in the Python virtual environment:

```bash
poetry shell
```

Run a test build:

```bash
poetry build
```

## Releasing

This project uses https://github.com/coveooss/pypi-publish-with-poetry to publish the Poetry package to PyPI.
