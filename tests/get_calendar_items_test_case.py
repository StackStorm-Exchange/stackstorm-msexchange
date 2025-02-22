from exchange_test_case import ExchangeBaseActionTestCase
from actions.get_calendar_items import GetCalendarItems


class GetCalendarItemsActionTestCase(ExchangeBaseActionTestCase):
    action_cls = GetCalendarItems

    def test_action(self):
        result = self.get_action_instance(config=self._test_config).run(
            start_year=2019,
            start_day=1,
            start_month=1,
            end_year=2020,
            end_day=2,
            end_month=2,
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)
