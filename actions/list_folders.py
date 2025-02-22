from base.action import BaseExchangeAction
from base import folder_to_dict


class ListFoldersAction(BaseExchangeAction):
    def run(self, root=None):
        if root:
            folders = (self.account.root / root).children
        else:
            folders = self.account.root.children  # pylint: disable=no-member

        return [folder_to_dict(folder) for folder in folders]
