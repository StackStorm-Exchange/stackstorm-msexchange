# Change Log

## 1.0.1

* Update exchangelib to 4.3.0

## 1.0.0

* Drop Python 2.7 support

## 0.1.4

* Corrected timestamp handling functions in item_sensor
* Added poll_interval configuration option for item_sensor
* Added dispatch trigger function with logic to process new item object properties in item_sensor
* Updated polling logic in item_sensor to update "READ" status on all new items
* Corrected version pinning in requirements.txt file - 1.10.0

## 0.1.3

* Set default folder to `Inbox` for `search_items`
* Fixed sensor bug with config object handling for non-autodiscovery systems 

## 0.1.2

* Pinned exchangelib version to avoid `get_folder_by_name()` deprecation
* Fixed actions bug with config object handling for non-autodiscovery systems
