from base64 import b85encode
from django.template import Library


register = Library()


@register.filter
def base65(s):
    return b85encode(str(s).encode())
