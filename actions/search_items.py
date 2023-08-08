from base.action import BaseExchangeAction
from base import item_to_dict


class SearchItemsAction(BaseExchangeAction):
    def run(self, folder, include_body, subject=None):
        folder = self.account.root / folder
        if subject:
            items = folder.filter(subject__contains=subject)
        else:
            items = folder.all()

        return [item_to_dict(item, include_body=include_body,
                             folder_name=folder) for item in items]
