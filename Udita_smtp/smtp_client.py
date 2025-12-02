"""
SMTP Client Implementation
This client can compose and send emails to an SMTP server.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import socket
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smtp_client.log'),
        logging.StreamHandler()
    ]
)


class SMTPClientException(Exception):
    """Base exception for SMTP client errors"""
    pass


class InvalidEmailAddress(SMTPClientException):
    """Raised when email address is invalid"""
    pass


class NetworkError(SMTPClientException):
    """Raised when there's a network connectivity issue"""
    pass


class DeliveryFailure(SMTPClientException):
    """Raised when email delivery fails"""
    pass


class SMTPClient:
    """
    SMTP Client for composing and sending emails.
    """
    
    def __init__(self, server_host='127.0.0.1', server_port=1025):
        """
        Initialize SMTP Client.
        
        Args:
            server_host: SMTP server host address
            server_port: SMTP server port
        """
        self.server_host = server_host
        self.server_port = server_port
        logging.info(f"SMTP Client initialized for {server_host}:{server_port}")
        self.failed_deliveries = []
        self.delivery_log_file = 'delivery_failures.json'
        self._load_failed_deliveries()

    def _load_failed_deliveries(self):
        """Load failed deliveries from file"""
        try:
            if os.path.exists(self.delivery_log_file):
                with open(self.delivery_log_file, 'r') as f:
                    self.failed_deliveries = json.load(f)
        except Exception as e:
            logging.warning(f"Could not load delivery failures: {e}")
            self.failed_deliveries = []

    def _save_failed_delivery(self, sender, recipients, subject, reason):
        """Save failed delivery info to log file"""
        try:
            failure = {
                'timestamp': datetime.now().isoformat(),
                'sender': sender,
                'recipients': recipients if isinstance(recipients, list) else [recipients],
                'subject': subject,
                'reason': reason
            }
            self.failed_deliveries.append(failure)
            with open(self.delivery_log_file, 'w') as f:
                json.dump(self.failed_deliveries, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save delivery failure: {e}")
    
    def create_email(self, sender, recipients, subject, body, attachments=None):
        """
        Create an email message.
        
        Args:
            sender: Sender email address
            recipients: List of recipient email addresses or single email string
            subject: Email subject
            body: Email body content
            attachments: List of file paths to attach (optional)
            
        Returns:
            MIMEMultipart: Formatted email message
        """
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Attach body text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._attach_file(msg, file_path)
                    else:
                        logging.warning(f"Attachment file not found: {file_path}")
            
            logging.info(f"Email created - From: {sender}, To: {recipients}, Subject: {subject}")
            return msg
            
        except Exception as e:
            logging.error(f"Error creating email: {str(e)}")
            raise
    
    def _attach_file(self, msg, file_path):
        """
        Attach a file to the email message.
        
        Args:
            msg: MIMEMultipart message object
            file_path: Path to the file to attach
        """
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
            logging.info(f"Attached file: {filename}")
            
        except Exception as e:
            logging.error(f"Error attaching file {file_path}: {str(e)}")
            raise
    
    def send_email(self, sender, recipients, subject, body, attachments=None):
        """
        Send an email through the SMTP server.
        
        Args:
            sender: Sender email address
            recipients: List of recipient email addresses or single email string
            subject: Email subject
            body: Email body content
            attachments: List of file paths to attach (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure recipients is a list
            if isinstance(recipients, str):
                recipients = [recipients]
            
            # Validate email addresses (strict)
            if not self.validate_email(sender):
                reason = f"Invalid sender email: {sender} (missing or invalid format)"
                self._save_failed_delivery(sender, recipients, subject, reason)
                raise InvalidEmailAddress(reason)
            
            for recipient in recipients:
                if not self.validate_email(recipient):
                    reason = f"Invalid recipient email: {recipient} (missing or invalid format)"
                    self._save_failed_delivery(sender, recipients, subject, reason)
                    raise InvalidEmailAddress(reason)
            
            # Create email message
            msg = self.create_email(sender, recipients, subject, body, attachments)
            
            # Connect to SMTP server and send email
            logging.info(f"Connecting to SMTP server at {self.server_host}:{self.server_port}")
            
            with smtplib.SMTP(self.server_host, self.server_port, timeout=10) as server:
                server.set_debuglevel(0)  # Set to 1 for debug output
                server.sendmail(sender, recipients, msg.as_string())
            
            logging.info(f"Email sent successfully to {recipients}")
            print(f"\n✓ Email sent successfully!")
            print(f"  From: {sender}")
            print(f"  To: {', '.join(recipients)}")
            print(f"  Subject: {subject}\n")
            
            return True
            
        except InvalidEmailAddress as e:
            error_msg = f"Invalid email address: {str(e)}"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, str(e))
            print(f"\n✗ {error_msg}\n")
            return False
            
        except socket.timeout:
            error_msg = f"Connection timeout to {self.server_host}:{self.server_port}"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, "Network timeout - connection to server timed out after 10 seconds")
            print(f"\n✗ {error_msg}\n")
            return False
            
        except socket.gaierror as e:
            error_msg = f"Failed to resolve hostname {self.server_host}: {str(e)}"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, f"DNS error - failed to resolve {self.server_host}")
            print(f"\n✗ {error_msg}\n")
            return False
            
        except ConnectionRefusedError as e:
            error_msg = f"Connection refused by {self.server_host}:{self.server_port} - server may not be running"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, "Connection refused - SMTP server not accepting connections")
            print(f"\n✗ {error_msg}\n")
            return False
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, str(e))
            print(f"\n✗ {error_msg}\n")
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logging.error(error_msg)
            self._save_failed_delivery(sender, recipients, subject, f"Unexpected error: {str(e)}")
            print(f"\n✗ {error_msg}\n")
            return False
    
    def validate_email(self, email):
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if '@' in email and '.' in email.split('@')[1]:
            return True
        return False


def interactive_mode():
    """
    Interactive mode for composing and sending emails.
    """
    print("\n" + "="*60)
    print("SMTP CLIENT - Interactive Mode")
    print("="*60 + "\n")
    
    # Get server details
    server_host = input("Enter SMTP server host (default: 127.0.0.1): ").strip() or '127.0.0.1'
    server_port = input("Enter SMTP server port (default: 1025): ").strip() or '1025'
    server_port = int(server_port)
    
    # Create client
    client = SMTPClient(server_host, server_port)
    
    # Get email details
    print("\nCompose your email:")
    print("-" * 60)
    
    sender = input("From (sender email): ").strip()
    recipients = input("To (recipient email(s), comma-separated): ").strip()
    recipients = [r.strip() for r in recipients.split(',')]
    
    subject = input("Subject: ").strip()
    
    print("Body (enter your message, type 'END' on a new line to finish):")
    body_lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        body_lines.append(line)
    body = '\n'.join(body_lines)
    
    # Ask about attachments
    attachments = None
    add_attachments = input("\nAdd attachments? (y/n): ").strip().lower()
    if add_attachments == 'y':
        attachment_paths = input("Enter file path(s) (comma-separated): ").strip()
        attachments = [p.strip() for p in attachment_paths.split(',')]
    
    # Send email
    print("\nSending email...")
    client.send_email(sender, recipients, subject, body, attachments)


def send_quick_email(sender, recipients, subject, body, server_host='127.0.0.1', server_port=1025, attachments=None):
    """
    Quick function to send an email with minimal code.
    
    Args:
        sender: Sender email address
        recipients: List of recipient email addresses or single email string
        subject: Email subject
        body: Email body content
        server_host: SMTP server host (default: 127.0.0.1)
        server_port: SMTP server port (default: 1025)
        attachments: List of file paths to attach (optional)
    """
    client = SMTPClient(server_host, server_port)
    return client.send_email(sender, recipients, subject, body, attachments)


if __name__ == '__main__':
    # Run in interactive mode
    interactive_mode()
