from django import template

register = template.Library()

@register.assignment_tag
def get_zipped_hashes(current, old):
    if old and old.hashes:
        return zip(current.hashes_list, old.hashes_list)
    else:
        return zip(current.hashes_list, [None] * len(current.hashes_list))
