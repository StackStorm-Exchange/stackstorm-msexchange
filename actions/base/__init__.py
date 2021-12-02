from exchangelib import Mailbox, Message


def folder_to_dict(folder):
    return {
        'id': folder.folder_id,
        'name': folder.name,
        'class': folder.folder_class,
        'total_count': folder.total_count,
        'child_folder_count': folder.child_folder_count,
        'unread_count': folder.unread_count
    }


def item_to_dict(item, include_body=False, folder_name=None):
    result = {
        'id': item.item_id,
        'changekeyid': item.changekey,
        'subject': item.subject,
        'sensitivity': item.sensitivity,
        'text_body': item.text_body,
        'body': item.body,
        'attachments': len(item.attachments),
        'datetime_received': item.datetime_received.ewsformat() if item.datetime_received else None,
        'categories': item.categories,
        'importance': item.importance,
        'is_draft': item.is_draft,
        'datetime_sent': item.datetime_sent.ewsformat() if item.datetime_sent else None,
        'datetime_created': item.datetime_created.ewsformat() if item.datetime_created else None,
        'reminder_is_set': item.reminder_is_set,
        'reminder_due_by': item.reminder_due_by.ewsformat() if item.reminder_due_by else None,
        'reminder_minutes_before_start': item.reminder_minutes_before_start,
        'last_modified_name': item.last_modified_name
    }
    if not include_body:
        del result['body']
        del result['text_body']
    if folder_name:
        result["folder_name"] = folder_name
    # If this is an email message, add sender and recipients.
    if isinstance(item, Message):
        result["sender_email_address"] = None
        if isinstance(item.sender, Mailbox):
            result["sender_email_address"] = str(item.sender.email_address)
        result["email_recipient_addresses"] = list()
        for recpt in item.to_recipients:
            if isinstance(recpt, Mailbox):
                result["email_recipient_addresses"].append(
                    str(recpt.email_address))
    return result
