from base.action import BaseExchangeAction
from base import item_to_dict


class SearchItemsAction(BaseExchangeAction):
    def run(self, folder, include_body, subject=None):
        folder = self.account.root.get_folder_by_name(folder)
        if subject:
            items = folder.filter(subject__contains=subject)
        else:
            items = folder.all()
        for item in items:
            self.logger.debug("Item class: ".format(type(item)))
        return [item_to_dict(item, include_body=include_body) for item in items]
