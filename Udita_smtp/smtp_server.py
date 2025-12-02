"""
SMTP Server Implementation
This server listens for incoming emails and delivers them to recipient mailboxes.
"""

import os
import json
import logging
from datetime import datetime
from email.parser import Parser, BytesParser
from email import policy
import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPProtocol

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smtp_server.log'),
        logging.StreamHandler()
    ]
)

# Exception Classes for Error Handling
class SMTPServerException(Exception):
    """Base exception for SMTP server errors"""
    pass

class InvalidRecipient(SMTPServerException):
    """Raised when recipient email address is invalid"""
    pass

class DeliveryFailure(SMTPServerException):
    """Raised when email delivery to mailbox fails"""
    pass

class CustomSMTPHandler:
    """
    Custom SMTP Handler that processes incoming emails and delivers them to mailboxes.
    """
    
    def __init__(self, mailbox_dir='mailboxes'):
        self.mailbox_dir = mailbox_dir
        self.gui_log_queue = None  # For GUI logging
        self.failed_deliveries = []
        self.delivery_failures_file = 'server_delivery_failures.json'
        
        # Load existing failed deliveries
        self._load_failed_deliveries()
        
        # Create mailbox directory if it doesn't exist
        if not os.path.exists(self.mailbox_dir):
            os.makedirs(self.mailbox_dir)
            logging.info(f"Created mailbox directory: {self.mailbox_dir}")
            self._gui_log(f"Created mailbox directory: {self.mailbox_dir}\n")
    
    def _load_failed_deliveries(self):
        """Load failed deliveries from JSON file on startup"""
        try:
            if os.path.exists(self.delivery_failures_file):
                with open(self.delivery_failures_file, 'r') as f:
                    self.failed_deliveries = json.load(f)
                logging.info(f"Loaded {len(self.failed_deliveries)} failed deliveries from log")
            else:
                self.failed_deliveries = []
        except Exception as e:
            logging.error(f"Error loading failed deliveries: {str(e)}")
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
            
            # Persist to JSON file
            with open(self.delivery_failures_file, 'w') as f:
                json.dump(self.failed_deliveries, f, indent=4)
            
            logging.info(f"Failed delivery logged: {reason}")
        except Exception as e:
            logging.error(f"Error saving failed delivery: {str(e)}")
    
    async def handle_DATA(self, server, session, envelope):
        """
        Process incoming email messages with comprehensive error handling.
        
        Args:
            server: SMTP server instance
            session: Session information
            envelope: Email envelope containing mail_from, rcpt_tos, and content
        """
        try:
            peer = session.peer
            mailfrom = envelope.mail_from
            rcpttos = envelope.rcpt_tos
            data = envelope.content
            
            logging.info(f"Receiving email from: {peer}")
            logging.info(f"Sender: {mailfrom}")
            logging.info(f"Recipients: {rcpttos}")
            
            self._gui_log(f"📨 Receiving email from {mailfrom}\n")
            self._gui_log(f"   To: {', '.join(rcpttos)}\n")
            
            # Parse the email data using BytesParser
            try:
                msg = BytesParser(policy=policy.default).parsebytes(data if isinstance(data, bytes) else data.encode('utf-8'))
            except Exception as e:
                self.logger.error(f"Error parsing email: {str(e)}")
                self._save_failed_delivery(mailfrom, rcpttos, "Unknown", f"Email parsing error: {str(e)}")
                return '550 Error parsing email message'
            
            # Extract email details
            subject = msg.get('Subject', 'No Subject')
            from_addr = msg.get('From', mailfrom)
            to_addrs = msg.get('To', ', '.join(rcpttos))
            date = msg.get('Date', datetime.now().strftime('%a, %d %b %Y %H:%M:%S'))
            
            logging.info(f"Subject: {subject}")
            self._gui_log(f"   Subject: {subject}\n")
            
            # Validate sender
            try:
                self.validate_email(mailfrom)
            except InvalidRecipient as e:
                error_msg = f"Invalid sender: {str(e)}"
                self.logger.warning(error_msg)
                self._gui_log(f"✗ {error_msg}\n")
                self._save_failed_delivery(mailfrom, rcpttos, subject, error_msg)
                return '550 Invalid sender address'
            
            # Deliver email to each recipient's mailbox
            failed_recipients = []
            for recipient in rcpttos:
                try:
                    # Validate recipient
                    self.validate_email(recipient)
                    
                    # Deliver to mailbox
                    self.deliver_to_mailbox(recipient, mailfrom, subject, data, msg)
                    logging.info(f"Email delivered to {recipient}")
                    self._gui_log(f"✓ Email delivered to {recipient}\n")
                    
                except InvalidRecipient as e:
                    error_msg = f"Invalid recipient {recipient}: {str(e)}"
                    self.logger.warning(error_msg)
                    self._gui_log(f"✗ {error_msg}\n")
                    self._save_failed_delivery(mailfrom, [recipient], subject, error_msg)
                    failed_recipients.append(recipient)
                    
                except DeliveryFailure as e:
                    error_msg = f"Delivery failed to {recipient}: {str(e)}"
                    self.logger.error(error_msg)
                    self._gui_log(f"✗ {error_msg}\n")
                    self._save_failed_delivery(mailfrom, [recipient], subject, error_msg)
                    failed_recipients.append(recipient)
                    
                except Exception as e:
                    error_msg = f"Unexpected error delivering to {recipient}: {str(e)}"
                    self.logger.error(error_msg)
                    self._gui_log(f"✗ {error_msg}\n")
                    self._save_failed_delivery(mailfrom, [recipient], subject, error_msg)
                    failed_recipients.append(recipient)
            
            logging.info("Email processing completed\n")
            self._gui_log("\n")
            
            # Return success if at least one recipient succeeded
            if len(failed_recipients) < len(rcpttos):
                return '250 Message accepted for delivery'
            else:
                return '550 Message rejected - all recipients invalid'
            
        except Exception as e:
            error_msg = f"Unexpected error in handle_DATA: {str(e)}"
            self.logger.error(error_msg)
            self._gui_log(f"✗ {error_msg}\n")
            return '550 Error processing message'
    
    def validate_email(self, email):
        """
        Strict email validation for server-side recipient checking.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            InvalidRecipient: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise InvalidRecipient(f"Email must be a non-empty string, got {type(email)}")
        
        email = email.strip()
        
        if '@' not in email:
            raise InvalidRecipient(f"Email must contain '@' symbol: {email}")
        
        local, domain = email.rsplit('@', 1)
        
        if not local or len(local) > 64:
            raise InvalidRecipient(f"Local part must be 1-64 characters: {email}")
        
        if not domain or '.' not in domain:
            raise InvalidRecipient(f"Domain must contain a dot: {email}")
        
        if domain.startswith('.') or domain.endswith('.'):
            raise InvalidRecipient(f"Domain cannot start or end with dot: {email}")
        
        return True
    
    def deliver_to_mailbox(self, recipient, sender, subject, raw_data, parsed_msg):
        """
        Deliver email to recipient's mailbox with comprehensive error handling.
        
        Args:
            recipient: Recipient email address
            sender: Sender email address
            subject: Email subject
            raw_data: Raw email data
            parsed_msg: Parsed email message object
            
        Raises:
            DeliveryFailure: If delivery to mailbox fails
        """
        try:
            # Create recipient mailbox if it doesn't exist
            recipient_safe = recipient.replace('@', '_at_').replace('.', '_')
            recipient_mailbox = os.path.join(self.mailbox_dir, recipient_safe)
            
            # Create directory with error handling
            try:
                if not os.path.exists(recipient_mailbox):
                    os.makedirs(recipient_mailbox)
            except OSError as e:
                raise DeliveryFailure(f"Failed to create mailbox directory {recipient_mailbox}: {str(e)}")
            
            # Generate unique filename for email
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            email_filename = f"email_{timestamp}.eml"
            email_path = os.path.join(recipient_mailbox, email_filename)
            
            # Save raw email data with error handling
            try:
                with open(email_path, 'wb') as f:
                    f.write(raw_data if isinstance(raw_data, bytes) else raw_data.encode('utf-8'))
            except IOError as e:
                raise DeliveryFailure(f"Failed to write email file {email_path}: {str(e)}")
            
            # Save email metadata with error handling
            try:
                metadata = {
                    'timestamp': datetime.now().isoformat(),
                    'from': sender,
                    'to': recipient,
                    'subject': subject,
                    'filename': email_filename
                }
                
                metadata_path = os.path.join(recipient_mailbox, f"metadata_{timestamp}.json")
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
            except (IOError, json.JSONDecodeError) as e:
                raise DeliveryFailure(f"Failed to write metadata file: {str(e)}")
            
            logging.info(f"Email saved to: {email_path}")
            
        except DeliveryFailure:
            raise
        except Exception as e:
            raise DeliveryFailure(f"Unexpected error delivering to mailbox: {str(e)}")
    
    def _gui_log(self, message):
        """Send log message to GUI if available"""
        if self.gui_log_queue:
            try:
                self.gui_log_queue.put(message)
            except:
                pass


def start_server(host='127.0.0.1', port=1025):
    """
    Start the SMTP server.
    
    Args:
        host: Server host address (default: localhost)
        port: Server port (default: 1025, non-privileged port)
    """
    try:
        handler = CustomSMTPHandler()
        controller = Controller(handler, hostname=host, port=port)
        
        print(f"\n{'='*60}")
        print(f"SMTP Server is running on {host}:{port}")
        print(f"Mailboxes will be stored in './mailboxes' directory")
        print(f"Logs are being written to 'smtp_server.log'")
        print(f"Press Ctrl+C to stop the server")
        print(f"{'='*60}\n")
        
        controller.start()
        logging.info(f"SMTP Server started on {host}:{port}")
        
        # Keep the server running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        print("\nServer stopped.")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        if 'controller' in locals():
            controller.stop()


if __name__ == '__main__':
    # You can change these values or add command-line argument parsing
    HOST = '127.0.0.1'  # localhost
    PORT = 1025         # Use non-privileged port (>1024)
    
    start_server(HOST, PORT)
