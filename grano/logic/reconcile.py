from sqlalchemy import func, cast, types
from sqlalchemy.orm import aliased

from grano.interface import Startup
from grano.model import Entity, Property, Schema
from grano.core import db


class Matches(object):

    def __init__(self, q, project, account):
        self.lq = self.q = q
        self.account = account
        self.project = project

    def limit(self, l):
        self.lq = self.lq.limit(l)
        return self

    def offset(self, o):
        self.lq = self.lq.offset(o)
        return self

    def count(self):
        return self.q.count()

    def __iter__(self):
        rows = self.lq.all()
        ids = [r[0] for r in rows]
        q = db.session.query(Entity)
        q = q.filter(Entity.project == self.project)
        q = q.filter(Entity.id.in_(ids))
        by_id = {}
        for entity in q.all():
            by_id[entity.id] = entity
        for (id, score) in rows:
            yield {
                'score': int(score),
                'entity': by_id.get(id)
            }


def find_matches(project, account, text, schemata=[], properties=[]):
    main = aliased(Property)
    ent = aliased(Entity)
    q = db.session.query(main.entity_id)
    q = q.filter(main.name == 'name')
    q = q.filter(main.entity_id == ent.id)
    q = q.join(ent)
    q = q.filter(ent.project_id == project.id)

    if len(schemata):
        obj = aliased(Schema)
        q = q.join(obj, ent.schema_id == obj.id)
        q = q.filter(obj.name.in_(schemata))

    for name, value in properties:
        p = aliased(Property)
        q = q.join(p, p.entity_id == ent.id)
        q = q.filter(p.active == True) # noqa
        q = q.filter(p.name == name)
        column = getattr(p, p.type_column(value))
        q = q.filter(column == value)

    # prepare text fields (todo: further normalization!)
    text_field = func.left(func.lower(main.value_string), 254)
    match_text = text.lower().strip()[:254]
    match_text_db = cast(match_text, types.Unicode)

    # calculate the difference percentage
    l = func.greatest(1.0, func.least(len(match_text), func.length(text_field)))
    score = func.greatest(0.0, ((l - func.levenshtein(text_field, match_text_db)) / l) * 100.0)
    score = score.label('score')
    q = q.group_by(main.entity_id)
    q = q.add_columns(func.max(score))
    q = q.order_by(func.max(score).desc())
    q = q.filter(score > 50)
    return Matches(q, project, account)


class ConfigurePostgres(Startup):

    def configure(self, manager):
        ext = "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;"
        db.session.execute(ext)
        db.session.commit()
