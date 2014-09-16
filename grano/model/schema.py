from grano.core import db, url_for
from grano.model.common import IntBase
from grano.model.util import MutableDict, JSONEncodedDict
from grano.model.attribute import Attribute


ENTITY_DEFAULT = 'Entity'
RELATION_DEFAULT = 'Relation'


class Schema(db.Model, IntBase):
    __tablename__ = 'grano_schema'

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    hidden = db.Column(db.Boolean())
    obj = db.Column(db.Unicode())
    meta = db.Column(MutableDict.as_mutable(JSONEncodedDict))
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('grano_schema.id'),
                          nullable=True)

    local_attributes = db.relationship(Attribute, backref='schema',
                                       lazy='dynamic',
                                       cascade='all, delete, delete-orphan')
    relations = db.relationship('Relation', backref='schema', lazy='dynamic',
                                cascade='all, delete, delete-orphan')
    entities = db.relationship('Entity', backref='schema', lazy='dynamic',
                               cascade='all, delete, delete-orphan')
    children = db.relationship('Schema', lazy='dynamic',
                               backref=db.backref('parent',
                                                  remote_side='Schema.id'))

    @property
    def inherited_attributes(self):
        if self.parent is None:
            return []
        return self.parent.attributes

    @property
    def attributes(self):
        return list(self.local_attributes) + self.inherited_attributes

    def get_attribute(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute

    def is_circular(self, path=None):
        if path is None:
            path = []
        if self.name in path:
            return True
        elif self.parent is None:
            return False
        else:
            path.append(self.name)
            return self.parent.is_circular(path)

    def is_parent(self, other):
        if self.parent is None:
            return False
        if self.parent == other:
            return True
        return self.parent.is_parent(other)

    def common_parent(self, other):
        if self == other or self.is_parent(other):
            return self
        return self.common_parent(other.parent)

    @classmethod
    def by_name(cls, project, name):
        q = db.session.query(cls).filter_by(name=name)
        q = q.filter_by(project=project)
        return q.first()

    @classmethod
    def by_obj_name(cls, project, obj, name):
        q = db.session.query(cls)
        q = q.filter_by(project=project)
        q = q.filter_by(name=name)
        q = q.filter_by(obj=obj)
        return q.first()

    def to_dict_index(self):
        return {
            'name': self.name,
            'label': self.label,
            'hidden': self.hidden,
            'meta': self.meta,
            'obj': self.obj,
            'api_url': url_for('schemata_api.view',
                               slug=self.project.slug,
                               name=self.name)
        }

    def to_dict(self):
        data = self.to_dict_index()
        data['id'] = self.id
        if self.parent is not None:
            data['parent'] = self.parent.to_dict_index()
        else:
            data['parent'] = None
        data['project'] = self.project.to_dict_index()
        data['attributes'] = [a.to_dict() for a in self.local_attributes]
        for attr in self.inherited_attributes:
            d = attr.to_dict()
            d['inherited'] = True
            data['attributes'].append(d)
        return data
