from flask import Blueprint, render_template, request
from flask import redirect, make_response, url_for

from grano import __version__
from grano.lib.serialisation import jsonify
from grano.core import app, url_for, app_name
from grano.background import ping


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


@base_api.route('/api')
@base_api.route('/api/1')
def status():
    return jsonify({
        'service': app_name,
        'status': 'ok',
        'version': __version__,
        'docs': 'http://grano.pudo.org/api.html',
        'api_url': url_for('base_api.status'),
        'services': {
            'entities_index_url': url_for('entities_api.index'),
            'relations_index_url': url_for('relations_api.index'),
            'schemata_index_url': url_for('schemata_api.index')
        }
    })


@base_api.route('/api/1/ping')
def queue_ping():
    ret = ping.delay(message=request.args.get('message'))
    return jsonify({'status': 'sent', 'task': ret.task_name, 'id': ret.id})
