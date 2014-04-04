from grano.core import db, url_for
from grano.model.common import IntBase


class Permission(db.Model, IntBase):
    __tablename__ = 'grano_permission'

    reader = db.Column(db.Boolean)
    editor = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)

    account_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))

    @classmethod
    def by_project_and_id(cls, project, id):
        q = db.session.query(cls).filter_by(id=id)
        q = q.filter_by(project=project)
        return q.first()


    def to_dict_index(self):
        return {
            'id': self.id,
            'reader': self.reader,
            'editor': self.editor,
            'admin': self.admin,
            'project': self.project.to_dict_index(),
            'account': self.account.to_dict_index(),
            'api_url': url_for('permissions_api.view', slug=self.project.slug, id=self.id)
            }


    def to_dict(self):
        return self.to_dict_index()
