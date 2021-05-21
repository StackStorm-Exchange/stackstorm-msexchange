[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-msexchange.svg?style=shield)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-msexchange)

# <img src="https://raw.githubusercontent.com/StackStorm-Exchange/stackstorm-msexchange/master/icon.png" width="32px" valign="-3px"/> Microsoft Exchange Integration Pack

This pack provides Microsoft Exchange integration to perform simple searches on an Exchange user.

Exchange Server 2010, 2013 and 2016 as well as Office 365 hosted Exchange accounts.

## Actions

* `get_calendar_items` - Get a list of calendar items within a date range
* `get_folder` - Get information about a folder (mail, contact, meta)
* `list_folders` - List all folders or subfolders within a folder
* `search_items` - Search for items by subject within a folder (default folder Inbox)
* `send_email` - Send an email

## Sensors

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
