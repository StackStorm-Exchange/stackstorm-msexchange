from base.action import BaseExchangeAction
from base import folder_to_dict


class GetFolderAction(BaseExchangeAction):
    def run(self, folder_name):
        result = self.account.root / folder_name

        return folder_to_dict(result)
