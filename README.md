# pymessage-lite

`pymessage-lite` is a simple Python library for fetching recipients and messages from OS X's Messages database.

## Background

While there is no API for accessing iMessage data on OS X or iOS, OS X users can query the [sqlite](https://www.sqlite.org/) database that stores iMessage data. It can be found in the `~/Library/Messages/` directory under the name `chat.db`.

The database schema is undocumented, but by poking around with the `sqlite3` command line tool it's easy to figure out how it works.

## Exploring the Database

Open a new Terminal window and enter:

`sqlite3 ~/Library/Messages/chat.db`

To list all the tables in the database, type `.tables` and hit Enter. The output should look something like:

```
_SqliteDatabaseProperties  deleted_messages         
attachment                 handle                   
chat                       message                  
chat_handle_join           message_attachment_join  
chat_message_join
```

The contents of these tables should be fairly self-explanatory.

- `attachment` keeps track of any attachments sent, including paths to where they are stored locally as well as their file format.
- `handle` keeps track of all known recipients (people you previously exchanged iMessages with).
- `chat` keeps track of your conversation threads.
- `message` keeps track of all messages along with their text contents, date, and the ID of the recipient.

In my limited testing, I found `deleted_messages` is always empty. The other tables should not be necessary for most use cases.

To view the full schema of a table and list all of its columns, type:

`.schema <table_name>`

Here is the output for `.schema message`:

```
CREATE TABLE message (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, guid TEXT UNIQUE NOT NULL, text TEXT, replace INTEGER DEFAULT 0, service_center TEXT, handle_id INTEGER DEFAULT 0, subject TEXT, country TEXT, attributedBody BLOB, version INTEGER DEFAULT 0, type INTEGER DEFAULT 0, service TEXT, account TEXT, account_guid TEXT, error INTEGER DEFAULT 0, date INTEGER, date_read INTEGER, date_delivered INTEGER, is_delivered INTEGER DEFAULT 0, is_finished INTEGER DEFAULT 0, is_emote INTEGER DEFAULT 0, is_from_me INTEGER DEFAULT 0, is_empty INTEGER DEFAULT 0, is_delayed INTEGER DEFAULT 0, is_auto_reply INTEGER DEFAULT 0, is_prepared INTEGER DEFAULT 0, is_read INTEGER DEFAULT 0, is_system_message INTEGER DEFAULT 0, is_sent INTEGER DEFAULT 0, has_dd_results INTEGER DEFAULT 0, is_service_message INTEGER DEFAULT 0, is_forward INTEGER DEFAULT 0, was_downgraded INTEGER DEFAULT 0, is_archive INTEGER DEFAULT 0, cache_has_attachments INTEGER DEFAULT 0, cache_roomnames TEXT, was_data_detected INTEGER DEFAULT 0, was_deduplicated INTEGER DEFAULT 0, is_audio_message INTEGER DEFAULT 0, is_played INTEGER DEFAULT 0, date_played INTEGER, item_type INTEGER DEFAULT 0, other_handle INTEGER DEFAULT -1, group_title TEXT, group_action_type INTEGER DEFAULT 0, share_status INTEGER, share_direction INTEGER, is_expirable INTEGER DEFAULT 0, expire_state INTEGER DEFAULT 0, message_action_type INTEGER DEFAULT 0, message_source INTEGER DEFAULT 0);
...
```

If you focus on the `CREATE_TABLE` line, you'll notice it's followed by the columns of the table. For example, the third column, `text TEXT`, stores the context of the message as text and the `handle_id` column stores the ID of the recipient who sent the message, which you can in turn look up in the `handle` table. While none of this is documented, you can probably guess what each column stores. For example, `INTEGERis_read` probably stores a `1` if a message has been acknowledged with a read recipient and `0` otherwise.

To view all your recipients, you can type:

`SELECT * FROM handle;`

And to view all message exchanged with a recipient of a given ID:

`SELECT * FROM message WHERE handle_id=<ID>`

This is standard SQL, and there are plenty of [references on the web](http://www.w3schools.com/sql/sql_quickref.asp) detailing all the commands you can issue.

**Warning:** Be careful! You can delete your entire iMessage history with commands such as `DELETE`.

## The Library

The Python library simply uses the sqlite Python API to issue some of the commands you have seen above, but programmatically so you don't have to use the Terminal.

The code for `get_all_recipients` simply connects to the sqlite3 database, issues a `SELECT` query to retrieve all recipients, and returns them as instances of a custom Python class, `Recipient`.

If you've read everything above, this should be fairly straightforward:

	connection = _new_connection()
	c = connection.cursor()
    
    # The `handle` table stores all known recipients.
	c.execute("SELECT * FROM `handle`")
	recipients = []
	for row in c:
		recipients.append(Recipient(row[0], row[1]))
    
	connection.close()
	return recipients

## Using the Library

To try out the library, navigate to the `pymessage_lite` directory and enter `python imessage_test.py`. This test script will print out all your iMessage recipients and let you display all messages exchanged with a given recipient.

## Compatibility

This has been written and tested with OS X 10.11 "El Capitan". It might stop working in future releases of OS X as iMessage evolves.
