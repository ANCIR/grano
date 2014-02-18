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


def to_rest_index(account):
    return {
        'id': account.id,
        'login': account.login,
        }

def to_rest(account):
    data = to_rest_index(account)
    data['github_id'] = account.github_id
    data['created_at'] = account.created_at 
    data['updated_at'] = account.updated_at
    return data
