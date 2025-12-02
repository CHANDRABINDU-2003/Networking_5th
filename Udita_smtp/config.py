"""
Configuration settings for SMTP Lab project.
"""

# Server Configuration
SERVER_CONFIG = {
    'host': '127.0.0.1',      # localhost
    'port': 1025,              # Non-privileged port
    'mailbox_dir': 'mailboxes' # Directory to store mailboxes
}

# Client Configuration
CLIENT_CONFIG = {
    'default_server_host': '127.0.0.1',
    'default_server_port': 1025,
    'timeout': 30  # Connection timeout in seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'server_log_file': 'smtp_server.log',
    'client_log_file': 'smtp_client.log',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Email Validation Rules
EMAIL_VALIDATION = {
    'max_subject_length': 200,
    'max_body_length': 10000,
    'max_recipients': 50,
    'allowed_domains': None  # None = allow all domains, or provide list of allowed domains
}

# Attachment Configuration (Optional Feature)
ATTACHMENT_CONFIG = {
    'enabled': True,
    'max_file_size_mb': 10,
    'max_attachments': 5,
    'allowed_extensions': ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.zip']
}
