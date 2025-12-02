#!/usr/bin/env python3
"""
SMTP Lab Launcher
Cross-platform launcher for the SMTP Lab GUI application.
Works on Windows, Mac, and Linux.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from smtp_gui import main
    print("Starting SMTP Lab GUI...")
    main()
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("\nPlease install required packages:")
    print("  pip3 install -r requirements.txt")
    print("\nor:")
    print("  python3 -m pip install aiosmtpd")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
