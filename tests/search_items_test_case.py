from exchange_test_case import ExchangeBaseActionTestCase
from actions.search_items import SearchItemsAction


class SearchItemsActionTestCase(ExchangeBaseActionTestCase):
    action_cls = SearchItemsAction

    def test_search(self):
        result = self.get_action_instance(config=self._test_config).run(
            folder="TestFolder", subject="testing"
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)

    def test_search_no_subject(self):
        result = self.get_action_instance(config=self._test_config).run(
            folder="TestFolder"
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)
