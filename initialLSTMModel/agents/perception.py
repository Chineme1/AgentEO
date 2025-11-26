# agents/perception.py
import imaplib
import email
from email.header import decode_header
import re

class PerceptionAgent:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def _clean_text(self, s):
        if not s:
            return ""
        # Remove excessive whitespace and non-printables
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def fetch_inbox(self, limit=50):
        """
        Fetch latest 'limit' messages from INBOX. Returns list of dicts:
        {"id": str, "subject": str, "from": str, "body": str}
        """
        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        if result != "OK":
            raise RuntimeError("IMAP search failed")

        ids = data[0].split()
        # take last `limit` ids
        ids = ids[-limit:]
        emails = []

        for eid in ids[::-1]:  # newest first
            res, msg_data = mail.fetch(eid, "(RFC822)")
            if res != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg.get("Subject") or ""
            # decode header if needed
            try:
                dh = decode_header(subject)
                subject = "".join([ (t.decode(h) if isinstance(t, bytes) else t) if h else (t.decode() if isinstance(t, bytes) else t) for t,h in dh ])
            except Exception:
                pass

            sender = msg.get("From", "")
            # get body (plain text preference)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and part.get_content_disposition() in (None, 'inline'):
                        try:
                            body_part = part.get_payload(decode=True).decode(errors="ignore")
                            body += body_part + "\n"
                        except:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                except:
                    body = ""

            body = self._clean_text(body)
            emails.append({
                "id": eid.decode() if isinstance(eid, bytes) else str(eid),
                "subject": self._clean_text(subject),
                "from": sender,
                "body": body
            })
        mail.logout()
        return emails
