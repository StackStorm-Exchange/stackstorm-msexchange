from base.action import BaseExchangeAction
from base import item_to_dict


class SearchItemsAction(BaseExchangeAction):
    def run(self, folder, include_body, subject=None, search_start_date=None):
        folder = self.account.root.get_folder_by_name(folder)

        start_date = None
        if search_start_date:
            start_date = self._get_date_from_string(search_start_date)

        if subject:
            if start_date:
                items = folder.filter(subject__contains=subject,
                                    start__gte=start_date)
            else:
                items = folder.filter(subject__contains=subject)
        else:
            if start_date:
                items = folder.filter(start__gte=start_date)
            else:
                items = folder.all()

        return [item_to_dict(item, include_body=include_body) for item in items]

    def _get_date_from_string(self, date_str):
        """
        Use dateutil library (https://dateutil.readthedocs.io/) to parse
        unstructured date string to standard format.
        :param date_str str: Date as string in unknown/unstructured format
        :returns datetime or None
        """
        try:
            from dateutil import parser
            start_date = parser.parse(date_str)
        except ImportError:
            self.logger.error("Unable to find/load 'dateutil' library.")
            start_date = None
        except ValueError:
            self.logger.error("Invalid format for date input: {dt}"
                .format(dt=date_str))
            start_date = None

        return start_date