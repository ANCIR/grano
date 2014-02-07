from flask import Blueprint, render_template
from flask import redirect, make_response

from grano.core import app


base_api = Blueprint('base_api', __name__)

ROBOTS = """
User-agent: *
Sitemap: /static/sitemap.xml
"""


@base_api.route('/robots.txt')
def robots_txt():
    res = make_response(ROBOTS)
    res.headers['Content-Type'] = 'text/plain'
    return res


@base_api.route('/favicon.ico')
def favicon_ico():
    ico_url = app.config.get('FAVICON_URL',
        'http://assets.pudo.org/img/favicon.ico')
    return redirect(ico_url)
