from datetime import datetime
import time

from st2reactor.sensor.base import PollingSensor
from exchangelib import (
    Account,
    Credentials,
    Configuration,
    DELEGATE,
    EWSDateTime,
    EWSTimeZone,
)
from exchangelib.protocol import FaultTolerance


class ItemSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(ItemSensor, self).__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._stop = False
        self._store_key = "exchange.item_sensor_date_str"
        self._timezone = EWSTimeZone.timezone(config["timezone"])
        self._credentials = Credentials(
            username=config["username"], password=config["password"]
        )
        self.primary_smtp_address = config["primary_smtp_address"]
        self.sensor_folder = config["sensor_folder"]
        try:
            self.server = config["server"]
            self.autodiscover = False if self.server is not None else True
        except KeyError:
            self.autodiscover = True

    def setup(self):
        if self.autodiscover:
            self.account = Account(
                primary_smtp_address=self.primary_smtp_address,
                credentials=self._credentials,
                autodiscover=True,
                access_type=DELEGATE,
            )
        else:
            ms_config = Configuration(
                server=self.server,
                credentials=self._credentials,
                retry_policy=FaultTolerance(max_wait=config.get("timeout", 600)),
            )
            self.account = Account(
                primary_smtp_address=self.primary_smtp_address,
                config=ms_config,
                autodiscover=False,
                access_type=DELEGATE,
            )

    def poll(self):
        stored_date = self._get_last_date()
        self._logger.info("Stored Date: {}".format(stored_date))
        if not stored_date:
            stored_date = datetime.now()
        start_date = self._timezone.localize(EWSDateTime.from_datetime(stored_date))
        target = self.account.root / self.sensor_folder
        items = target.filter(is_read=False).filter(datetime_received__gt=start_date)

        self._logger.info("Found {0} items".format(items.count()))

        for newitem in items:
            self._logger.info("Sending trigger for item '{0}'.".format(newitem.subject))
            self._dispatch_trigger_for_new_item(newitem=newitem)
            self._set_last_date(newitem.datetime_received)
            self._logger.info(
                "Updating read status on item '{0}'.".format(newitem.subject)
            )
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

    def _get_last_date(self):
        self._last_date = self._sensor_service.get_value(name=self._store_key)
        if self._last_date is None:
            return None
        return datetime.strptime(self._last_date, "%Y-%m-%dT%H:%M:%S")

    def _set_last_date(self, last_date):
        # Check if the last_date value is an EWSDateTime object
        if isinstance(last_date, EWSDateTime):
            self._last_date = last_date.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            self._last_date = time.strftime("%Y-%m-%dT%H:%M:%S", last_date)
        self._sensor_service.set_value(name=self._store_key, value=self._last_date)

    def _dispatch_trigger_for_new_item(self, newitem):
        trigger = "msexchange.exchange_new_item"
        if isinstance(newitem.datetime_received, EWSDateTime):
            datetime_received = newitem.datetime_received.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            datetime_received = str(newitem.datetime_received)

        payload = {
            "item_id": str(newitem.item_id),
            "subject": str(newitem.subject),
            "body": str(newitem.body),
            "datetime_received": datetime_received,
        }
        self._sensor_service.dispatch(trigger=trigger, payload=payload)
