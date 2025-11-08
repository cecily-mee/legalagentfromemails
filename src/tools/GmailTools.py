# import os
# import re
# import uuid
# import base64
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart


# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# class GmailToolsClass:
#     def __init__(self):
#         self.service = self._get_gmail_service()
        
#     def fetch_unanswered_emails(self, max_results=50):
#         """
#         Fetches all emails included in unanswered threads.

#         @param max_results: Maximum number of recent emails to fetch
#         @return: List of dictionaries, each representing a thread with its emails
#         """
#         try:
#             # Get recent emails and organize them into threads
#             recent_emails = self.fetch_recent_emails(max_results)
#             if not recent_emails: return []
            
#             # Get all draft replies
#             drafts = self.fetch_draft_replies()

#             # Create a set of thread IDs that have drafts
#             threads_with_drafts = {draft['threadId'] for draft in drafts}

#             # Process new emails
#             seen_threads = set()
#             unanswered_emails = []
#             for email in recent_emails:
#                 thread_id = email['threadId']
#                 if thread_id not in seen_threads and thread_id not in threads_with_drafts:
#                     seen_threads.add(thread_id)
#                     email_info = self._get_email_info(email['id'])
#                     if self._should_skip_email(email_info):
#                         continue
#                     unanswered_emails.append(email_info)
#             return unanswered_emails

#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return []

#     def fetch_recent_emails(self, max_results=50):
#         try:
#             # Set delay of 8 hours
#             now = datetime.now()
#             delay = now - timedelta(hours=8)

#             # Format for Gmail query
#             after_timestamp = int(delay.timestamp())
#             before_timestamp = int(now.timestamp())

#             # Query to get emails from the last 8 hours
#             query = f"after:{after_timestamp} before:{before_timestamp}"
#             results = self.service.users().messages().list(
#                 userId="me", q=query, maxResults=max_results
#             ).execute()
#             messages = results.get("messages", [])
            
#             return messages
        
#         except Exception as error:
#             print(f"An error occurred while fetching emails: {error}")
#             return []
        
#     def fetch_draft_replies(self):
#         """
#         Fetches all draft email replies from Gmail.
#         """
#         try:
#             drafts = self.service.users().drafts().list(userId="me").execute()
#             draft_list = drafts.get("drafts", [])
#             return [
#                 {
#                     "draft_id": draft["id"],
#                     "threadId": draft["message"]["threadId"],
#                     "id": draft["message"]["id"],
#                 }
#                 for draft in draft_list
#             ]

#         except Exception as error:
#             print(f"An error occurred while fetching drafts: {error}")
#             return []

#     def create_draft_reply(self, initial_email, reply_text):
#         try:
#             # Create the reply message
#             message = self._create_reply_message(initial_email, reply_text)

#             # Create draft with thread information
#             draft = self.service.users().drafts().create(
#                 userId="me", body={"message": message}
#             ).execute()

#             return draft
#         except Exception as error:
#             print(f"An error occurred while creating draft: {error}")
#             return None

#     def send_reply(self, initial_email, reply_text):
#         try:
#             # Create the reply message
#             message = self._create_reply_message(initial_email, reply_text, send=True)

#             # Send the message with thread ID
#             sent_message = self.service.users().messages().send(
#                 userId="me", body=message
#             ).execute()
            
#             return sent_message

#         except Exception as error:
#             print(f"An error occurred while sending reply: {error}")
#             return None
        
#     def _create_reply_message(self, email, reply_text, send=False):
#         # Create message with proper headers
#         message = self._create_html_email_message(
#             recipient=email.sender,
#             subject=email.subject,
#             reply_text=reply_text
#         )

#         # Set threading headers
#         if email.messageId:
#             message["In-Reply-To"] = email.messageId
#             # Combine existing references with the original message ID
#             message["References"] = f"{email.references} {email.messageId}".strip()
            
#             if send:
#                 # Generate a new Message-ID for this reply
#                 message["Message-ID"] = f"<{uuid.uuid4()}@gmail.com>"
                
#         # Construct email body
#         body = {
#             "raw": base64.urlsafe_b64encode(message.as_bytes()).decode(),
#             "threadId": email.threadId
#         }

#         return body

        
#     def _get_gmail_service(self):
#         creds = None
#         if os.path.exists('token.json'):
#             creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#                 creds = flow.run_local_server(port=0)
#             with open('token.json', 'w') as token:
#                 token.write(creds.to_json())
        
#         return build('gmail', 'v1', credentials=creds)
    
