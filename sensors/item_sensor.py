from st2reactor.sensor.base import PollingSensor
from exchangelib import Account, ServiceAccount, Configuration, DELEGATE, EWSDateTime, EWSTimeZone


class ItemSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(ItemSensor, self).__init__(sensor_service=sensor_service, config=config,
                                         poll_interval=poll_interval)
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
            self.autodiscover = False if self.server is not None else True
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
            ms_config = Configuration(
                server=self.server,
                credentials=self._credentials)
            self.account = Account(
                primary_smtp_address=self.primary_smtp_address,
                config=ms_config,
                autodiscover=False,
                access_type=DELEGATE)

    def poll(self):
        target = self.account.root.get_folder_by_name(self.sensor_folder)
        items = target.filter(is_read=False)

        self._logger.info("Found {0} items".format(items.count()))

        for newitem in items:
            self._logger.info("Sending trigger for item '{0}'.".format(newitem.subject))
            self._dispatch_trigger_for_new_item(newitem=newitem)
            self._logger.info("Updating read status on item '{0}'.".format(newitem.subject))
            newitem.is_read = True
            newitem.save()

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

    def _dispatch_trigger_for_new_item(self, newitem):
        trigger = 'msexchange.exchange_new_item'
        if isinstance(newitem.datetime_received, EWSDateTime):
            datetime_received = newitem.datetime_received.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            datetime_received = str(newitem.datetime_received)

        payload = {
            'item_id': str(newitem.item_id),
            "change_key": str(newitem.changekey),
            'subject': str(newitem.subject),
            'body': str(newitem.body),
            'datetime_received': datetime_received,
        }
        self._sensor_service.dispatch(trigger=trigger, payload=payload)
