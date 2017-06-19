from base.action import BaseExchangeAction
from base import folder_to_dict


class ListFoldersAction(BaseExchangeAction):
    def run(self, root=None):
        if root:
            folders = self.account.root.get_folder_by_name(root)
        else:
            folders = self.account.root.get_folders()

        return [folder_to_dict(folder) for folder in folders]
