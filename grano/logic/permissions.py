import colander

from grano.core import db, url_for
from grano.model import Permission
from grano.logic import accounts as accounts_logic
from grano.logic import projects as projects_logic
from grano.logic.validation import Invalid
from grano.logic.references import ProjectRef, AccountRef


class PermissionValidator(colander.MappingSchema):
    project = colander.SchemaNode(ProjectRef())
    account = colander.SchemaNode(AccountRef())
    reader = colander.SchemaNode(colander.Boolean(), missing=False)
    editor = colander.SchemaNode(colander.Boolean(), missing=False)
    admin = colander.SchemaNode(colander.Boolean(), missing=False)


def save(data, permission=None):
    validator = PermissionValidator()
    data = validator.deserialize(data)

    if permission is None:
        q = Permission.all()
        q = q.filter(Permission.project==data['project'])
        q = q.filter(Permission.account==data['account'])
        permission = q.first()

    if permission is None:
        permission = Permission()
        permission.project = data.get('project')
        permission.account = data.get('account')
    
    permission.reader = data['reader'] or data['editor'] or data['admin']
    permission.editor = data['editor'] or data['admin']
    permission.admin = data['admin']
    
    db.session.add(permission)
    db.session.flush()
    return permission


def delete(permission):
    db.session.delete(permission)
    db.session.flush()
