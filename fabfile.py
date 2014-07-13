# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from fabric.api import *

env.user = 'fifoci'
env.hosts = ['underlord.dolphin-emu.org']

def deploy():
    with cd("/home/fifoci/fifoci"):
        run("git fetch")
        run("git checkout master")
        run("git reset --hard origin/master")
        run("~/pip install -r requirements.txt")
        with cd("/home/fifoci/fifoci/frontend"):
            run("~/python manage.py collectstatic --noinput")
            run("pkill -HUP gunicorn")
