from mongoengine import Document, DateTimeField
from datetime import datetime

class GranoDocument(Document):
    meta = {
        'abstract': True,
    }

    created_at = DateTimeField(default=datetime.utcnow, required=True)
    updated_at = DateTimeField(default=datetime.utcnow, required=True)
    
    def to_json(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }


class ModelException(Exception):
    pass


class ObjectExists(ModelException):
    pass