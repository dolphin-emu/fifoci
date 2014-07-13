from django import template

register = template.Library()

@register.assignment_tag
def get_zipped_hashes(current, old):
    current = [] if current is None else current.hashes_list
    old = [] if old is None else old.hashes_list
    length = max(len(current), len(old))
    current += [None] * (length - len(current))
    old += [None] * (length - len(old))
    return zip(current, old)
