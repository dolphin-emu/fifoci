from fabric.api import *

env.user = 'fifoci'
env.hosts = ['underlord.dolphin-emu.org']

def deploy():
    with cd("/home/fifoci/fifoci"):
        run("git fetch")
        run("git checkout master")
        run("git reset --hard origin/master")
        with cd("/home/fifoci/fifoci/frontend"):
            run("~/python manage.py collectstatic --noinput")
            run("pkill -HUP gunicorn")
