from functools import wraps
from flask import request, url_for, g


class Pagination(object):

    def __init__(self, app=None):

        if app:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.globals['url_for_other_page'] = url_for_other_page
        self.app = app


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def paginate(f):

    PAGE_DEFAULT = 1
    PAGE_SIZE_DEFAULT = 20
    PAGE_SIZE_MAX = 50

    @wraps(f)
    def decorated(*args, **kwargs):

        page = request.args.get('page', PAGE_DEFAULT)
        page = page if (is_int(page) and int(page) >= 1) else PAGE_DEFAULT

        s = request.args.get('page_size', PAGE_SIZE_DEFAULT)

        if not (is_int(s) and int(s) >= 1 and int(s) <= PAGE_SIZE_MAX):
            s = PAGE_SIZE_DEFAULT

        kwargs['page'] = int(page)
        kwargs['page_size'] = int(s)

        g._bed_page = int(page)
        g._bed_page_size = int(s)

        return f(*args, **kwargs)
    return decorated


def url_for_other_page(page):
    args = dict(request.view_args.items() + request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)
