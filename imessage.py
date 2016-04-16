from os.path import expanduser
import sqlite3
import datetime

OSX_EPOCH = 978307200

# Represents a user that iMessages can be exchanged with.
#
# Each user has...
#  - an `id` property that uniquely identifies him or her in the Messages database
#  - a `phone_or_email` property that is either the user's phone number or iMessage-enabled email address
class Recipient:
	def __init__(self, id, phone_or_email):
		self.id = id
		self.phone_or_email = phone_or_email
	
	def __repr__(self):
		return "ID: " + str(self.id) + " Phone or email: " + self.phone_or_email

# Represents an iMessage message.
#
# Each message has:
#  - a `text` property that holds the text contents of the message
#  - a `date` property that holds the delivery date of the message
class Message:
	def __init__(self, text, date):
		self.text = text
		self.date = date
	
	def __repr__(self):
		return "Text: " + self.text + " Date: " + str(self.date)

def _new_connection():
    # The current logged-in user's Messages sqlite database is found at:
    # ~/Library/Messages/chat.db
	db_path = expanduser("~") + '/Library/Messages/chat.db'
	return sqlite3.connect(db_path)

# Fetches all known recipients.
#
# The `id`s of the recipients fetched can be used to fetch all messages exchanged with a given recipient.
def get_all_recipients():
	connection = _new_connection()
	c = connection.cursor()
    
    # The `handle` table stores all known recipients.
	c.execute("SELECT * FROM `handle`")
	recipients = []
	for row in c:
		recipients.append(Recipient(row[0], row[1]))
    
	connection.close()
	return recipients

# Fetches all messages exchanged with a given recipient.
def get_messages_for_recipient(id):
	connection = _new_connection()
	c = connection.cursor()
    
    # The `message` table stores all exchanged iMessages.
	c.execute("SELECT * FROM `message` WHERE handle_id=" + str(id))
	messages = []
	for row in c:
		text = row[2]
		if text is None:
			continue
		date = datetime.datetime.fromtimestamp(row[15] + OSX_EPOCH)
        
        # Strip any special non-ASCII characters (e.g., the special character that is used as a placeholder for attachments such as files or images).
        encoded_text = text.encode('ascii', 'ignore')
        messages.append(Message(encoded_text, date))
	connection.close()
	return messages