#     def _should_skip_email(self, email_info):
#         return os.environ['MY_EMAIL'] in email_info['sender']

#     def _get_email_info(self, msg_id):
#         message = self.service.users().messages().get(
#             userId="me", id=msg_id, format="full"
#         ).execute()

#         payload = message.get('payload', {})
#         headers = {header["name"].lower(): header["value"] for header in payload.get("headers", [])}

#         return {
#             "id": msg_id,
#             "threadId": message.get("threadId"),
#             "messageId": headers.get("message-id"),
#             "references": headers.get("references", ""),
#             "sender": headers.get("from", "Unknown"),
#             "subject": headers.get("subject", "No Subject"),
#             "body": self._get_email_body(payload),
#         }
    
#     def _get_email_body(self, payload):
#         """
#         Extract the email body, prioritizing text/plain over text/html.
#         Handles multipart messages, avoids duplicating content, and strips HTML if necessary.
#         """
#         def decode_data(data):
#             """Decode base64-encoded data."""
#             return base64.urlsafe_b64decode(data).decode('utf-8').strip() if data else ""

#         def extract_body(parts):
#             """Recursively extract text content from parts."""
#             for part in parts:
#                 mime_type = part.get('mimeType', '')
#                 data = part['body'].get('data', '')
#                 if mime_type == 'text/plain':
#                     return decode_data(data)
#                 if mime_type == 'text/html':
#                     html_content = decode_data(data)
#                     return self._extract_main_content_from_html(html_content)
#                 if 'parts' in part:
#                     result = extract_body(part['parts'])
#                     if result:
#                         return result
#             return ""

#         # Process single or multipart payload
#         if 'parts' in payload:
#             body = extract_body(payload['parts'])
#         else:
#             data = payload['body'].get('data', '')
#             body = decode_data(data)
#             if payload.get('mimeType') == 'text/html':
#                 body = self._extract_main_content_from_html(body)

#         return self._clean_body_text(body)

#     def _extract_main_content_from_html(self, html_content):
#         """
#         Extract main visible content from HTML.
#         """
#         soup = BeautifulSoup(html_content, 'html.parser')
#         for tag in soup(['script', 'style', 'head', 'meta', 'title']):
#             tag.decompose()
#         return soup.get_text(separator='\n', strip=True)

#     def _clean_body_text(self, text):
#         """
#         Clean up the email body text by removing extra spaces and newlines.
#         """
#         return re.sub(r'\s+', ' ', text.replace('\r', '').replace('\n', '')).strip()
    
#     def _create_html_email_message(self, recipient, subject, reply_text):
#         """
#         Creates a simple HTML email message with proper formatting and plaintext fallback.
#         """
#         message = MIMEMultipart("alternative")
#         message["to"] = recipient
#         message["subject"] = f"Re: {subject}" if not subject.startswith("Re: ") else subject

#         # Simplified HTML Template
#         html_text = reply_text.replace("\n", "<br>").replace("\\n", "<br>")
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="utf-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         </head>
#         <body>{html_text}</body>
#         </html>
#         """

#         html_part = MIMEText(html_content, "html")

#         # message.attach(text_part)
#         message.attach(html_part)

#         return message

import os
import re
import uuid
import base64
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

