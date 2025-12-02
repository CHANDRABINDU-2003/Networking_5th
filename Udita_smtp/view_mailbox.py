"""
Mailbox Viewer Utility
View received emails in the mailboxes directory.
"""

import os
import json
from email import policy
from email.parser import BytesParser
from datetime import datetime


def list_mailboxes(mailbox_dir='mailboxes'):
    """List all mailboxes (recipients)."""
    if not os.path.exists(mailbox_dir):
        print(f"No mailboxes directory found at: {mailbox_dir}")
        return []
    
    mailboxes = [d for d in os.listdir(mailbox_dir) 
                 if os.path.isdir(os.path.join(mailbox_dir, d))]
    return mailboxes


def get_emails_in_mailbox(mailbox_dir, mailbox_name):
    """Get all emails in a specific mailbox."""
    mailbox_path = os.path.join(mailbox_dir, mailbox_name)
    emails = []
    
    # Get all .eml files
    eml_files = [f for f in os.listdir(mailbox_path) if f.endswith('.eml')]
    
    for eml_file in eml_files:
        eml_path = os.path.join(mailbox_path, eml_file)
        
        # Try to find corresponding metadata
        metadata_file = eml_file.replace('email_', 'metadata_').replace('.eml', '.json')
        metadata_path = os.path.join(mailbox_path, metadata_file)
        
        metadata = None
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        emails.append({
            'eml_file': eml_file,
            'eml_path': eml_path,
            'metadata': metadata
        })
    
    # Sort by filename (which includes timestamp)
    emails.sort(key=lambda x: x['eml_file'], reverse=True)
    return emails


def display_email(email_data):
    """Display a single email."""
    eml_path = email_data['eml_path']
    metadata = email_data['metadata']
    
    print("\n" + "="*70)
    
    if metadata:
        print(f"From: {metadata.get('from', 'Unknown')}")
        print(f"To: {metadata.get('to', 'Unknown')}")
        print(f"Subject: {metadata.get('subject', 'No Subject')}")
        print(f"Date: {metadata.get('timestamp', 'Unknown')}")
    
    print("-"*70)

    # Read and parse the email
    try:
        with open(eml_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # helper to decode bytes fallback
        def _safe_decode(payload_bytes):
            if payload_bytes is None:
                return ''
            if isinstance(payload_bytes, bytes):
                try:
                    return payload_bytes.decode('utf-8')
                except Exception:
                    return payload_bytes.decode('utf-8', errors='replace')
            return str(payload_bytes)

        # Find a plain-text body first, fall back to HTML if needed
        body_text = None
        html_text = None
        attachments = []

        if msg.is_multipart():
            for part in msg.iter_parts():
                ctype = part.get_content_type()
                cdisp = part.get_content_disposition()  # 'attachment', 'inline', or None
                filename = part.get_filename()

                # Collect attachments (filename or explicit attachment disposition)
                if cdisp == 'attachment' or filename:
                    attachments.append({'filename': filename or 'unnamed', 'part': part})
                    continue

                # Prefer text/plain
                if ctype == 'text/plain' and body_text is None:
                    try:
                        body_text = part.get_content()
                    except Exception:
                        body_text = _safe_decode(part.get_payload(decode=True))
                    continue

                # Keep html if no plain text available
                if ctype == 'text/html' and html_text is None:
                    try:
                        html_text = part.get_content()
                    except Exception:
                        html_text = _safe_decode(part.get_payload(decode=True))
        else:
            # Single part message
            ctype = msg.get_content_type()
            if ctype.startswith('text/'):
                try:
                    body_text = msg.get_content()
                except Exception:
                    body_text = _safe_decode(msg.get_payload(decode=True))

        # Print body
        if body_text:
            print(body_text)
        elif html_text:
            print("[HTML content — raw]")
            print(html_text)
        else:
            print("[No text body found]")

        # Show attachments if any
        if attachments:
            print("\n" + "-"*70)
            print(f"Attachments ({len(attachments)}):")
            for att in attachments:
                print(f"  📎 {att['filename']}")

    except Exception as e:
        print(f"Error reading email: {str(e)}")
    
    print("="*70)


def main():
    print("\n" + "="*70)
    print("MAILBOX VIEWER")
    print("="*70 + "\n")
    
    mailbox_dir = 'mailboxes'
    
    # List all mailboxes
    mailboxes = list_mailboxes(mailbox_dir)
    
    if not mailboxes:
        print("No mailboxes found. Send some emails first!")
        return
    
    print(f"Found {len(mailboxes)} mailbox(es):\n")
    
    for i, mailbox in enumerate(mailboxes, 1):
        # Convert back to email format
        email_addr = mailbox.replace('_at_', '@').replace('_', '.')
        emails = get_emails_in_mailbox(mailbox_dir, mailbox)
        print(f"{i}. {email_addr} ({len(emails)} email(s))")
    
    print("\n" + "-"*70)
    
    # Let user choose a mailbox to view
    while True:
        choice = input("\nEnter mailbox number to view (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("\nGoodbye!")
            break
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(mailboxes):
                selected_mailbox = mailboxes[choice_num - 1]
                emails = get_emails_in_mailbox(mailbox_dir, selected_mailbox)
                
                if not emails:
                    print(f"\nNo emails in this mailbox.")
                    continue
                
                print(f"\n{len(emails)} email(s) in this mailbox:")
                
                for i, email_data in enumerate(emails, 1):
                    metadata = email_data['metadata']
                    if metadata:
                        print(f"\n{i}. Subject: {metadata.get('subject', 'No Subject')}")
                        print(f"   From: {metadata.get('from', 'Unknown')}")
                        print(f"   Date: {metadata.get('timestamp', 'Unknown')}")
                
                # Let user select an email to view
                email_choice = input("\nEnter email number to view (or 'b' to go back): ").strip()
                
                if email_choice.lower() == 'b':
                    continue
                
                try:
                    email_num = int(email_choice)
                    if 1 <= email_num <= len(emails):
                        display_email(emails[email_num - 1])
                    else:
                        print("Invalid email number.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("Invalid mailbox number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == '__main__':
    main()
