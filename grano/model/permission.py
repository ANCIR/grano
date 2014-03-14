from grano.core import db
from grano.model.common import IntBase


class Permission(db.Model, IntBase):
    __tablename__ = 'permission'

    reader = db.Column(db.Boolean)
    editor = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    @classmethod
    def by_project_and_id(cls, project, id):
        q = db.session.query(cls).filter_by(id=id)
        q = q.filter_by(project=project)
        return q.first()
