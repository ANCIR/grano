from grano.core import db, url_for
from grano.model.common import IntBase


class File(db.Model, IntBase):
    __tablename__ = 'grano_file'

    file_name = db.Column(db.Unicode)
    mime_type = db.Column(db.Unicode)

    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    data = db.Column(db.LargeBinary)


    def to_dict_index(self):
        return {
            'id': self.id,
            'project': self.project.to_dict_index(),
            'api_url': url_for('files_api.view', id=self.id),
            'serve_api_url': url_for('files_api.serve', id=self.id),
            'file_name': self.file_name,
            'mime_type': self.mime_type
        }


    def to_dict(self):
        """ Full serialization of the file metadata. """
        return self.to_dict_index()
