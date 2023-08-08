from exchange_test_case import ExchangeBaseSensorTestCase
from sensors.item_sensor import ItemSensor


class ItemSensorTestCase(ExchangeBaseSensorTestCase):
    sensor_cls = ItemSensor

    def test_run_get_test_folder(self):
        result = self.get_sensor_instance(config=self._test_config).run()
        expected = {"id": 1234}
        self.assertEqual(result, expected)
