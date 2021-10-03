# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django.db import models
from django.urls import reverse


class FifoTest(models.Model):
    file = models.FileField(upload_to="dff/", max_length=256)
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=32, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse('dff-view', args=[self.shortname])

    def __str__(self):
        return self.shortname


class Version(models.Model):
    hash = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=64, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, db_index=True, on_delete=models.CASCADE)
    parent_hash = models.CharField(max_length=40)
    submitted = models.BooleanField(default=False, db_index=True)
    ts = models.DateTimeField(auto_now_add=True, blank=True, db_index=True)

    def get_absolute_url(self):
        return reverse('version-view', args=[self.hash])

    def __str__(self):
        return '%s (%s)' % (self.name, self.hash[:8])


class Type(models.Model):
    type = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.type


class Result(models.Model):
    dff = models.ForeignKey(FifoTest, on_delete=models.CASCADE)
    ver = models.ForeignKey(Version, related_name='results', on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    has_change = models.BooleanField(default=False)
    first_result = models.BooleanField(default=False)

    # Format: "h1,h2,h3,...,hN"
    hashes = models.TextField()

    def get_absolute_url(self):
        return reverse('result-view', args=[self.id])

    @property
    def hashes_list(self):
        return self.hashes.split(',')

    def __str__(self):
        return '%s / %s / %s' % (self.dff, self.ver, self.type)
