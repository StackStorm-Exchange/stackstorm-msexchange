from base.action import BaseExchangeAction
from base import item_to_dict

from exchangelib import EWSDateTime


class SearchItemsAction(BaseExchangeAction):
    def run(self, folder, include_body, subject=None, search_start_date=None):
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
                    items = folder.filter(subject__contains=subject,
                                            datetime_received__range=(
                                                start_date, end_date
                                            ))
                # Search on other items, which have regular "start" attribute...
                except Exception:
                    items = folder.filter(subject__contains=subject,
                                            start__gte=start_date)
            else:
                items = folder.filter(subject__contains=subject)
        else:
            if start_date:
                try:
                    items = folder.filter(datetime_received__range=(
                                                start_date, end_date
                                            ))
                except Exception:
                    items = folder.filter(start__gte=start_date)
            else:
                items = folder.all()

        return [item_to_dict(item, include_body=include_body,
                            folder_name=folder.name) for item in items]

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