from st2reactor.sensor.base import PollingSensor


class AttachmentDirectoryMaintenanceSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(AttachmentDirectoryMaintenanceSensor, self).__init__(
            sensor_service=sensor_service, config=config,
            poll_interval=poll_interval)
        self._logger = self.sensor_service.get_logger(
            name=self.__class__.__name__)
        self._trigger_pack = "msexchange"

    def setup(self):
        pass

    def poll(self):
        self._logger.info("*** Starting Attachment Folder Maintenance "
                          "Sensor ***")

        self._logger.info("Dispatching trigger...")
        self._dispatch_trigger_for_attachment_directory_maintenance()

        self._logger.info("*** Ending Attachment Folder Maintenance "
                          "Sensor ***")

    def cleanup(self):
        # This is called when the st2 system goes down.
        # You can perform cleanup operations like
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

    def _dispatch_trigger_for_attachment_directory_maintenance(self):
        trigger = ".".join([self._trigger_pack,
                            'attachment_directory_maintenance'])

        payload = {}
        self._sensor_service.dispatch(trigger=trigger, payload=payload)
