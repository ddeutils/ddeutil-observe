# Observe Web App

[![test](https://github.com/ddeutils/ddeutil-observe/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ddeutils/ddeutil-observe/actions/workflows/tests.yml)
[![pypi version](https://img.shields.io/pypi/v/ddeutil-observe)](https://pypi.org/project/ddeutil-observe/)
[![python support version](https://img.shields.io/pypi/pyversions/ddeutil-observe)](https://pypi.org/project/ddeutil-observe/)
[![size](https://img.shields.io/github/languages/code-size/ddeutils/ddeutil-observe)](https://github.com/ddeutils/ddeutil-observe)
[![gh license](https://img.shields.io/github/license/ddeutils/ddeutil-observe)](https://github.com/ddeutils/ddeutil-observe/blob/main/LICENSE)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The **Lightweight observation web application** project was created for easy to
make a observation web application that getting log, or trigger status from any
data framework formats and endpoint APIs, this project focuses on the
`ddeutil-workflow` data orchestration tool first :dart:.

> [!WARNING]
> This project is the best fit integration with `ddeutil-workflow` package.
> The first propose is monitor and observe from worker nodes that deploy the
> workflow application on a target self-hosted.

## :round_pushpin: Installation

```shell
pip install ddeutil-observe
```

> I added this feature to the main milestone.
>
> :egg: **Docker Images** supported:
>
> | Docker Image               | Python Version | Support |
> |----------------------------|----------------|---------|
> | ddeutil-observe:latest     | `3.9`          | :x:     |
> | ddeutil-observe:python3.10 | `3.10`         | :x:     |
> | ddeutil-observe:python3.11 | `3.11`         | :x:     |
> | ddeutil-observe:python3.12 | `3.12`         | :x:     |
> | ddeutil-observe:python3.12 | `3.13`         | :x:     |

## :beers: Getting Started

This project implement the best scalable FastAPI web application structure.
For the first phase, I will use the SQLite be a backend database that keep
authentication and workflows data.

### Main Page

### Workflow Release Page

## :cookie: Configuration

| Environment                                 | Component | Default                          | Description                                                                                   |
|---------------------------------------------|-----------|----------------------------------|-----------------------------------------------------------------------------------------------|
| `OBSERVE_CORE_TIMEZONE`                     | Core      | UTC                              | A timezone that use on all components of this application                                     |
| `OBSERVE_SQLALCHEMY_DB_ASYNC_URL`           | Core      | sqlite+aiosqlite:///./observe.db | A database url of the application backend side                                                |
| `OBSERVE_CORE_ACCESS_SECRET_KEY`            | Core      | `secrets.token_urlsafe(32)`      | A secret key that use to hash the access token with jwt package                               |
| `OBSERVE_CORE_ACCESS_TOKEN_EXPIRE_MINUTES`  | Core      | 30                               | Expire period of the access token in minute unit                                              |
| `OBSERVE_CORE_REFRESH_SECRET_KEY`           | Core      | `secrets.token_urlsafe(32)`      | A secret key that use to hash the refresh token with jwt package                              |
| `OBSERVE_CORE_REFRESH_TOKEN_EXPIRE_MINUTES` | Core      | 60 * 24 * 8                      | Expire period of the refresh token in minute unit                                             |
| `OBSERVE_WEB_ADMIN_USER`                    | Web       | observe                          | An username of superuser                                                                      |
| `OBSERVE_WEB_ADMIN_PASS`                    | Web       | observe                          | A password of superuser                                                                       |
| `OBSERVE_WEB_ADMIN_EMAIL`                   | Web       | observe@mail.com                 | An email of superuser                                                                         |
| `OBSERVE_LOG_DEBUG_MODE`                    | Log       | true                             | Logging mode                                                                                  |
| `OBSERVE_LOG_SQLALCHEMY_DEBUG_MODE`         | Log       | true                             | Database Logging mode that will logging every execution statement before and after connection |

## :rocket: Deployment

```shell
(env) $ uvicorn src.ddeutil.observe.app:app --host 127.0.0.1 --port 88
```

> [!NOTE]
> If this package already deploy, it able to use
> `uvicorn ddeutil.workflow.api:app --host 127.0.0.1 --port 88 --workers 4`
