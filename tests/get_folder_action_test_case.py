from exchange_test_case import ExchangeBaseActionTestCase
from actions.get_folder import GetFolderAction


class GetFolderActionTestCase(ExchangeBaseActionTestCase):
    action_cls = GetFolderAction

    def test_run_get_test_folder(self):
        result = self.get_action_instance(config=self._test_config).run(
            folder_name="test_folder"
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)
