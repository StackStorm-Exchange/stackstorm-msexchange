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