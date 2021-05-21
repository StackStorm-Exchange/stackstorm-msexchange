from exchange_test_case import ExchangeBaseTestCase
from actions.get_folder import GetFolderAction


class ListFoldersActionTestCase(ExchangeBaseTestCase):
    action_cls = GetFolderAction

    def test_run_get_test_folder(self):
        result = self.get_action_instance().run(
            config=self._test_config, folder_name="test_folder"
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)
