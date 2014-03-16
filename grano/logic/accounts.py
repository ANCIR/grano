from grano.core import db, url_for
from grano.model import Account


def save(data, account=None):
    if account is None:
        account = Account()
        account.github_id = data.get('github_id')
        account.twitter_id = data.get('twitter_id')
        account.facebook_id = data.get('facebook_id')
    account.login = data.get('login')
    
    if data.get('full_name'):
        account.full_name = data.get('full_name')
    
    if data.get('email'):
        account.email = data.get('email')
    
    db.session.add(account)
    db.session.flush()
    return account


def console_account(login='_system'):
    account = Account.by_login(login)
    if account is None:
        account = save({
            'login': login,
            'email': None,
            'full_name': 'System Operations'
            })
    return account


def to_rest_index(account):
    return {
        'id': account.id,
        'api_url': url_for('accounts_api.view', id=account.id),
        'display_name': account.display_name
        }

def to_rest(account):
    data = to_rest_index(account)
    data['login'] = account.login
    data['full_name'] = account.full_name
    data['github_id'] = account.github_id
    data['twitter_id'] = account.twitter_id
    data['facebook_id'] = account.facebook_id
    data['created_at'] = account.created_at 
    data['updated_at'] = account.updated_at
    data['email'] = account.email
    return data
