#i might remove this file, im not sure... 
import imaplib

def apply_label(email_id, label, host, user, password):
    """
    Uses Gmail IMAP X-GM-LABELS to apply (create if necessary) a label to a message.
    email_id should be the IMAP UID as retrieved earlier.
    """
    mail = imaplib.IMAP4_SSL(host)
    mail.login(user, password)
    mail.select("inbox")

    # Use store command to add label
    try:
        typ, data = mail.store(email_id, '+X-GM-LABELS', label)
    except Exception as e:
        print("apply_label error:", e)
    mail.logout()
