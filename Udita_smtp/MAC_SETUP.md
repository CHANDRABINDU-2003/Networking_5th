# SMTP Lab - Mac Setup Guide

## 🍎 Quick Setup for Mac

### Step 1: Install Dependencies

Open Terminal and navigate to the project folder:

```bash
cd /path/to/abhinash_smtp

# Install required package
pip3 install -r requirements.txt
```

If `pip3` is not found, install it:
```bash
# Install pip for Python 3
python3 -m ensurepip --upgrade
```

### Step 2: Run the Application

**Option 1 - Using the launcher:**
```bash
python3 run.py
```

**Option 2 - Using the shell script:**
```bash
# Make it executable (first time only)
chmod +x run.sh

# Run it
./run.sh
```

**Option 3 - Direct launch:**
```bash
python3 smtp_gui.py
```

### Step 3: Use the Application

1. **Server Tab** - Click "Start Server" (use default 127.0.0.1:1025)
2. **Send Email Tab** - Compose and send emails
3. **Mailbox Tab** - View received emails

## 🔧 Troubleshooting on Mac

### Issue: "command not found: python"
**Solution:** Use `python3` instead of `python`

### Issue: "No module named 'tkinter'"
**Solution:** tkinter comes with Python on Mac. If missing, reinstall Python:
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python with tkinter
brew install python-tk@3.11
```

### Issue: "Permission denied"
**Solution:** Make the script executable:
```bash
chmod +x run.sh
```

### Issue: Port already in use
**Solution:** Change the port in the GUI (try 1026, 1027, etc.)

## 🎯 Testing the Application

### Test 1: Send a simple email
1. Start server in GUI
2. Go to "Send Email" tab
3. Fill in:
   - From: alice@example.com
   - To: bob@example.com
   - Subject: Test from Mac
   - Message: Hello from my Mac!
4. Click "Send Email"
5. Check "Mailbox" tab → Select bob@example.com → See the email!

### Test 2: Send with attachments
1. In "Send Email" tab
2. Click "➕ Add" under Attachments
3. Select any file (txt, pdf, jpg, etc.)
4. Send email
5. View in Mailbox - you'll see 📎 indicating attachments

## 📁 File Locations on Mac

All files are stored in the project folder:

```
abhinash_smtp/
├── mailboxes/           # Received emails (created automatically)
├── smtp_server.log      # Server activity log
├── smtp_client.log      # Client activity log
└── [other files...]
```

## 🚀 Pro Tips for Mac Users

1. **Create a Desktop Shortcut:**
   ```bash
   # Create an alias to launch easily
   echo 'alias smtp-lab="cd ~/path/to/abhinash_smtp && python3 run.py"' >> ~/.zshrc
   source ~/.zshrc
   
   # Now just type: smtp-lab
   ```

2. **Run in Background:**
   ```bash
   python3 run.py &
   ```

3. **View Logs in Real-time:**
   ```bash
   tail -f smtp_server.log
   ```

## ✅ Verification Checklist

- [ ] Python 3.7+ installed (`python3 --version`)
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] GUI launches without errors
- [ ] Can start server
- [ ] Can send emails
- [ ] Can view received emails

## 🎓 Educational Notes

This project demonstrates:
- SMTP protocol fundamentals
- Client-server architecture
- GUI programming with tkinter
- Cross-platform Python development
- Email message structure (MIME)

## 📞 Need Help?

If you encounter issues:
1. Check `smtp_server.log` for server errors
2. Check `smtp_client.log` for sending errors
3. Verify Python version: `python3 --version` (should be 3.7+)
4. Ensure no firewall is blocking port 1025

---

**Enjoy learning about email systems! 📧🍎**
