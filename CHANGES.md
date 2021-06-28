# Change Log

## 1.1.0

* **Add** `save_attachments` action.
    * Includes several _pack_ configuration options:
        * `attachment_directory`: Fully-qualified server path name used to store attachments. Must be readable and writeable by Stackstorm. Defaults to "/opt/stackstorm/packs/msexchange/attachments".
        * `attachment_folder_maximum_size`: Maximum storage space in MB (default is 50MB) alloted to `attachment_directory`. Pack maintenance process (see below) manages this.
        * `attachment_days_to_keep`: Maximum number of days to keep saved attachments (default is 7 days). Also, managed by pack maintenance process.
    * Uses same model as `search_items` for finding email messages for which to save attachments. Only _email_ messages and _file_ attachments are supported.

* **Enhancements** to `search_items` action.
    * Moved search logic from `run` method in `search_items` action into `_search_items` utility method in `base/actions.py` to allow functionality to be shared by `search_items` and `save_attachments`.
    * Added `search_start_date` parameter specifying the start date for items to search. (End date is always "today".) Date can be entered as free-form text.




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
