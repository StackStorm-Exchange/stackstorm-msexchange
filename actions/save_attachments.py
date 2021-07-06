import datetime
import os.path
import random
import string

from base import item_to_dict
from base.action import BaseExchangeAction

from exchangelib import Message, FileAttachment

# Dictionary lookup for output format to write attachment from action parameter
ATTACHMENT_FORMAT = dict([
    ("BINARY", "wb"),
    ("TEXT", "wt")
])
REPLACE_SPACE = dict([
    ("NONE", None),
    ("UNDERSCORE", "_"),
    ("OCTOTHORPE/HASH", "#"),
    ("PIPE", "|")
])
# Buffer size for writing attachments to file system.
BUFFER_SIZE = 1024


class SaveFileAttachmentAction(BaseExchangeAction):
    """
    Action to save *file* attachments from MS Exchange *email* messages.
    """
    def run(self, folder="Inbox", subject=None, search_start_date=None,
            attachment_format="BINARY", replace_spaces_in_filename=None):
        """
        Action entrypoint
        :param folder str: MS Exchange folder to search for messages.
        :param subject str: [Optional] Partial, case-sensitive string to
            search for in "Subject" field.
        :param search_start_date str: [Optional] Date, preferably in ISO 8601
            format, as start date for search.
        :param attachment_format str: Format to save attachments in.
            BINARY or TEXT
        :param replace_spaces_in_filename str: Character to replace spaces in
            file names, if desired. Default is to leave spaces.

        :returns list: List of *dictionaries* of:
            Email Subject
            Date/time email sent
            Sender email address
            List of fully-qualified file/path names of saved attachments
        """

        messages = self._search_items(
            folder=folder,
            subject=subject,
            search_start_date=search_start_date)
        full_messages_as_dict = [item_to_dict(item=item, include_body=False,
                                 folder_name=folder) for item in messages]
        messages_as_dict = list()
        for message in full_messages_as_dict:
            messages_as_dict.append(dict([
                ("subject", message["subject"]),
                ("attachments", message["attachments"]),
                ("datetime_sent", message["datetime_sent"]),
                ("folder_name", message["folder_name"]),
                ("sender_email_address", message["sender_email_address"]),
                ("email_recipient_addresses",
                    message["email_recipient_addresses"])
            ]))
        self.logger.debug("Messages found: \n{m}".format(m=messages_as_dict))

        attachment_result_list = self._save_attachments(
            messages=messages,
            attachment_format=attachment_format,
            replace_spaces_in_filename=replace_spaces_in_filename)

        return attachment_result_list

    def _save_attachments(self, messages, attachment_format,
                          replace_spaces_in_filename):
        """
        Save attachments to specified server folder from provided list of
        email messages.
        """

        output_format = ATTACHMENT_FORMAT[attachment_format]
        replace_spaces_in_filename = REPLACE_SPACE.get(
            replace_spaces_in_filename, None)
        att_result_list = list()

        for message in messages:
            # Only *email* messages are handled.
            if not isinstance(message, Message):
                err_msg = ("Message ID '{id}' is not an email message "
                           "(item type: {item_type}).".format(
                               id=str(message.item_id),
                               item_type=str(message.item_type)))
                self.logger.error(err_msg)
                raise TypeError(err_msg)
            # Save each attachment, if any
            att_filename_list = list()
            for attachment in message.attachments:
                if isinstance(attachment, FileAttachment):
                    output_file = self._get_unique_filename(
                        attachment_name=attachment.name,
                        attachment_sent=message.datetime_sent,
                        replace_spaces_in_filename=replace_spaces_in_filename)
                    self.logger.debug("File attachment: {f}"
                                      .format(f=output_file))
                    with open(os.path.abspath(output_file), output_format) \
                            as f:
                        f.write(attachment.content)
                    self.logger.info("Saved attachment '{att_name}'."
                                     .format(att_name=output_file))
                    att_filename_list.append(output_file)
                else:
                    self.logger.info("Attachment '{att_name}' on email "
                                     "'{email}' is not a *file* attachment. "
                                     "Skipping...".format(
                                         att_name=str(attachment.name),
                                         email=str(message.subject)))

            # Append to result list ONLY if one or more attachments are saved.
            if att_filename_list:
                att_result_list.append(dict([
                    ("email_subject", str(message.subject)),
                    ("email_sent", str(message.datetime_sent)),
                    ("sender_email_address",
                        str(message.sender.email_address)),
                    ("attachment_files", att_filename_list)
                ]))

        return att_result_list

    def _get_unique_filename(self, attachment_name, attachment_sent,
                             replace_spaces_in_filename):

        save_dir = self.attachment_directory
        if replace_spaces_in_filename:
            attachment_name = (
                str(attachment_name).replace(" ", replace_spaces_in_filename))
        # Try combination of path and attachment filename
        output_filename = os.path.join(save_dir, attachment_name)
        if not os.path.exists(output_filename):
            return output_filename

        base_file_name = os.path.splitext(attachment_name)
        # Try appending *attachment* date in format MM_DD_YYYY
        file_date = str(attachment_sent.strftime("%m_%d_%Y"))
        output_filename = self._construct_filename(
            base_file_name=base_file_name, append_str=file_date
        )
        if not os.path.exists(output_filename):
            return output_filename

        # Try appending *attachment* date in format MM_DD_YYYY_HH_MI_SS
        file_date = str(attachment_sent.strftime("%m_%d_%Y_%H_%M_%S"))
        output_filename = self._construct_filename(
            base_file_name=base_file_name, append_str=file_date
        )
        if not os.path.exists(output_filename):
            return output_filename

        # Try appending *current* date in format MM_DD_YYYY_HH_MI_SS
        file_date = str(datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%m_%d_%Y_%H_%M_%S"))
        output_filename = self._construct_filename(
            base_file_name=base_file_name, append_str=file_date
        )
        if not os.path.exists(output_filename):
            return output_filename

        # Try appending random 8-character string
        while os.path.exists(output_filename):
            rnd_str = "".join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(8))
            output_filename = self._construct_filename(
                base_file_name=base_file_name, append_str=rnd_str
            )
            if not os.path.exists(output_filename):
                return output_filename

    def _construct_filename(self, base_file_name, append_str, save_dir=None):
        if not save_dir:
            save_dir = self.attachment_directory
        file_name = "{name}_{append_str}{ext}".format(
            name=base_file_name[0], append_str=append_str,
            ext=base_file_name[1])
        output_filename = os.path.join(save_dir, file_name)

        return output_filename
