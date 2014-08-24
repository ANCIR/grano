from datetime import datetime

from flask import Blueprint, request
from flask import redirect, make_response

from grano.lib.serialisation import jsonify
from grano.core import app, url_for, app_name, app_version
from grano.views.cache import validate_cache, disable_cache
from grano.background import ping


blueprint = Blueprint('base_api', __name__)
startup_time = datetime.utcnow()
ROBOTS = """
User-agent: *
Sitemap: /static/sitemap.xml
Disallow: /harming/humans
Disallow: /ignoring/human/orders
Disallow: /harm/to/self
"""


@blueprint.route('/robots.txt', methods=['GET'])
def robots_txt():
    validate_cache(last_modified=startup_time)
    res = make_response(ROBOTS)
    res.headers['Content-Type'] = 'text/plain'
    return res


@blueprint.route('/favicon.ico', methods=['GET'])
def favicon_ico():
    validate_cache(last_modified=startup_time)
    ico_url = app.config.get('FAVICON_URL',
        'http://assets.pudo.org/img/favicon.ico')
    return redirect(ico_url)


@blueprint.route('/api', methods=['GET'])
@blueprint.route('/api/1', methods=['GET'])
def status():
    validate_cache(last_modified=startup_time)
    return jsonify({
        'service': app_name,
        'status': 'ok',
        'version': app_version,
        'docs': 'http://granoproject.org/docs',
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
    disable_cache()
    ret = ping.delay(message=request.args.get('message'))
    return jsonify({'status': 'sent', 'task': ret.task_name, 'id': ret.id})
