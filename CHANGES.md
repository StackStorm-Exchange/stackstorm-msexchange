# Change Log

## 1.1.0

* **Add** `save_attachments` action.
    * Includes several _pack_ configuration options:
        - `attachment_directory`: Fully-qualified server path name used to store attachments. Must be readable and writeable by Stackstorm. Defaults to "/opt/stackstorm/packs/msexchange/attachments".
        - `attachment_folder_maximum_size`: Maximum storage space in MB (default is 50MB) alloted to `attachment_directory`. Pack maintenance process (see below) manages this.
        - `attachment_days_to_keep`: Maximum number of days to keep saved attachments (default is 7 days). Also, managed by pack maintenance process.
    * Uses same model as `search_items` for finding email messages for which to save attachments. Only _email_ messages and _file_ attachments are supported.
    * Action returns a _list/array_ of dictionaries with following attributes:
        - `email_subject` - Full subject of the email.
        - `email_sent` - Date that email was sent.
        - `sender_email_address` - Email address of the sender.
        - `attachment_files` - _List/array_ of fully-qualified filenames from server of attachments saved. Example:
        ```JSON
        [
            {
                "email_subject": "ACCOUNT LIST - resend for testing",
                "email_sent": "2021-06-25 13:54:34+00:00",
                "sender_email_address": "someone@example.com",
                "attachment_files": [
                "/opt/stackstorm/packs/msexchange/attachments/Accounts_06_23_2021.xlsx"
                ]
            }
        ]
        ```
    * If attachment filename is **not** unique in target folder, attempts to generate a unique filename for each attachment via several methods, including date sent, date _and_ time sent, and "random" 8-character string.
    * Attachments can be saved either as BINARY (default) or TEXT format.
    * An `attachment_directory_maintenance` sensor/trigger/rule combination has been implemented and, by default, runs once daily (polling interval of 86400 seconds) to enforce these rules through the `do_attachment_directory_maintenance` action. This action can be run manually, as well, if you need to override the pack configuration values; running manually it with no input values uses the pack configuration.
    * Maintenance process removes files by age first and then, if necessary, deletes remaining files starting with _largest_ files until threshold is reached.
    * Save attachment action has `replace_spaces_in_filename` enumerated value parameter (NONE [default], UNDERSCORE, OCTOTHORPE/HASH, and PIPE) to allow user to replace spaces in attachment file names, if desired. Default (NONE) is to preserve spaces.

* **Enhancements** to `search_items` action.
    * Moved search logic from `run` method in `search_items` action into `_search_items` utility method in `base/actions.py` to allow functionality to be shared by `search_items` and `save_attachments`.
    * Added `search_start_date` parameter specifying the start date for items to search. (End date is always "today".) Date can be entered as free-form text. Most any date format is supported, as [`dateutil`](https://dateutil.readthedocs.io/) library is used to parse input to valid `datetime` value.
    * Update `search_items` action to return additional item attributes, specific to _email_ messages, from `item_to_dict` helper method. Such attributes can be useful in filtering e-mails based on sender and/or originating domain.
        - `sender_email_address` - Email address of sender.
        - `email_recipient_addresses` - List/array of email recipients (from [`exchangelib`](https://ecederstrand.github.io/exchangelib/) `to_recipients` list **only**).
    * Added optional `folder_name` parameter to `item_to_dict` helper method to include the name of the folder used in the search as attribute of returned dictionary.
    * Update `requirements.txt` to include `python-dateutil` (see above) and `pytz`, which is needed for creating timezone-aware `exchangelib` [`EWSDateTime`](https://ecederstrand.github.io/exchangelib/exchangelib/ewsdatetime.html#exchangelib.ewsdatetime.EWSDateTime) objects for date searches.

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
