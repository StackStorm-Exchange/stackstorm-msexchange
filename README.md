[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-msexchange.svg?style=shield)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-msexchange)

# <img src="https://raw.githubusercontent.com/StackStorm-Exchange/stackstorm-msexchange/master/icon.png" width="32px" valign="-3px"/> Microsoft Exchange Integration Pack
This pack provides Microsoft Exchange integration to perform simple searches on an Exchange user.

Exchange Server 2010, 2013 and 2016 as well as Office 365 hosted Exchange accounts.

## Actions
* `do_attachment_directory_maintenance` - Performance maintenance on server directory in which email file attachments are saved.
* `get_calendar_items` - Get a list of calendar items within a date range
* `get_folder` - Get information about a folder (mail, contact, meta)
* `list_folders` - List all folders or subfolders within a folder
* `save_attachments` - Save _file_ attachments on _email_ messages to server directory.
* `search_items` - Search for items by subject and/or date within a folder (default folder Inbox)
* `send_email` - Send an email

## Rules
* `attachment_directory_maintenance` - Runs maintenance (storage usage) via `do_attachment_directory_maintenance` action on server directory in which file attachments are saved when triggered by associated sensor.

## Sensors
* `attachment_directory_maintenance_sensor` - Runs maintenance  periodically (default daily).
* `item_sensor` - Monitors the configured folder (Inbox by default) for new items and sends a `exchange_new_item` trigger when one is received

## Configuration

Configuration should contain the primary SMTP address (for knowing what user to send email as), the username and password. Also, for searches using date ranges, the time zone will be normalized to the one specified.

```yaml
---
primary_smtp_address: "bob@company.com"
username: "bob@company.com"
password: "B0bsPassword!"
timezone: "Europe/London"
```

Where autodiscovery is not available, the EWS host (typically the webmail host address) can be used.

```yaml
---
primary_smtp_address: "bob@company.com"
username: "bob@company.com"
password: "B0bsPassword!"
server: ourcompany-webmail.company.com
timezone: "Europe/London"
```

The sensor folder for the new item sensor can also be configured

```yaml
---
primary_smtp_address: "bob@company.com"
username: "bob@company.com"
password: "B0bsPassword!"
timezone: "Europe/London"
sensor_folder: "My folder to monitor"
```

### Email Attachment Configuration
- `attachment_directory`: Fully-qualified server path name used to store attachments. Must be readable and writeable by Stackstorm. Defaults to "/opt/stackstorm/packs/msexchange/attachments".
- `attachment_folder_maximum_size`: Maximum storage space in MB (default is 50MB) alloted to `attachment_directory`. Pack maintenance process (see below) manages this.
- `attachment_days_to_keep`: Maximum number of days to keep saved attachments (default is 7 days). Also, managed by pack maintenance process.