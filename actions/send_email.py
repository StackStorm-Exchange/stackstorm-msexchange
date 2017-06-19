from base.action import BaseExchangeAction
from exchangelib import Message, Mailbox


class SendEmailAction(BaseExchangeAction):
    def run(self, subject, body, to_recipients, store):
        rcpts = [Mailbox(email_address=rcpt) for rcpt in to_recipients.split(',')]
        mail = Message(
            account=self.account,
            subject=subject,
            body=body,
            to_recipients=rcpts
        )

        if store:
            mail.send_and_save()  # Save in Sent folder
        else:
            mail.send()
        return mail
