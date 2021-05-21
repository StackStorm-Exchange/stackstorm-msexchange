from exchange_test_case import ExchangeBaseActionTestCase
from actions.list_folders import ListFoldersAction


class ListFoldersActionTestCase(ExchangeBaseActionTestCase):
    action_cls = ListFoldersAction

    def test_default_root(self):
        result = self.get_action_instance(config=self._test_config).run()
        expected = {"id": 1234}
        self.assertEqual(result, expected)

    def test_unique_root(self):
        result = self.get_action_instance(config=self._test_config).run(root="foo")
        expected = {"id": 1234}
        self.assertEqual(result, expected)
