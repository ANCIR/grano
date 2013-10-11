from flask import request, session, render_template
from flask.ext.login import LoginManager
from flask.ext.browserid import BrowserID

#from formencode import Invalid

from grano.core import app
from grano.model import user

login_manager = LoginManager()
login_manager.user_loader(user.login_by_email)
login_manager.init_app(app)

browser_id = BrowserID()
browser_id.user_loader(user.login_by_browserid)
browser_id.init_app(app)


@app.route("/")
def index(path=None):
    return render_template('layout.html')
