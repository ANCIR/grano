from flask import Blueprint, render_template, make_response


seo = Blueprint('seo', __name__)

ROBOTS = """
User-agent: *
Sitemap: /static/sitemap.xml
"""

@seo.route('/robots.txt')
def robots_txt():
    res = make_response(ROBOTS)
    res.headers['Content-Type'] = 'text/plain'
    return res

