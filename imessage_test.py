import imessage

raw_input("Hello, press any key to print all known recipients you exchanged iMessages with.")
print(imessage.get_all_recipients())

recipient_id_str = raw_input("Enter the ID (number) of the recipient you wish to view message for:")

print(imessage.get_messages_for_recipient(int(recipient_id_str)))
