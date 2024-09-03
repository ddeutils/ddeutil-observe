# Observe Web App

[![test](https://github.com/ddeutils/ddeutil-observe/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ddeutils/ddeutil-observe/actions/workflows/tests.yml)
[![pypi version](https://img.shields.io/pypi/v/ddeutil-observe)](https://pypi.org/project/ddeutil-observe/)
[![python support version](https://img.shields.io/pypi/pyversions/ddeutil-observe)](https://pypi.org/project/ddeutil-observe/)
[![size](https://img.shields.io/github/languages/code-size/ddeutils/ddeutil-observe)](https://github.com/ddeutils/ddeutil-observe)
[![gh license](https://img.shields.io/github/license/ddeutils/ddeutil-observe)](https://github.com/ddeutils/ddeutil-observe/blob/main/LICENSE)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


The **Lightweight observation web application** project was created for easy to
make a observation web application that getting log, or trigger status from any
data framework formats and endpoint APIs, it project will focus on the
`ddeutil-workflow` data orchestration tool.

> [!WARNING]
> This project is the best fit with `ddeutil-workflow` package. The first propose
> is monitor and observe from worker nodes that deploy workflow application.

## Installation

```shell
pip install ddeutil-observe
```

> I added this feature to the main milestone.
>
> **Docker Images** supported:
>
> | Docker Image               | Python Version | Support |
> |----------------------------|----------------|---------|
> | ddeutil-observe:latest     | `3.9`          | :x:     |
> | ddeutil-observe:python3.10 | `3.10`         | :x:     |
> | ddeutil-observe:python3.11 | `3.11`         | :x:     |
> | ddeutil-observe:python3.12 | `3.12`         | :x:     |

## Getting Started

This project implement the best scalable FastAPI web application structure.

## Configuration

| Environment              | Component | Default  | Description                              |
|--------------------------|-----------|----------|------------------------------------------|
| `OBSERVE_LOG_DEBUG_MODE` | Log       | true     | Logging mode of this observe application |

## Deployment

```shell
(env) $ uvicorn src.ddeutil.observe.app:app --host 127.0.0.1 --port 88
```
