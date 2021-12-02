from base.action import BaseExchangeAction
from base import item_to_dict


class SearchItemsAction(BaseExchangeAction):
    def run(self, folder, include_body, subject=None, search_start_date=None):
        items = self._search_items(folder=folder, subject=subject,
                                   search_start_date=search_start_date)

        return [item_to_dict(item, include_body=include_body,
                             folder_name=folder) for item in items]