##CHANGE MADE##
# Add imports for byte handling (io) and PDF-to-image conversion (pdf2image)
import io 
from pdf2image import convert_from_bytes
##CHANGE MADE##


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailToolsClass:
    def __init__(self):
        self.service = self._get_gmail_service()
        
    ##CHANGE MADE##
    # Add a helper function to convert PDF bytes to a list of base64-encoded images.
    def _convert_pdf_to_images(self, data_bytes):
        """Converts PDF bytes into a list of base64-encoded JPEG images."""
        images_base64 = []
        try:
            # Use pdf2image to convert bytes to a list of PIL Image objects
            images = convert_from_bytes(data_bytes)
            print(f"Converting {len(images)} PDF pages to images...")
            
            for img in images:
                buffered = io.BytesIO()
                # Save the image to an in-memory buffer as JPEG
                img.save(buffered, format="JPEG")
                # Encode the image bytes to base64
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                images_base64.append(img_str)
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
        return images_base64
    ##CHANGE MADE##
        
    def fetch_unanswered_emails(self, max_results=50):
        """
        Fetches all emails included in unanswered threads.

        @param max_results: Maximum number of recent emails to fetch
        @return: List of dictionaries, each representing a thread with its emails
        """
        try:
            # Get recent emails and organize them into threads
            recent_emails = self.fetch_recent_emails(max_results)
            if not recent_emails: return []
            
            # Get all draft replies
            drafts = self.fetch_draft_replies()

            # Create a set of thread IDs that have drafts
            threads_with_drafts = {draft['threadId'] for draft in drafts}

            # Process new emails
            seen_threads = set()
            unanswered_emails = []
            for email in recent_emails:
                thread_id = email['threadId']
                if thread_id not in seen_threads and thread_id not in threads_with_drafts:
                    seen_threads.add(thread_id)
                    email_info = self._get_email_info(email['id'])
                    if self._should_skip_email(email_info):
                        continue
                    unanswered_emails.append(email_info)
            return unanswered_emails

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def fetch_recent_emails(self, max_results=50):
        try:
            # Set delay of 8 hours
            now = datetime.now()
            delay = now - timedelta(hours=8)

            # Format for Gmail query
            after_timestamp = int(delay.timestamp())
            before_timestamp = int(now.timestamp())

            # Query to get emails from the last 8 hours
            # Only fetch messages in the inbox that are unread and not from our own address
            my_email = os.environ.get('MY_EMAIL', '')
            query = f"after:{after_timestamp} before:{before_timestamp} is:inbox is:unread -from:{my_email}"
            results = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            messages = results.get("messages", [])
            
            return messages
        
        except Exception as error:
            print(f"An error occurred while fetching emails: {error}")
            return []
        
    def fetch_draft_replies(self):
        """
        Fetches all draft email replies from Gmail.
        """
        try:
            drafts = self.service.users().drafts().list(userId="me").execute()
            draft_list = drafts.get("drafts", [])
            return [
                {
                    "draft_id": draft["id"],
                    "threadId": draft["message"]["threadId"],
                    "id": draft["message"]["id"],
                }
                for draft in draft_list
            ]

        except Exception as error:
            print(f"An error occurred while fetching drafts: {error}")
            return []

    def mark_as_read(self, msg_id: str):
        """Marks a specific email as read by removing the 'UNREAD' label."""
        try:
            body = {"removeLabelIds": ["UNREAD"]}
            self.service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
            print(f"Marked email {msg_id} as read.")
        except Exception as e:
            print(f"Error marking email {msg_id} as read: {e}")

    def create_draft_reply(self, initial_email, reply_text):
        try:
            # Create the reply message
            message = self._create_reply_message(initial_email, reply_text)

            # Create draft with thread information
            draft = self.service.users().drafts().create(
                userId="me", body={"message": message}
            ).execute()

            return draft
        except Exception as error:
            print(f"An error occurred while creating draft: {error}")
            return None

    def send_reply(self, initial_email, reply_text):
        try:
            # Create the reply message
            message = self._create_reply_message(initial_email, reply_text, send=True)

            # Send the message with thread ID
            sent_message = self.service.users().messages().send(
                userId="me", body=message
            ).execute()
            
            return sent_message

        except Exception as error:
            print(f"An error occurred while sending reply: {error}")
            return None
        
    def _create_reply_message(self, email, reply_text, send=False):
        # Create message with proper headers
        message = self._create_html_email_message(
            recipient=email.sender,
            subject=email.subject,
            reply_text=reply_text
        )

        # Set threading headers
        if email.messageId:
            message["In-Reply-To"] = email.messageId
            # Combine existing references with the original message ID
            message["References"] = f"{email.references} {email.messageId}".strip()
            
            if send:
                # Generate a new Message-ID for this reply
                message["Message-ID"] = f"<{uuid.uuid4()}@gmail.com>"
                
        # Construct email body
        body = {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode(),
            "threadId": email.threadId
        }

        return body

        
    def _get_gmail_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def _should_skip_email(self, email_info):
        return os.environ['MY_EMAIL'] in email_info['sender']

    def _get_email_info(self, msg_id):
        message = self.service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        payload = message.get('payload', {})
        headers = {header["name"].lower(): header["value"] for header in payload.get("headers", [])}
        ##CHANGE MADE##
        # We now call _get_email_body and our new _get_attachment_content function
        # to get the text body and a list of attachment images separately.
        body = self._get_email_body(payload)
        attachment_images = self._get_attachment_content(msg_id, payload)
        ##CHANGE MADE##

        return {
            "id": msg_id,
            "threadId": message.get("threadId"),
            "messageId": headers.get("message-id"),
            "references": headers.get("references", ""),
            "sender": headers.get("from", "Unknown"),
            "to": headers.get("to", ""),
            "subject": headers.get("subject", "No Subject"),
            ##CHANGE MADE##
            # We assign the variables to our new keys in the dictionary.
            "body": body,
            "attachment_images": attachment_images
            ##CHANGE MADE##
        }
    
    ##CHANGE MADE##
    # Add a new function to get attachment content. It will iterate through
    # email parts, find PDFs, and convert them to images.
    def _get_attachment_content(self, msg_id, payload):
        """Recursively finds and extracts images from attachments."""
        attachment_images = [] # Will be a list of base64 strings
        if 'parts' not in payload:
            return []
        
        for part in payload.get('parts', []):
            # Recurse for multipart messages
            if 'parts' in part:
                attachment_images.extend(self._get_attachment_content(msg_id, part))

            filename = part.get('filename', '').lower()
            mime_type = part.get('mimeType', '')
            
            # Skip parts that aren't attachments
            if not filename: 
                continue

            # Get attachment data
            data = None
            if 'data' in part.get('body', {}):
                data = part['body']['data']
            elif 'attachmentId' in part.get('body', {}):
                att_id = part['body']['attachmentId']
                try:
                    attachment = self.service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
                    data = attachment['data']
                except Exception as e:
                    print(f"Error fetching attachment {att_id}: {e}")
                    continue
            
            if not data:
                continue

            # Decode data
            try:
                decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            except Exception as e:
                print(f"Error decoding base64 data for {filename}: {e}")
                continue

            # Parse based on type
            print(f"Found attachment: {filename} (MIME: {mime_type})")
            if mime_type == 'application/pdf' or filename.endswith('.pdf'):
                images = self._convert_pdf_to_images(decoded_data)
                attachment_images.extend(images)
            
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or filename.endswith('.docx'):
                print(f"Skipping DOCX file (image conversion not implemented): {filename}")
                # Note: To handle DOCX, you would need another system dependency 
                # like 'unoconv' to convert it to PDF first, then use _convert_pdf_to_images.
                # For now, we'll just skip it.
                pass
                
        return attachment_images
    ##CHANGE MADE##

    def _get_email_body(self, payload):
        """
        Extract the email body, prioritizing text/plain over text/html.
        Handles multipart messages, avoids duplicating content, and strips HTML if necessary.
        """
        def decode_data(data):
            """Decode base64-encoded data."""
            return base64.urlsafe_b64decode(data).decode('utf-8').strip() if data else ""

        def extract_body(parts):
            """Recursively extract text content from parts."""
            for part in parts:
                mime_type = part.get('mimeType', '')
                
                ##CHANGE MADE##
                # This ensures we don't grab text from text attachments, 
                # only the main email body.
                filename = part.get('filename', '').lower()
                if filename:
                    continue
                ##CHANGE MADE##

                data = part['body'].get('data', '')
                if mime_type == 'text/plain':
                    return decode_data(data)
                if mime_type == 'text/html':
                    html_content = decode_data(data)
                    return self._extract_main_content_from_html(html_content)
                if 'parts' in part:
                    result = extract_body(part['parts'])
                    if result:
                        return result
            return ""

        # Process single or multipart payload
        if 'parts' in payload:
            body = extract_body(payload['parts'])
        else:
            data = payload['body'].get('data', '')
            body = decode_data(data)
            if payload.get('mimeType') == 'text/html':
                body = self._extract_main_content_from_html(body)

        return self._clean_body_text(body)

    def _extract_main_content_from_html(self, html_content):
        """
        Extract main visible content from HTML.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup(['script', 'style', 'head', 'meta', 'title']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)

    def _clean_body_text(self, text):
        """
        Clean up the email body text by removing extra spaces and newlines.
        """
        return re.sub(r'\s+', ' ', text.replace('\r', '').replace('\n', '')).strip()
    
    def _create_html_email_message(self, recipient, subject, reply_text):
        """
        Creates a simple HTML email message with proper formatting and plaintext fallback.
        """
        message = MIMEMultipart("alternative")
        message["to"] = recipient
        message["subject"] = f"Re: {subject}" if not subject.startswith("Re: ") else subject

        # Simplified HTML Template
        html_text = reply_text.replace("\n", "<br>").replace("\\n", "<br>")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>{html_text}</body>
        </html>
        """

        html_part = MIMEText(html_content, "html")

        # message.attach(text_part)
        message.attach(html_part)

        return message
