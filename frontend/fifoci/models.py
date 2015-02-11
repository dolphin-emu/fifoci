# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.db import models


class FifoTest(models.Model):
    file = models.FileField(upload_to="dff/", max_length=256)
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=32, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('dff-view', [self.shortname])

    def __str__(self):
        return self.shortname


class Version(models.Model):
    hash = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=64, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, db_index=True)
    parent_hash = models.CharField(max_length=40)
    submitted = models.BooleanField(default=False, db_index=True)
    ts = models.DateTimeField(auto_now_add=True, blank=True, db_index=True)

    @models.permalink
    def get_absolute_url(self):
        return ('version-view', [self.hash])

    def __str__(self):
        return '%s (%s)' % (self.name, self.hash[:8])


class Result(models.Model):
    dff = models.ForeignKey(FifoTest)
    ver = models.ForeignKey(Version, related_name='results')
    type = models.CharField(max_length=64, db_index=True)
    has_change = models.BooleanField(default=False, db_index=True)
    first_result = models.BooleanField(default=False, db_index=True)

    # Format: "h1,h2,h3,...,hN"
    hashes = models.TextField()

    @models.permalink
    def get_absolute_url(self):
        return ('result-view', [self.id])

    @property
    def hashes_list(self):
        return self.hashes.split(',')

    def __str__(self):
        return '%s / %s / %s' % (self.dff, self.ver, self.type)
