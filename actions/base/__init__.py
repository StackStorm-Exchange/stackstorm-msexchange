def folder_to_dict(folder):
    return {
        'id': folder.folder_id,
        'name': folder.name,
        'class': folder.folder_class,
        'total_count': folder.total_count,
        'child_folder_count': folder.child_folder_count,
        'unread_count': folder.unread_count
    }
