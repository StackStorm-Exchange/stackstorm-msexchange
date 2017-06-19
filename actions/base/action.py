from st2actions.runners.pythonrunner import Action
from exchangelib import Account, ServiceAccount, Configuration, DELEGATE


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
