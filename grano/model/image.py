from grano.core import db
from grano.model.common import IntBase


class ImageConfig(db.Model, IntBase):
    __tablename__ = 'grano_imageconfig'
    __table_args__ = (db.UniqueConstraint('name', 'project_id'), )

    name = db.Column(db.Unicode())
    label = db.Column(db.Unicode())
    description = db.Column(db.Unicode())

    project_id = db.Column(db.Integer(), db.ForeignKey('grano_project.id'))

    height = db.Column(db.Integer())
    width = db.Column(db.Integer())
    crop_origin_x = db.Column(db.Integer())
    crop_origin_y = db.Column(db.Integer())

    files = db.relationship('File', backref='image_config', lazy='dynamic')

    @classmethod
    def by_project_and_name(cls, project, name):
        q = db.session.query(cls)
        q = q.filter_by(project=project)
        q = q.filter_by(name=name)
        return q.one()

    def to_dict_index(self):
        return {
            'id': self.id,
            'project': self.project.to_dict_index(),
            'name': self.name,
            'label': self.label,
            'description': self.description,
            'height': self.height,
            'width': self.width,
            'crop_origin_x': self.crop_origin_x,
            'crop_origin_y': self.crop_origin_y
        }

    def to_dict(self):
        return self.to_dict_index()
