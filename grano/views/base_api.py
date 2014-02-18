from flask import Blueprint, render_template, request
from flask import redirect, make_response, url_for

from grano import __version__
from grano.lib.serialisation import jsonify
from grano.core import app, url_for, app_name
from grano.background import ping


blueprint = Blueprint('base_api', __name__)

ROBOTS = """
User-agent: *
Sitemap: /static/sitemap.xml
"""


@blueprint.route('/robots.txt', methods=['GET'])
def robots_txt():
    res = make_response(ROBOTS)
    res.headers['Content-Type'] = 'text/plain'
    return res


@blueprint.route('/favicon.ico', methods=['GET'])
def favicon_ico():
    ico_url = app.config.get('FAVICON_URL',
        'http://assets.pudo.org/img/favicon.ico')
    return redirect(ico_url)


@blueprint.route('/api', methods=['GET'])
@blueprint.route('/api/1', methods=['GET'])
def status():
    return jsonify({
        'service': app_name,
        'status': 'ok',
        'version': __version__,
        'docs': 'http://grano.pudo.org/rest_api.html',
        'api_url': url_for('base_api.status'),
        'services': {
            'projects_index_url': url_for('projects_api.index'),
            'entities_index_url': url_for('entities_api.index'),
            'relations_index_url': url_for('relations_api.index'),
            'sessions_status_url': url_for('sessions_api.status')
        }
    })


@blueprint.route('/api/1/ping', methods=['GET'])
def queue_ping():
    ret = ping.delay(message=request.args.get('message'))
    return jsonify({'status': 'sent', 'task': ret.task_name, 'id': ret.id})
