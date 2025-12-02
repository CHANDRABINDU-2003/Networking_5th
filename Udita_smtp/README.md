# SMTP Lab in Python

A comprehensive SMTP email client-server application with an **interactive GUI**. Cross-platform compatible with Windows, Mac, and Linux.

## 📋 Overview

This project implements a complete SMTP email system with:
- **Modern GUI Application** - Easy-to-use graphical interface
- **SMTP Server** - Receives and stores emails in local mailboxes
- **SMTP Client** - Send emails with attachments
- **Email Viewer** - Browse and read received emails

## ✨ Features

- 🖥️ **Cross-Platform GUI** - Works on Windows, Mac, and Linux
- 📧 **Full Email Support** - Send/receive emails with attachments
- 📬 **Mailbox Management** - View and organize received emails
- 🔄 **Real-time Logging** - Monitor server activity
- 🎨 **Modern Interface** - Clean and intuitive design
- 📎 **Attachment Support** - Send multiple file attachments
- 👥 **Multiple Recipients** - Send to multiple addresses

## 🔧 Requirements

- **Python 3.7 or higher**
- **pip** (Python package manager)

### Platform-Specific Notes

**Mac/Linux:**
- Python 3 usually comes pre-installed
- Use `python3` and `pip3` commands

**Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

## 📦 Installation

### 1. Download/Clone the Project

```bash
cd /path/to/abhinash_smtp
```

### 2. Install Dependencies

**On Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

**On Windows:**
```bash
pip install -r requirements.txt
```

### 3. Verify tkinter (GUI library)

**Mac:** Already included with Python

**Linux:** If GUI doesn't start, install tkinter:
```bash
sudo apt-get install python3-tk
```

**Windows:** Already included with Python

## 🚀 Quick Start

### Launch the GUI Application

**Mac/Linux:**
```bash
# Method 1: Using the launcher script
python3 run.py

# Method 2: Direct launch
python3 smtp_gui.py

# Method 3: Make executable and run
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
# Method 1: Double-click run.bat

# Method 2: Command line
python run.py

# Method 3: Direct launch
python smtp_gui.py
```

### Using the GUI

1. **Start Server Tab** 📬
   - Click "▶ Start Server" to begin receiving emails
   - Default: localhost (127.0.0.1) on port 1025
   - Server logs appear in real-time

2. **Send Email Tab** 📧
   - Fill in sender, recipient(s), subject, and message
   - Add attachments with "➕ Add" button
   - Click "📤 Send Email"
   - Multiple recipients: separate with commas

3. **Mailbox Tab** 📬
   - Click "🔄 Refresh" to see new emails
   - Select a mailbox from dropdown
   - Click on emails to read them
   - View attachments in email details

## 📁 Project Structure

```
abhinash_smtp/
├── smtp_gui.py             # Main GUI application
├── smtp_server.py          # SMTP server backend
├── smtp_client.py          # SMTP client backend
├── config.py               # Configuration settings
├── view_mailbox.py         # CLI mailbox viewer (optional)
├── run.py                  # Cross-platform launcher
├── run.sh                  # Mac/Linux launcher script
├── run.bat                 # Windows launcher script
├── README.md               # This file
├── requirements.txt        # Dependencies
├── mailboxes/              # Email storage (auto-created)
├── smtp_server.log         # Server logs
└── smtp_client.log         # Client logs
```

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
# Server Configuration
SERVER_CONFIG = {
    'host': '127.0.0.1',      # Server host
    'port': 1025,              # Server port
    'mailbox_dir': 'mailboxes' # Mailbox storage directory
}

# Client Configuration
CLIENT_CONFIG = {
    'default_server_host': '127.0.0.1',
    'default_server_port': 1025,
    'timeout': 30
}

# Email Validation Rules
EMAIL_VALIDATION = {
    'max_subject_length': 200,
    'max_body_length': 10000,
    'max_recipients': 50
}

