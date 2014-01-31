import logging
import os

from flask import render_template

from grano.core import app
from grano.model import Entity


log = logging.getLogger(__name__)


def generate_sitemap(count=20000):
    """ Generate a static sitemap.xml for the most central entities in the 
    database. """

    PATTERN = app.config.get('ENTITY_VIEW_PATTERN')
    
    entities = []
    for i, entity in enumerate(Entity.all().yield_per(5000)):
        dt = entity.updated_at.strftime('%Y-%m-%d')
        entities.append((PATTERN % entity.id, dt, entity.degree))
        if i > 0 and i % 1000 == 0:
            log.info("Loaded %s entities...", i)

    upper = max([e[2] for e in entities])
    entities = sorted(entities, key=lambda e: e[2], reverse=True)[:count]
    entities = [(i, d, '%.2f' % (float(s)/upper)) for (i,d,s) in entities]

    xml = render_template('sitemap.xml', entities=entities)
    with open(os.path.join(app.static_folder, 'sitemap.xml'), 'w') as fh:
        fh.write(xml)

