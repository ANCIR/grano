import os 

from flask import render_template
from flask.ext.login import LoginManager
from flask.ext.browserid import BrowserID

#from formencode import Invalid

from grano.core import app
from grano.model import User

from grano.views.sessions import blueprint as sessions
from grano.views.users import blueprint as users
from grano.views.projects import blueprint as projects

login_manager = LoginManager()
login_manager.user_loader(User.by_email)
login_manager.init_app(app)

browser_id = BrowserID()
browser_id.user_loader(User.from_browserid)
browser_id.init_app(app)

app.register_blueprint(sessions, url_prefix='/api/1')
app.register_blueprint(users, url_prefix='/api/1')
app.register_blueprint(projects, url_prefix='/api/1')


def angular_templates():
    #if app.config.get('ASSETS_DEBUG'):
    #    return
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                yield ('/static/templates/%s' % file_path[len(partials_dir)+1:],
                       fh.read().decode('utf-8'))

@app.route("/")
def index(path=None):
    return render_template('layout.html', angular_templates=angular_templates())