# Attachment Configuration
ATTACHMENT_CONFIG = {
    'enabled': True,
    'max_file_size_mb': 10,
    'max_attachments': 5
}
```

## 📚 Examples

### Example 1: Simple Email via GUI
1. Start the server in the "Server" tab
2. Go to "Send Email" tab
3. Fill in the form:
   - From: alice@example.com
   - To: bob@example.com
   - Subject: Hello
   - Message: This is a test!
4. Click "Send Email"
5. Check "Mailbox" tab to see the delivered email

### Example 2: Programmatic Usage (Optional)

You can still use the CLI if needed:

```python
from smtp_client import SMTPClient

client = SMTPClient('127.0.0.1', 1025)
client.send_email(
    sender='alice@example.com',
    recipients='bob@example.com',
    subject='Hello',
    body='This is a test email.'
)
```

### Example 3: Email with Attachments

In the GUI:
1. Compose your email
2. Click "➕ Add" under Attachments
3. Select files to attach
4. Send email

## 🛡️ Error Handling

The GUI provides clear error messages:
- **Connection refused**: Server not running - start it first
- **Invalid email**: Check email format (must contain @ and .)
- **File not found**: Verify attachment file paths

## 📝 Logging

Logs are generated automatically:
- **smtp_server.log** - Server activity and email deliveries
- **smtp_client.log** - Email sending operations
- **GUI console** - Real-time server logs in the Server tab

## 🎁 Additional Features

### GUI Features
- 📊 Real-time server monitoring
- 🎨 Clean, intuitive interface
- 📱 Responsive design
- 🔔 Status notifications
- 📎 Drag-and-drop attachment support (via Add button)

### Backend Features
- ✅ Full SMTP protocol implementation
- ✅ Metadata storage (JSON)
- ✅ Email validation
- ✅ Multiple mailbox support
- ✅ Thread-safe operations

## 🔍 Troubleshooting

### GUI won't start

**Issue**: `ModuleNotFoundError: No module named 'tkinter'`

**Solution (Linux):**
```bash
sudo apt-get install python3-tk
```

**Solution (Mac/Windows):** Reinstall Python from official website

### Server won't start

**Issue**: Port already in use

**Solution**: 
- Change port in GUI (try 1026, 1027, etc.)
- Or kill the process using port 1025

### Emails not sending

**Issue**: Connection refused

**Solution**:
1. Make sure server is running (green status in GUI)
2. Check host/port match between client and server tabs
3. Check firewall settings

### Mac-Specific

**Issue**: Python 2 vs Python 3

**Solution**: Always use `python3` command:
```bash
python3 run.py
```

## 🌐 Cross-Platform Notes

### File Paths
- Uses `os.path.join()` for compatibility
- Works with both `/` (Mac/Linux) and `\` (Windows)

### Commands
- **Mac/Linux**: Use `python3` and `pip3`
- **Windows**: Use `python` and `pip`

### Line Endings
- Project handles different line endings automatically

## 📖 Understanding SMTP Protocol

The application implements the SMTP protocol:

1. **Connection**: Client connects to server
2. **Handshake**: EHLO command exchange
3. **Mail Transaction**: 
   - MAIL FROM: sender
   - RCPT TO: recipient(s)
   - DATA: email content
4. **Termination**: QUIT

## 🧪 Testing on Mac

Your friend can test on Mac with these commands:

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Launch GUI
python3 run.py

# Or use the shell script
chmod +x run.sh
./run.sh
```

## 📄 License

Educational project for learning SMTP protocol implementation.

## 🆘 Support

For issues:
1. Check log files for errors
2. Verify server is running before sending
3. Ensure proper email format
4. Check firewall/antivirus settings

---

## 🎯 Quick Reference

**Start Application:**
- Mac/Linux: `python3 run.py`
- Windows: Double-click `run.bat` or `python run.py`

**Default Server:** 127.0.0.1:1025

**Mailboxes Location:** `./mailboxes/`

**Logs:** `smtp_server.log` and `smtp_client.log`

---

**Happy Email Testing! 📧**
