from collections import namedtuple
import os

from st2common.runners.base_action import Action
from st2client.client import Client
from st2client.models import KeyValuePair
from exchangelib import (Account, ServiceAccount, Configuration, DELEGATE,
                        EWSTimeZone, EWSDateTime)

CacheEntry = namedtuple('CacheEntry', 'ews_url ews_auth_type primary_smtp_address')


class BaseExchangeAction(Action):
    def __init__(self, config):
        super(BaseExchangeAction, self).__init__(config)
        api_url = os.environ.get('ST2_ACTION_API_URL', None)
        token = os.environ.get('ST2_ACTION_AUTH_TOKEN', None)
        self.client = Client(api_url=api_url, token=token)
        self._credentials = ServiceAccount(
            username=config['username'],
            password=config['password'])
        self.timezone = EWSTimeZone.timezone(config['timezone'])
        try:
            server = config['server']
            autodiscover = False if server is not None else True
        except KeyError:
            autodiscover = True
        cache = self._get_cache()
        if cache:
            config = Configuration(
                service_endpoint=cache.ews_url,
                credentials=self._credentials,
                auth_type=cache.ews_auth_type)
            self.account = Account(
                primary_smtp_address=cache.primary_smtp_address,
                config=config,
                autodiscover=False,
                access_type=DELEGATE
            )
        else:
            if autodiscover:
                self.account = Account(
                    primary_smtp_address=config['primary_smtp_address'],
                    credentials=self._credentials,
                    autodiscover=autodiscover,
                    access_type=DELEGATE)
            else:
                ms_config = Configuration(
                    server=server,
                    credentials=self._credentials)
                self.account = Account(
                    primary_smtp_address=config['primary_smtp_address'],
                    config=ms_config,
                    autodiscover=False,
                    access_type=DELEGATE)
            self._store_cache_configuration()

        # Configure attachment parameters
        self._attachment_configuration()

    def _store_cache_configuration(self):
        ews_url = self.account.protocol.service_endpoint
        ews_auth_type = self.account.protocol.auth_type
        primary_smtp_address = self.account.primary_smtp_address
        self.client.keys.update(KeyValuePair(name='exchange_ews_url',
            value=ews_url))
        self.client.keys.update(KeyValuePair(name='exchange_ews_auth_type',
            value=ews_auth_type))
        self.client.keys.update(KeyValuePair(name='exchange_primary_smtp_address',
            value=primary_smtp_address))

    def _get_cache(self):
        ews_url = self.client.keys.get_by_name(
            name='exchange_ews_url')
        ews_auth_type = self.client.keys.get_by_name(
            name='exchange_ews_auth_type')
        primary_smtp_address = self.client.keys.get_by_name(
            name='exchange_primary_smtp_address')
        if ews_url:
            return CacheEntry(
                ews_url=ews_url.value,
                ews_auth_type=ews_auth_type.value,
                primary_smtp_address=primary_smtp_address.value)
        else:
            return None

    def _attachment_configuration(self):
        attach_dir = self.config.get("attachment_directory", None)
        if not attach_dir:
            try:
                from st2common.content import utils as content_utils
                pack_name = getattr(self.action_service._action_wrapper,
                                    "_pack", "unknown")
                pack_path = content_utils.get_pack_base_path(pack_name)
                attach_dir = os.path.join(pack_path, "attachments")
            except ImportError:
                err_msg = (
                    "Unable load import 'st2common.content.utils' "
                    "library. Using pack default attachment directory of "
                    "'/opt/stackstorm/packs/msexchange/attachments'.")
                self.logger.error(err_msg)
                attach_dir = "/opt/stackstorm/packs/msexchange/attachments"
        else:
            attach_dir = os.path.abspath(attach_dir)

        # Create the folder/directory, if it doesn't exist,
        # and make it writeable.
        if not os.path.exists(attach_dir):
            os.makedirs(attach_dir, exist_ok=True)
            os.chmod(attach_dir, 0o755)
            self.logger.info("Created directory '{dir}' and made writeable."
                             .format(dir=attach_dir))

        if not os.access(attach_dir, os.W_OK):
            raise OSError("Unable to write to attachment directory '{dir}'."
                          .format(dir=attach_dir))

        self.attachment_directory = attach_dir
        self.attachment_directory_maximum_size = int(self.config.get(
            "attachment_directory_maximum_size", 50))
        self.attachment_days_to_keep = int(self.config.get(
            "attachment_days_to_keep", 7))

    def _get_date_from_string(self, date_str=None):
        """
        Use dateutil library (https://dateutil.readthedocs.io/) to parse
        unstructured date string to standard format.
        :param date_str str: Date as string in unknown/unstructured format
        :returns EWSDateTime object or None
        """
        # If date_str is not provided, we assume that this is for the *end*
        # of the filter range, which we set to "now", using timezone from
        # pack configuration.
        if not date_str:
            return EWSDateTime.now(tz=self.timezone)

        try:
            from dateutil import parser
            import pytz
            parsed_date = parser.parse(date_str)
            utc_date = pytz.utc.localize(parsed_date)
            local_date = utc_date
            try:
                local_date = utc_date.astimezone(self.timezone)
            except Exception:
                self.logger.error("Unable to convert search date to pack "
                                  "timezone. Using UTC...")
            start_date = EWSDateTime.from_datetime(local_date)
            self.logger.debug("Search start date: {dt}".format(dt=start_date))
        except ImportError:
            self.logger.error("Unable to find/load 'dateutil' library.")
            start_date = None
        except ValueError:
            self.logger.error("Invalid format for date input: {dt}"
                              .format(dt=date_str))
            start_date = None

        return start_date

    def _search_items(self, folder, subject=None, search_start_date=None):
        """
        Common method for searching for MS Exchange items (email messages,
        calendar items, etc.). Used by _search_items_ and _save_attachments_.
        """
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
                # First, try searching for messages...
                try:
                    items = folder.filter(
                        subject__contains=subject,
                        datetime_received__range=(start_date, end_date))
                # Search on other items, which have regular "start" attribute.
                except Exception:
                    items = folder.filter(
                        subject__contains=subject, start__gte=start_date)
            else:
                items = folder.filter(subject__contains=subject)
        else:
            if start_date:
                try:
                    items = folder.filter(
                        datetime_received__range=(start_date, end_date))
                except Exception:
                    items = folder.filter(start__gte=start_date)
            else:
                items = folder.all()

        return (items)
