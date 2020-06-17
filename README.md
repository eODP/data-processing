# eODP Data Processing

Scripts to process eODP data.

## Setup

We are using Python 3.6.8 on the production server.

For the dev environment, we are using [pyenv](https://github.com/pyenv/pyenv)
to run Python 3.6.8, pip to manage packages, and
[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to manage virtual
environments. We are also using JupyterLab to process the raw data.

(1) Install pyenv, pyenv-virtualenv, jupyterlab

(2) Install Python 3.6.8

```bash
pyenv install 3.6.8
```

set this directory to use Python 3.6.8

```bash
pyenv local 3.6.8
```

(3) Start virtual environment

create virtual environment

```bash
pyenv virtualenv 3.6.8 <venv-name>
```

set this directory to use `<venv-name>` virtual environment

```bash
pyenv local <venv-name>
```

(4) Install packages.

```bash
pip install -r requirements.txt
```

(5) Config .env file

Copy `.env-example` and rename it `.env`.

Fill in the missing environmental variables.

(6) Install additional packages

```bash
pip install <package>

pip freeze > requirements.txt
```

## Run Scripts

Start JupyterLab to run data processing scripts. We are using JupyterLab instead
of plain Jupyter notebooks because JupyterLab lets you easily browse the data
files while working.

```bash
cd notebooks
jupyter lab
```

## Testing

Run tests

```bash
pytest
```

Run linter (flake8) and code formatter (Black).

```bash
python scripts/linter.py
```

## Deploy

We are using rsync to sync the files to the live server

```bash
./deploy.sh user@live.server.host
```
