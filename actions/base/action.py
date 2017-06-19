from collections import namedtuple

from st2actions.runners.pythonrunner import Action
from st2client.models import KeyValuePair
from exchangelib import Account, ServiceAccount, Configuration, DELEGATE

CacheEntry = namedtuple('CacheEntry', 'ews_url ews_auth_type primary_smtp_address')


class BaseExchangeAction(Action):
    def __init__(self, config):
        super(BaseExchangeAction, self).__init__(config)
        self._credentials = ServiceAccount(
            username=config['username'],
            password=config['password'])

        try:
            server = config['server']
            autodiscover = False
        except KeyError:
            autodiscover = True
        cache = self._get_cache()
        if cache:
            config = Configuration(
                service_endpoint=cache.ews_url,
                credentials=self._credentials,
                auth_type=cache.ews_auth_type)
            self.account = Account(
                primary_smtp_address=cache.primary_smtp_address,
                config=config,
                autodiscover=False,
                access_type=DELEGATE
            )
        else:
            if autodiscover:
                self.account = Account(
                    primary_smtp_address=config['primary_smtp_address'],
                    credentials=self._credentials,
                    autodiscover=autodiscover,
                    access_type=DELEGATE)
            else:
                config = Configuration(
                    server=server,
                    credentials=self._credentials)
                self.account = Account(
                    primary_smtp_address=config['primary_smtp_address'],
                    config=config,
                    autodiscover=False,
                    access_type=DELEGATE)
            self._store_cache_configuration()

    def _store_cache_configuration(self):
        ews_url = self.account.protocol.service_endpoint
        ews_auth_type = self.account.protocol.auth_type
        primary_smtp_address = self.account.primary_smtp_address
        self.action_service.set_value(name='exchange_ews_url', value=ews_url)
        self.action_service.set_value(name='exchange_ews_auth_type', value=ews_auth_type)
        self.action_service.set_value(name='exchange_primary_smtp_address', value=primary_smtp_address)

    def _get_cache(self):
        ews_url = self.action_service.get_value(
            name='exchange_ews_url')
        ews_auth_type = self.action_service.get_value(
            name='exchange_ews_auth_type')
        primary_smtp_address = self.action_service.get_value(
            name='exchange_primary_smtp_address')
        if ews_url:
            return CacheEntry(
                ews_url=ews_url.value,
                ews_auth_type=ews_auth_type.value,
                primary_smtp_address=primary_smtp_address.value)
        else:
            return None
