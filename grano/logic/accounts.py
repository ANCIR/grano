from grano.core import db
from grano.model import Account


def create(data):
    account = Account()
    account.github_id = data['id']
    account.login = data['login']
    account.email = data.get('email')
    db.session.add(account)
    db.session.flush()
    return account


def update(account, data):
    account.login = data['login']
    account.email = data.get('email')
    db.session.add(account)
    return account


def console_account(login='_system'):
    account = Account.by_login(login)
    if account is None:
        account = create({'login': login, 'id': None, 'email': None})
    return account


def to_rest(account):
    return {
        'id': account.id,
        'github_id': account.github_id,
        'login': account.login,
        'created_at': account.created_at, 
        'updated_at': account.updated_at,
        }
