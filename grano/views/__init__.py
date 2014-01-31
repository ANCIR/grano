from grano.core import app
from grano.views.seo import seo

app.register_blueprint(seo)
