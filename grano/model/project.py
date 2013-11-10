from flask import url_for
from mongoengine import StringField

from grano.model.util import GranoDocument


class Project(GranoDocument):
    label = StringField(min_length=2, max_length=200)
    slug = StringField(min_length=2, max_length=200)
    description = StringField(min_length=2)

    @property
    def api_uri(self):
        return url_for('projects.get', slug=self.slug, _external=True)

    @classmethod
    def by_slug(cls, slug):
        return cls.objects(slug=slug).first()

    def to_json(self):
        data = super(Project, self).to_json()
        data['label'] = self.label
        data['slug'] = self.slug
        return data

