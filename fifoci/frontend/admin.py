# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.contrib import admin
from .models import FifoTest, Result, Version

admin.site.register(FifoTest)
admin.site.register(Result)
admin.site.register(Version)
