from grano.core import db
from grano.model.common import IntBase


class File(db.Model, IntBase):
    __tablename__ = 'grano_file'

    file_name = db.Column(db.Unicode)
    mime_type = db.Column(db.Unicode)

    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    data = db.Column(db.LargeBinary)

