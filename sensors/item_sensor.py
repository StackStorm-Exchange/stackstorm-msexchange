from datetime import datetime
import time

from st2reactor.sensor.base import PollingSensor
from exchangelib import Account, ServiceAccount, Configuration, DELEGATE, EWSDateTime, EWSTimeZone


class ItemSensor(PollingSensor):
    def __init__(self, sensor_service, config):
        super(ItemSensor, self).__init__(sensor_service=sensor_service, config=config)
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._stop = False
        self._store_key = 'exchange.item_sensor_date_str'
        self._timezone = EWSTimeZone.timezone(config['timezone'])
        self._credentials = ServiceAccount(
            username=config['username'],
            password=config['password'])
        self.primary_smtp_address = config['primary_smtp_address']
        self.sensor_folder = config['sensor_folder']
        try:
            self.server = config['server']
            self.autodiscover = False
        except KeyError:
            self.autodiscover = True

    def setup(self):
        if self.autodiscover:
            self.account = Account(
                primary_smtp_address=self.primary_smtp_address,
                credentials=self._credentials,
                autodiscover=True,
                access_type=DELEGATE)
        else:
            config = Configuration(
                server=self.server,
                credentials=self._credentials)
            self.account = Account(
                primary_smtp_address=self.primary_smtp_address,
                config=config,
                autodiscover=False,
                access_type=DELEGATE)

    def poll(self):
        stored_date = self._get_last_date()
        if not stored_date:
            stored_date = datetime.now()
        start_date = self._timezone.localize(EWSDateTime.from_datetime(stored_date))
        target = self.account.root.get_folder_by_name(self.sensor_folder)
        items = target.filter(is_read=False).filter(datetime_received__gt=start_date)

        self._logger.info("Found {0} items".format(items.count()))
        for payload in items.values('item_id', 'subject', 'body', 'datetime_received'):
            self._logger.info("Sending trigger for item '{0}'.".format(payload['subject']))
            self._sensor_service.dispatch(trigger='exchange_new_item', payload=payload)
            self._set_last_date(payload['datetime_received'])

    def cleanup(self):
        # This is called when the st2 system goes down. You can perform cleanup operations like
        # closing the connections to external system here.
        pass

    def add_trigger(self, trigger):
        # This method is called when trigger is created
        pass

    def update_trigger(self, trigger):
        # This method is called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # This method is called when trigger is deleted
        pass

    def _get_last_date(self):
        self._last_date = self._sensor_service.get_value(name=self._store_key)
        if self._last_date is None:
            return None
        return time.strptime(self._last_date, '%Y-%m-%dT%H:%M:%S')

    def _set_last_date(self, last_date):
        self._last_date = time.strftime('%Y-%m-%dT%H:%M:%S', last_date)
        self._sensor_service.set_value(name=self._store_key,
                                       value=self._last_date)
