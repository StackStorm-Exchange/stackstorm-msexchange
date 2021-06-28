from datetime import datetime
import os
from st2common.runners.base_action import Action


class AttachmentDirectoryMaintenanceAction(Action):
    """
    Action to perform maintenance on file system folder/directory in which
    email attachments are stored using pack-level parameters.
    Typically, this class will be invoked by sensor/trigger.
    """
    def __init__(self, config):
        super(AttachmentDirectoryMaintenanceAction, self).__init__(config)

        # Get attributes from pack configuration
        self.attachment_directory = os.path.abspath(
            config["attachment_directory"])
        self.attachment_directory_maximum_size = int(self.config.get(
            "attachment_directory_maximum_size", 50))
        self.attachment_days_to_keep = int(self.config.get(
            "attachment_days_to_keep", 7))

    def run(self, attachment_directory_maximum_size=None,
            attachment_days_to_keep=None):
        """
        Action entrypoint
        :param attachment_directory_maximum_size int: *Optional* override of
            pack parameter
        :param attachment_days_to_keep int: *Optional* override of pack
            parameter
        """

        if attachment_directory_maximum_size:
            self.attachment_directory_maximum_size = \
                int(attachment_directory_maximum_size)
            self.logger.info("Overriding pack folder maximum size...")
        if attachment_days_to_keep:
            self.attachment_days_to_keep = int(attachment_days_to_keep)
            self.logger.info("Overriding pack maximum days to keep attachments...")

        self._remove_old_files()
        self._reduce_directory_size()

    def _remove_old_files(self):
        """
        Find all files older than "attachment_days_to_keep" and delete them.
        """
        deleted_file_count, deleted_file_size = 0, 0
        _older_than = (int(datetime.utcnow().strftime("%s"))
                        - (24 * 60 * 60 * self.attachment_days_to_keep))
        self.logger.info("Deleting all files older than {ts}..."
            .format(ts=_older_than.strftime("%m/%d/%Y %H:%M:%S")))
        for file in os.scandir(self.attachment_directory):
            if file.is_file() and file.stat().st_mtime < _older_than:
                os.remove(file.name)
                deleted_file_count += 1
                deleted_file_size += file.stat().st_size
                self.logger.info("Deleted '{file}'.".format(file.name))

        self.logger.info("Deleted {n} files totaling {size}MB."
            .format(n=deleted_file_count,
                    size=round(float(deleted_file_size) / (1024 * 1024), 1)))

    def _reduce_directory_size(self):
        """
        Reduce directory size below "attachment_directory_maximum_size" by
        deleting files until threshold is reached starting with _largest_
        (remaining) files first.
        """
        file_count, total_file_size = 0, 0
        for file in os.scandir(self.attachment_directory):
            if file.is_file():
                file_count += 1
                total_file_size += file.stat().st_size
        self.logger.info("Before deleting files: {n} files totaling {size}MB"
            .format(n=file_count,
                    size=round(float(total_file_size) / (1024 * 1024), 1)))

        max_folder_size = (1024 * 1024) * self.attachment_directory_maximum_size
        if total_file_size > max_folder_size:
            self.logger.info("Deleting files until threshold reached...")
            deleted_file_count, deleted_file_size = 0
            # Get list of *files* in directory and sort in descending
            # order by size.
            file_list = [file for file
                            in list(os.scandir(self.attachment_directory))
                            if file.is_file()]
            sorted_file_list = file_list.sort(key=lambda f: f.stat().st_size,
                                                reverse=True)
            for file in sorted_file_list:
                os.remove(file.name)
                deleted_file_count += 1
                deleted_file_size += file.stat().st_size
                self.logger.info("Deleted '{file}'.".format(file.name))

                if ((total_file_size - deleted_file_size) < max_folder_size):
                    break

            self.logger.info("Deleted {n} files totaling {size}MB."
                .format(n=deleted_file_count,
                    size=round(float(deleted_file_size) / (1024 * 1024), 1)))
        else:
            self.logger.info("Directory '{dir}' is already below maximum size "
                "of {max_size}MB. Nothing to do.".format(
                    dir=self.attachment_directory,
                    max_size=self.attachment_directory_maximum_size))


