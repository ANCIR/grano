from datetime import datetime

from mongoengine import Document, DateTimeField
from mongoengine import signals

class GranoDocument(Document):
    meta = {
        'abstract': True,
    }

    created_at = DateTimeField(default=datetime.utcnow, required=True)
    updated_at = DateTimeField(default=datetime.utcnow, required=True)
    
    def to_json(self):
        data = {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }
        if hasattr(self, 'api_uri'):
            data['api_uri'] = self.api_uri
        if hasattr(self, 'external_uri'):
            data['external_uri'] = self.external_uri
        return data


def pre_save(sender, document, **kw):
    if hasattr(document, 'updated_at'):
        document.updated_at = datetime.utcnow()


signals.pre_save.connect(pre_save)


class ModelException(Exception):
    pass


class ObjectExists(ModelException):
    pass

