import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from django.conf import settings


def get_plaid_client():
    env_map = {
        'sandbox': 'https://sandbox.plaid.com',
        'development': 'https://development.plaid.com',
        'production': 'https://production.plaid.com',
    }
    env = env_map.get(settings.PLAID_ENV, 'https://sandbox.plaid.com')
    configuration = plaid.Configuration(
        host=env,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET,
        }
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token(user_id):
    if not settings.PLAID_CLIENT_ID or not settings.PLAID_SECRET:
        raise ValueError("Plaid API keys not configured")
    client = get_plaid_client()
    request = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Finio",
        country_codes=[CountryCode('US')],
        language='en',
        user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
    )
    response = client.link_token_create(request)
    return response['link_token']


def exchange_public_token(public_token):
    client = get_plaid_client()
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response['access_token'], response['item_id']


def get_accounts(access_token):
    client = get_plaid_client()
    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)
    return response['accounts']


def sync_transactions(access_token, cursor=None):
    client = get_plaid_client()
    added, modified, removed = [], [], []
    has_more = True
    while has_more:
        kwargs = {'access_token': access_token}
        if cursor:
            kwargs['cursor'] = cursor
        request = TransactionsSyncRequest(**kwargs)
        response = client.transactions_sync(request)
        added.extend(response['added'])
        modified.extend(response['modified'])
        removed.extend(response['removed'])
        has_more = response['has_more']
        cursor = response['next_cursor']
    return added, modified, removed, cursor
