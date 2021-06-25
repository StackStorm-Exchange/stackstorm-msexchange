import os.path
import random, string
from base.action import BaseExchangeAction
from exchangelib import Message, FileAttachment, EWSDateTime

# Dictionary lookup for output format to write attachment from action parameter
ATTACHMENT_FORMAT = dict([
    ("BINARY", "wb"),
    ("TEXT", "wt")
])
# Buffer size for writing attachments to file system.
BUFFER_SIZE = 1024

class SaveFileAttachmentAction(BaseExchangeAction):
    """
    Action to save *file* attachments from MS Exchange *email* messages.
    """
    def run(self, message_id, changekey_id, attachment_format="BINARY"):
        """
        Action entrypoint
        :param message_id str: MS Exchange email message ID.
            Typically obtained from "search_items" action.
        :param attachment_format str: Format to save attachments in.
            BINARY or TEXT
        """

        attachment_filename_list = list()
        attachment_filename_list = self._save_attachments(message_id=message_id,
                                        changekey_id=changekey_id,
                                        attachment_format=attachment_format)

        return attachment_filename_list

    def _save_attachments(self, message_id, changekey_id, attachment_format):
        """
        Save attachments to specified server folder from provided list of
        email messages.
        """
        output_format = ATTACHMENT_FORMAT[attachment_format]
        att_filename_list = list()

        # Get email by *combination* of message ID and changekey ID.
        message = self.account.fetch(ids=list((message_id, changekey_id)))
        self.logger.debug("Message after retrieval by ID: {msg}"
            .format(msg=message))

        # Only *email* messages are handled.
        if not isinstance(message, Message):
            err_msg = ("Message ID '{id}' is not an email message (item type: "
                        "{item_type}).".format(id=str(message_id),
                        item_type=str(message.item_type)))
            self.logger.error(err_msg)
            raise TypeError(err_msg)

        # Remove each attachment
        for attachment in message.attachment:
            if isinstance(attachment, FileAttachment):
                output_file = self._get_unique_filename(
                    attachement_name=attachment.name,
                    attachment_sent=attachment.datetime_sent)
                # Perform buffered I/O to avoid memory issues
                # with large attachments.
                with open(output_file, output_format) \
                    as f, attachment.fp as fp:
                    buffer = fp.read(BUFFER_SIZE)
                    while buffer:
                        f.write()
                        buffer = fp.read(BUFFER_SIZE)
                self.logger.info("Saved attachment '{att_name}'."
                    .format(att_name=output_file))
                att_filename_list.append(output_file)
            else:
                self.logger.error("Attachment '{att_name}' on email "
                    "'{email}' is not a *file* attachment. Skipping..."
                    .format(att_name=str(attachment.name),
                            email=str(attachment.message.subject)))

        return att_filename_list

    def _get_unique_filename(self, attachment_name, attachment_sent):
        save_dir = self.attachment_directory
        # Try combination of path and attachment filename
        output_filename = os.path.join(save_dir, attachment_name)
        if not os.path.exists(output_filename):
            return output_filename

        base_file_name = os.path.splitext(attachment_name)
        # Try appending *attachment* date in format MM_DD_YYYY
        file_date = str(attachment_sent.strftime("%m_%d_%Y"))
        file_name = "{name}_{date}{ext}".format(name=base_file_name[0],
            date=file_date, ext=base_file_name[1])
        output_filename = os.path.join(save_dir, file_name)
        if not os.path.exists(output_filename):
            return output_filename

        # Try appending *attachment* date in format MM_DD_YYYY_HH_MI_SS
        file_date = str(attachment_sent.strftime("%m_%d_%Y_%H_%M_%S"))
        file_name = "{name}_{date}{ext}".format(name=base_file_name[0],
            date=file_date, ext=base_file_name[1])
        output_filename = os.path.join(save_dir, file_name)
        if not os.path.exists(output_filename):
            return output_filename

        # Try appending random 8-character string
        while os.path.exists(output_filename):
            rnd_str = "".join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(8))
            file_name = "{name}_{rnd_str}{ext}".format(
                name=base_file_name[0], rnd_str=rnd_str,
                ext=base_file_name[1])
            output_filename = os.path.join(save_dir, file_name)
            if not os.path.exists(output_filename):
                return output_filename