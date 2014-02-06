import requests
import logging
import json
import dataset

from grano.core import app, db
from grano.model import Entity, Schema
from grano.logic import properties
from grano.interface import EntityChangeProcessor


log = logging.getLogger(__name__)


class OpenCorporatesCanonicalizer(EntityChangeProcessor):

    def __init__(self):
        self.api_endpoint = app.config.get('OPENCORPORATES_URL',
            'http://opencorporates.com/reconcile')
        self.api_key = app.config.get('OPENCORPORATES_APIKEY')
        score_limit = app.config.get('OPENCORPORATES_SCORE_LIMIT', 90)
        self.score_limit = int(score_limit)
        self.schemata = app.config.get('OPENCORPORATES_SCHEMATA')
        self.cache_uri = app.config.get('OPENCORPORATES_CACHE_URI')
        if self.cache_uri is not None:
            self.cache = dataset.connect(self.cache_uri)['opencorporates_cache']
        self.country_code_field = app.config.get('OPENCORPORATES_COUNTRY_CODE')
        self.session = requests.Session()


    def entity_changed(self, entity_id):
        entity = Entity.by_id(entity_id)

        # check if the entity has a company-style schema
        schemata = [s.name for s in entity.schemata \
                    if s.name in self.schemata]
        if not len(schemata):
            return

        # check if there's already a recon match
        names = [prop for prop in entity.properties if prop.name == 'name']
        for name_prop in names:
            if name_prop.source_url is None:
                continue
            if name_prop.source_url.startswith('http://opencorporates.com/'):
                return

        country_code = None
        if self.country_code_field and entity[self.country_code_field]:
            country_code = entity[self.country_code_field].value.lower()

        matches = []
        for name_prop in names:
            matches.append(self.reconcile(name_prop.value, country_code))
        best_match = max(matches, key=lambda m: m.get('score'))

        if best_match.get('score') >= self.score_limit:
            log.info('OpenCorporates Lookup: %s -> %s',
                best_match['name'], best_match['canonical'])
            schema = Schema.cached(Entity, 'base')
            properties.set(entity, 'name', schema, best_match['canonical'],
                source_url=best_match['uri'])
            properties.set(entity, 'opencorporates_uri', schema, best_match['uri'],
                source_url=best_match['uri'])
            db.session.commit()


    def reconcile(self, name, country_code):
        if self.cache_uri is not None:
            data = self.cache.find_one(name=name, country=country_code)
            if data is not None:
                return data

        url = self.api_endpoint
        if country_code is not None:
            url = url + '/%s' % country_code

        query = json.dumps({'query': name, 'limit': 1})
        res = self.session.get(url, params={'query': query})
        data = {'name': name, 'country': country_code,
            'canonical': None, 'uri': None, 'score': 0}
        if res.ok and len(res.json().get('result')):
            r = res.json().get('result').pop()
            data['canonical'] = r['name']
            data['uri'] = r['uri']
            data['score'] = r['score']

        if self.cache_uri is not None:
            self.cache.insert(data)
        
        return data
        


