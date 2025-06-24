# Contributing

We can always use your help to improve Next.js FastAPI Template! Please feel free to tackle existing [issues](https://github.com/vintasoftware/nextjs-fastapi-template/issues). If you have a new idea, please create a thread on [Discussions](https://github.com/vintasoftware/django-ai-assistant/discussions).

Please follow this guide to learn more about how to develop and test the project locally, before opening a pull request.

## Local Dev Setup

### Clone the repo

```bash
git clone git@github.com:vintasoftware/nextjs-fastapi-template.git
```

Check the [Get Started](get-started.md#setup) page to complete the setup.


## Install pre-commit hooks

Check the [Additional Settings - Install pre-commit hooks](additional-settings.md#pre-commit-setup) section to complete the setup.


It's critical to run the pre-commit hooks before pushing your code to follow the project's code style, and avoid linting errors.

## Updating the OpenAPI schema

It's critical to update the OpenAPI schema when you make changes to the FastAPI routes or related files:

Check the [Additional Settings - Manual execution of hot reload commands](additional-settings.md#manual-execution-of-hot-reload-commands) section to run the command.

## Tests

Check the [Additional Settings - Testing](additional-settings.md#testing) section to run the tests.

## Documentation

We use [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) to generate the documentation from markdown files.
Check the files in the `docs` directory.

To run the documentation locally, you need to run:

```bash
uv run mkdocs serve
```

## Release

!!! info
    The backend and the frontend are versioned together, that is, they should have the same version number.

To release and publish a new version, follow these steps:

1. Update the version in `fastapi_backend/pyproject.toml`, `nextjs-frontend/package.json`.
2. Update the changelog in `CHANGELOG.md`.
3. Open a PR with the changes.
4. Once the PR is merged, run the [Release GitHub Action](https://github.com/vintasoftware/nextjs-fastapi-template/actions/workflows/release.yml) to create a draft release.
5. Review the draft release, ensure the description has at least the associated changelog entry, and publish it.
