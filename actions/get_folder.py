from base.action import BaseExchangeAction


class GetFolderAction(BaseExchangeAction):
    def run(self, folder_name):
        result = self.account.root.get_folder_by_name(folder_name)

        return {
            'total_count': result.total_count,
            'child_folder_count': result.child_folder_count,
            'unread_count': result.unread_count
        }
