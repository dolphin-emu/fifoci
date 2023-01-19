# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

from django import template

register = template.Library()

@register.simple_tag
def get_zipped_hashes(current, old):
    current = [] if current is None else current.hashes_list
    old = [] if old is None else old.hashes_list
    length = max(len(current), len(old))
    current += [None] * (length - len(current))
    old += [None] * (length - len(old))
    return zip(current, old)
