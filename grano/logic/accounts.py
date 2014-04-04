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
    """ Create the default system account. """
    account = Account.by_login(login)
    if account is None:
        account = save({
            'login': login,
            'email': None,
            'full_name': 'System Operations'
            })
    return account
