import os.path
import random, string
from base import item_to_dict
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
    def run(self, folder="Inbox", subject=None, search_start_date=None,
            attachment_format="BINARY"):
        """
        Action entrypoint
        :param folder str: MS Exchange folder to search for messages.
        :param subject str: [Optional] Partial, case-sensitive string to
            search for in "Subject" field.
        :param search_start_date str: [Optional] Date, preferably in ISO 8601
            format, as start date for search.
        :param attachment_format str: Format to save attachments in.
            BINARY or TEXT

        :returns list: List of *dictionaries* of:
            Email Subject
            List of fully-qualified file/path names of saved attachments
        """

        messages, messages_as_dicts = self._get_messages(folder=folder,
                                        subject=subject,
                                        search_start_date=search_start_date)
        self.logger.debug("Messages found: \n{m}".format(m=messages_as_dicts))

        attachment_result_list = self._save_attachments(messages=messages,
                                        attachment_format=attachment_format)

        return attachment_result_list

    def _save_attachments(self, messages, attachment_format):
        """
        Save attachments to specified server folder from provided list of
        email messages.
        """
        output_format = ATTACHMENT_FORMAT[attachment_format]
        att_filename_list = list()

        for message in messages:
            # Only *email* messages are handled.
            if not isinstance(message, Message):
                err_msg = ("Message ID '{id}' is not an email message "
                            "(item type: {item_type}).".format(
                                id=str(message.item_id),
                                item_type=str(message.item_type)))
                self.logger.error(err_msg)
                raise TypeError(err_msg)
            # Remove each attachment
            for attachment in message.attachment:
                if isinstance(attachment, FileAttachment):
                    output_file = self._get_unique_filename(
                        attachment_name=attachment.name,
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

    def _get_messages(self, folder, subject, search_start_date):
        folder = self.account.root.get_folder_by_name(folder)

        start_date = None
        if search_start_date:
            start_date = self._get_date_from_string(search_start_date)
            # For email messages, MS Exchange does not support using only a
            # start date for searches. Instead, we must use a *range* of dates
            # for search, so we set the *end* of range to "now".
            # See https://stackoverflow.com/a/48742644 for details.
            end_date = self._get_date_from_string()

        if subject:
            if start_date:
                # Try searching for *email* messages.
                try:
                    items = folder.filter(subject__contains=subject,
                                            datetime_received__range=(
                                                start_date, end_date
                                            ))
                except Exception:
                    self.logger.info("No *email* messages for search criteria.")
            else:
                items = folder.filter(subject__contains=subject)
        else:
            if start_date:
                try:
                    items = folder.filter(datetime_received__range=(
                                                start_date, end_date
                                            ))
                except Exception:
                    self.logger.info("No *email* messages for search criteria.")
            else:
                items = folder.all()

        return (items, [item_to_dict(item, include_body=False,
                            folder_name=folder.name) for item in items])

    # def _get_date_from_string(self, date_str=None):
    #     """
    #     Use dateutil library (https://dateutil.readthedocs.io/) to parse
    #     unstructured date string to standard format.
    #     :param date_str str: Date as string in unknown/unstructured format
    #     :returns EWSDateTime object or None
    #     """
    #     # If date_str is not provided, we assume that this is for the *end*
    #     # of the filter range, which we set to "now", using timezone from
    #     # pack configuration.
    #     if not date_str:
    #         return EWSDateTime.now(tz=self.timezone)

    #     try:
    #         from dateutil import parser
    #         import pytz
    #         parsed_date = parser.parse(date_str)
    #         utc_date = pytz.utc.localize(parsed_date)
    #         local_date = utc_date
    #         try:
    #             local_date = utc_date.astimezone(self.timezone)
    #         except Exception:
    #             self.logger.error("Unable to convert search date to pack "
    #                 "timezone. Using UTC...")
    #         start_date = EWSDateTime.from_datetime(local_date)
    #         self.logger.debug("Search start date: {dt}".format(dt=start_date))
    #     except ImportError:
    #         self.logger.error("Unable to find/load 'dateutil' library.")
    #         start_date = None
    #     except ValueError:
    #         self.logger.error("Invalid format for date input: {dt}"
    #             .format(dt=date_str))
    #         start_date = None

    #     return start_date