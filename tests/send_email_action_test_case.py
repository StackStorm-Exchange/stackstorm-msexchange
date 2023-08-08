from exchange_test_case import ExchangeBaseActionTestCase
from actions.send_email import SendEmailAction


class SendEmailActionTestCase(ExchangeBaseActionTestCase):
    action_cls = SendEmailAction

    def test_run_get_test_folder(self):
        result = self.get_action_instance(config=self._test_config).run(
            subject="test email",
            body="HELO world",
            to_recipients=["bob@test.com", "sandra@test.com"],
            store=True,
        )
        expected = {"id": 1234}
        self.assertEqual(result, expected)
