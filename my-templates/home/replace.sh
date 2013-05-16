#!/bin/sh
# Wrapper that calls replace.py in the virtualenv

# enable virtualenv
. /home/ckan/pyenv/bin/activate

cd /home/ckan/pyenv/src/ckan/my-templates/home
./replace.py

# exit venv (useless)
# deactivate
