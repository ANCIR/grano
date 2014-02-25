from grano.core import db
from grano.model import Account


def create(data, account=None):
    if account is None:
        account = Account()
        account.github_id = data.get('github_id')
        account.twitter_id = data.get('twitter_id')
        account.facebook_id = data.get('facebook_id')
    account.login = data.get('login')
    account.full_name = data.get('full_name')
    account.email = data.get('email')
    db.session.add(account)
    db.session.flush()
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
        'full_name': account.full_name
        }

def to_rest(account):
    data = to_rest_index(account)
    data['github_id'] = account.github_id
    data['twitter_id'] = account.twitter_id
    data['facebook_id'] = account.facebook_id
    data['created_at'] = account.created_at 
    data['updated_at'] = account.updated_at
    return data
