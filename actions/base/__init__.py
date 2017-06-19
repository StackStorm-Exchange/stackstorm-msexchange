def folder_to_dict(folder):
    return {
        'id': folder.folder_id,
        'name': folder.name,
        'class': folder.folder_class,
        'total_count': folder.total_count,
        'child_folder_count': folder.child_folder_count,
        'unread_count': folder.unread_count
    }


def item_to_dict(item):
    return {
        'id': item.item_id,
        'changekeyid': item.changekey,
        'mime_content': item.mime_content,
        'subject': item.subject,
        'sensitivity': item.sensitivity,
        'text_body': item.text_body,
        'body': item.body,
        'attachments': len(item.attachments),
        'datetime_received': item.datetime_received.ewsformat(),
        'categories': item.categories,
        'importance': item.importance,
        'is_draft': item.is_draft,
        'headers': item.headers,
        'datetime_sent': item.datetime_sent.ewsformat(),
        'datetime_created': item.datetime_created.ewsformat(),
        'reminder_is_set': item.reminder_is_set,
        'reminder_due_by': item.reminder_due_by.ewsformat(),
        'reminder_minutes_before_start': item.reminder_minutes_before_start,
        'last_modified_name': item.last_modified_name,
        'last_modified_time': item.last_modified_time.ewsformat(),
    }
