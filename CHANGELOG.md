# Changelogs

## Latest Changes

## 0.0.8

### :sparkles: Features

- :dart: feat: update workflow detail page.
- :dart: feat: add workflow detail page.
- :dart: feat: add workflow running page.
- :dart: feat: improve profile and setting page.
- :dart: feat: add notification feature to the main page.
- :dart: feat: add workflow detail can dynamic change when click on workflow name.
- :dart: feat: add modal for create workflow button.
- :dart: feat: add display trace log.
- :dart: feat: update models that sync with workflow.
- :dart: feat: add workflow endpoints config for map workflow node.
- :dart: feat: add logout on setting.
- :dart: feat: add views for schedule route.
- :dart: feat: remove custom logging and use uvicorn instead.
- :dart: feat: add routes and views for other routes.

### :bug: Bug fixes

- :gear: fixed: change htmx style from html.
- :gear: fixed: move main_contant css style to new file.
- :gear: fixed: move notifications template location.
- :gear: fixed: change create workflow form.
- :gear: fixed: fix logic of toggle theme.
- :gear: fixed: fix logic of toggle sidebar.
- :gear: fixed: change mapped type on models.
- :gear: fixed: change trace schema.

### :black_nib: Code Changes

- :construction: format: update typehint of initial module.
- :test_tube: tests: migrate mocking data to initial file.
- :art: styled: add graph view for workflow detail.
- :art: styled: revise notification page.
- :test_tube: tests: update venv lib on local.
- :art: format: change code with AI version 02
- :art: format: change code with AI version 01
- :construction: refactored: ⬆ deps: bump ddeutil-workflow from 0.0.58 to 0.0.67 (#48)
- :construction: refactored: ⬆ deps: bump uvicorn from 0.34.2 to 0.34.3 (#47)
- :construction: refactored: ⬆ deps: bump sqlalchemy from 2.0.40 to 2.0.41 (#46)
- :construction: refactored: ⬆ deps: bump uvicorn from 0.34.0 to 0.34.2 (#44)
- :construction: refactored: ⬆ deps: bump ddeutil-workflow from 0.0.41 to 0.0.58 (#43)
- :construction: refactored: ⬆ deps: bump python-dotenv from 1.0.1 to 1.1.0 (#39)
- :construction: refactored: ⬆ deps: bump pytest-asyncio from 0.25.3 to 0.26.0 (#41)
- :construction: refactored: ⬆ deps: bump sqlalchemy from 2.0.38 to 2.0.40 (#40)
- :construction: refactored: ⬆ deps: bump ddeutil-workflow from 0.0.36 to 0.0.39 (#38)
- :construction: refactored: ⬆ deps: bump fastapi from 0.115.10 to 0.115.12 (#37)
- :art: styled: resize sidebar menu.
- :art: styled: add skeleton loading on workflow detail.

### :package: Build & Workflow

- :toolbox: build: remove ignore file for cursur agent.
- :toolbox: build: ignore sampling data on static folder.

### :postbox: Dependencies

- :pushpin: deps: update ddeutil-workflow version to 0.0.78.
- :pushpin: deps: update greenlet deps.
- :pushpin: deps: update ddeutil-workflow from 0.0.35 to 0.0.36.

### :book: Documentations

- :page_facing_up: docs: update readme file.
- :page_facing_up: docs: move ai gen docs to docs dir.

## 0.0.7

### :stars: Highlight Features

- :star: hl: move static and template path to src.

### :sparkles: Features

- :dart: feat: add dynamic active on sidebar.
- :dart: feat: move base model to models module.
- :dart: feat: add associate models support role and group.

### :bug: Bug fixes

- :gear: fixed: change log to trace.
- :gear: fixed: change filename of model testcase that was deleted.
- :gear: fixed: revise route module name.

### :black_nib: Code Changes

- :art: styled: add history metadata on workflow page.
- :construction: Feature: redesign uxui and authentication flow on this app (#35)
- :construction: refactored: ⬆ deps: bump jinja2 from 3.1.5 to 3.1.6 (#36)
- :construction: refactored: ⬆ deps: bump fastapi from 0.115.8 to 0.115.10 (#34)
- :construction: refactored: ⬆ deps: bump bcrypt from 4.2.1 to 4.3.0 (#33)
- :test_tube: tests: update associate table for role and policy.
- :test_tube: tests: models policy testcase.
- :test_tube: tests: config pytest logging level to info.
- :test_tube: tests: seperate testcase for models.
- :test_tube: tests: update fixure for database.
- :test_tube: tests: update db testcase.
- :fast_forward: merge: branch 'main' of https://github.com/ddeutils/ddeutil-observe.
- :construction: refactored: ⬆ deps: bump aiosqlite from 0.20.0 to 0.21.0 (#31)

### :broom: Deprecate & Clean

- :recycle: clean: change | to optional and union type hint.

## 0.0.6

### :sparkles: Features

- :dart: feat: remove ruff config on this project.
- :dart: feat: add config database.

### :bug: Bug fixes

- :gear: fixed: secret key does not fix value.
- :gear: fixed: change config object from class attrs to property.

### :black_nib: Code Changes

- :art: styled: change format of layout.
- :package: refactored: bump sqlalchemy from 2.0.36 to 2.0.38 (#30)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.12.3 to 1.12.4 (#29)
- :package: refactored: bump httpx from 0.27.2 to 0.28.1 (#27)
- :package: refactored: bump bcrypt from 4.2.0 to 4.2.1 (#26)
- :package: refactored: bump fastapi from 0.115.6 to 0.115.8 (#25)
- :package: refactored: bump jinja2 from 3.1.4 to 3.1.5
- :package: refactored: bump uvicorn from 0.32.0 to 0.34.0 (#21)
- :package: refactored: bump python-multipart from 0.0.12 to 0.0.20
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.10.2 to 1.12.3
- :package: refactored: bump fastapi from 0.115.0 to 0.115.6
- :package: refactored: bump pyjwt from 2.9.0 to 2.10.1
- :package: refactored: bump sqlalchemy from 2.0.35 to 2.0.36
- :package: refactored: update ddeutil requirement from <0.4.0,>=0.3.8 to >=0.3.8,<0.5.0
- :package: refactored: bump uvicorn from 0.31.0 to 0.32.0
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.10.0 to 1.10.2
- :package: refactored: bump uvicorn from 0.30.6 to 0.31.0
- :package: refactored: bump python-multipart from 0.0.9 to 0.0.12
- :package: refactored: bump sqlalchemy from 2.0.34 to 2.0.35
- :art: styled: add media dynamic support for screen 1200px.
- :art: styled: add sidebar and toc.
- :art: styled: adjust css style for nesting format.
- :art: styled: change css style to nesting.

### :broom: Deprecate & Clean

- :recycle: clean: add workflow logs and audits folders on gitignore.

### :package: Build & Workflow

- :toolbox: build: adjust clishelf config.
- :toolbox: build: update clishelf version from 0.2.4 to 0.2.19.

### :postbox: Dependencies

- :pushpin: deps: update ddeutil-workflow deps for this project.
- :pushpin: deps: update perf optional dependency for improve fastapi perf.
- :pushpin: deps: update ddeutil[all]>=0.4.3,<0.5.0.
- :pushpin: deps: update ddeutil>=0.3.8,<0.5.0.

## 0.0.5

### :sparkles: Features

- :dart: feat: add title change on auth and workflow page. (_2024-09-20_)

### :black_nib: Code Changes

- :art: styled: fixed margin top of auth form. (_2024-09-23_)
- :art: styled: add authentication form. (_2024-09-23_)
- :art: styled: move all css for sidebar to its file. (_2024-09-23_)
- :art: styled: change main page with new sidebar and navbar. (_2024-09-21_)

### :package: Build & Workflow

- :toolbox: build: update supported python version for 3.13. (_2024-09-16_)

### :postbox: Dependencies

- :pushpin: deps: update fastapi version to 0.115.0. (_2024-09-20_)
- :pushpin: deps: update dependency that do not use yet. (_2024-09-17_)

## 0.0.4

### :sparkles: Features

- :dart: feat: add dynamic nav bar with current session user state. (_2024-09-16_)
- :dart: feat: add oauth middleware for checking this session has authorize. (_2024-09-16_)

### :bug: Fix Bugs

- :gear: fixed: remove access token when use fontend page. (_2024-09-16_)

### :postbox: Dependencies

- :pushpin: deps: add workflows test for python version 3.13. (_2024-09-16_)

## 0.0.3

### :sparkles: Features

- :dart: feat: seperate getting token on frontend page and api. (_2024-09-15_)
- :dart: feat: redirect to workflows page if user already register. (_2024-09-14_)
- :dart: feat: change default value of datetime that use on server side. (_2024-09-14_)
- :dart: feat: migrate sync database interface to full async. (_2024-09-13_)
- :dart: feat: add session event listener. (_2024-09-12_)
- :dart: feat: add verify token function on deps. (_2024-09-08_)

### :black_nib: Code Changes

- :test_tube: tests: add testcase for access and refresh token funcs. (_2024-09-16_)
- :art: styled: change style of sidebar. (_2024-09-14_)
- :art: styled: change color and pointer that use border line. (_2024-09-14_)
- :art: styled: add border line for debug component on frontend page. (_2024-09-13_)
- :construction: refactored: 📦 bump sqlalchemy from 2.0.32 to 2.0.34 (_2024-09-12_)
- :construction: refactored: 📦 bump bcrypt from 3.2.2 to 4.2.0 (_2024-09-12_)
- :art: styled: change html template include layer on base. (_2024-09-08_)

### :card_file_box: Documents

- :page_facing_up: docs: add emoji to readme. (_2024-09-13_)
- :page_facing_up: docs: update readme for config values. (_2024-09-09_)

### :bug: Fix Bugs

- :gear: fixed: change import on workflows route. (_2024-09-14_)
- :gear: fixed: merge change from remote repo. (_2024-09-13_)
- :gear: fixed: logout view does not valid on remove token logic. (_2024-09-08_)

### :postbox: Dependencies

- :pushpin: deps: update version of fastapi to 0.114.1. (_2024-09-12_)

## 0.0.2

### :sparkles: Features

- :dart: feat: update logout feature that update and remove refresh tokens. (_2024-09-08_)
- :dart: feat: add change password botton on main page. (_2024-09-08_)
- :dart: feat: add checkbox on login page. (_2024-09-07_)
- :dart: feat: add sqlalchemy handler route. (_2024-09-06_)
- :dart: feat: add logout feature. (_2024-09-06_)
- :dart: feat: change schema of user that use name instead username. (_2024-09-06_)
- :dart: feat: add reset pass and logout route. (_2024-09-06_)
- :dart: feat: add required authen in workflwos route. (_2024-09-05_)
- :dart: feat: add token auth with scopes. (_2024-09-05_)
- :dart: feat: add api for auth route. (_2024-09-05_)
- :dart: feat: add register page for create user login. (_2024-09-05_)
- :dart: feat: add user auth route. (_2024-09-05_)
- :dart: feat: change base from func to subclass. (_2024-09-05_)
- :dart: feat: add async session. (_2024-09-04_)
- :dart: feat: add create release log crud func. (_2024-09-03_)
- :dart: feat: add crud functions on log route. (_2024-09-02_)
- :dart: feat: add more fields on workflow schemas. (_2024-09-02_)

### :black_nib: Code Changes

- :art: styled: add frontend layout link. (_2024-09-07_)
- :art: styled: change import object systex. (_2024-09-07_)
- :construction: refactored: move models and schemas single file to folder on auth component. (_2024-09-07_)
- :art: styled: add font on layout page. (_2024-09-03_)
- :test_tube: tests: add release log dummy data. (_2024-09-03_)
- :construction: refactored: merge log route to workflow route. (_2024-09-03_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.9.0 to 1.10.0 (_2024-09-02_)
- :test_tube: tests: add init database function for adding dummy data. (_2024-09-02_)

### :card_file_box: Documents

- :page_facing_up: docs: update shields in readme for this project tracking. (_2024-09-02_)

### :bug: Fix Bugs

- :gear: fixed: merge token table together with backlist. (_2024-09-07_)

### :package: Build & Workflow

- :toolbox: build: add dependabot file for deps tracking by github. (_2024-09-02_)

### :postbox: Dependencies

- :pushpin: deps: update fastapi version to 0.114.0. (_2024-09-07_)
- :pushpin: deps: update fastapi to 0.113.0. (_2024-09-06_)
- :pushpin: deps: remove passlib and use bcrypt instead. (_2024-09-06_)
- :pushpin: deps: change jwt package from python-jose to pyjwt. (_2024-09-05_)

## 0.0.1

### :sparkles: Features

- :dart: feat: add searching workflows and display table. (_2024-08-31_)
- :dart: feat: add filter sqlite db files in gitignore. (_2024-08-31_)
- :dart: feat: add logs router. (_2024-08-31_)
- :dart: feat: add logging function to utils module. (_2024-08-30_)
- :dart: feat: add muti-templating folders for apiroute. (_2024-08-29_)
- :dart: feat: add static and midleware in fastapi application. (_2024-08-27_)
- :tada: init: add the first initial code. (_2024-08-09_)

### :black_nib: Code Changes

- :construction: refactored: change name of pipline to workflow. (_2024-09-01_)
- :test_tube: tests: add pytest runner on pre-commit. (_2024-08-31_)
- :test_tube: tests: add testcase for workflow schemas. (_2024-08-31_)
- :art: styled: add main file structures for router. (_2024-08-29_)
- :construction: refactored: Initial commit (_2024-07-25_)

### :card_file_box: Documents

- :page_facing_up: docs: update readme for config topic. (_2024-09-01_)
- :page_facing_up: docs: update description of this project package. (_2024-08-26_)

### :bug: Fix Bugs

- :gear: fixed: remove __init__ on namespace package. (_2024-09-01_)
- :gear: fixed: change models on workflows and logs. (_2024-08-31_)

### :package: Build & Workflow

- :toolbox: build: add public workflow. (_2024-09-01_)

### :postbox: Dependencies

- :pushpin: deps: add httpx package for testing fastapi. (_2024-09-01_)
- :pushpin: deps: renove fasthtml pakcage and use fastapi instead. (_2024-08-27_)
- :pushpin: deps: update fasthtml dependency to 0.4.5. (_2024-08-24_)
- :pushpin: deps: update python-fasthtml to 0.3.3. (_2024-08-12_)
- :pushpin: deps: update python version that was supported with fasthtml. (_2024-08-09_)
