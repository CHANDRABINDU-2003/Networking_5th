import socket
import random
import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


# -------------------------------------------------
#                UDP SERVER CODE
# -------------------------------------------------

HOST = "0.0.0.0"
PORT = 9999
BUFFER_SIZE = 10000


def handle_request(server_socket, data, addr):
    """Handle incoming file request from one client."""
    filename = data.decode().strip()
    print(f"Client {addr} requested: {filename}")

    if os.path.exists(filename):
        server_socket.sendto(b"OK", addr)
        time.sleep(0.1)

        with open(filename, "rb") as f:
            while True:
                chunk_size = random.randint(1000, 2000)
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                server_socket.sendto(chunk, addr)
                print(f"Sent {len(chunk)} bytes to {addr}")
                time.sleep(0.05)

        server_socket.sendto(b"EOF", addr)
        print(f"Streaming complete for {filename}")

    else:
        server_socket.sendto(b"ERROR", addr)
        print(f"File not found: {filename}")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print(f"🚀 UDP Streaming Server running on {HOST}:{PORT}")

    while True:
        data, addr = server_socket.recvfrom(2048)

        thread = threading.Thread(
            target=handle_request,
            args=(server_socket, data, addr),
            daemon=True
        )
        thread.start()


# -------------------------------------------------
#                GUI CLIENT CODE
# -------------------------------------------------

class UDPStreamingClient:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Streaming Client")
        self.master.configure(bg="#2C3E50")

        # Chat-like display box
        self.log_area = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, width=80, height=25,
            font=("Arial", 12), bg="#34495E", fg="white", state=tk.DISABLED
        )
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Input frame
        self.input_frame = tk.Frame(master, bg="#2C3E50")
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Input box
        self.input_text = tk.Entry(
            self.input_frame, font=("Arial", 12),
            bg="white", fg="black", width=60
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        self.input_text.bind("<Return>", self.send_request)

        # Send button
        self.send_button = tk.Button(
            self.input_frame, text="Request",
            command=self.send_request,
            font=("Arial", 12), bg="#1ABC9C", fg="white", width=12
        )
        self.send_button.pack(side=tk.RIGHT)

        # UDP socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(5)

        self.output_file = None
        self.player_launched = False
        self.bytes_received = 0

        self.add_log("System: Enter the multimedia filename (e.g., 18.mp4).", "yellow")

    def add_log(self, msg, color="white"):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.tag_configure('color', foreground=color)
        self.log_area.yview(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def send_request(self, event=None):
        filename = self.input_text.get().strip()
        if not filename:
            return

        self.add_log(f"You requested: {filename}", "lightgreen")

        self.output_file = f"streaming_{filename}"
        self.bytes_received = 0
        self.player_launched = False

        try:
            self.client.sendto(filename.encode(), ("127.0.0.1", PORT))
        except:
            self.add_log("Error: Cannot send request!", "red")
            return

        self.add_log("Waiting for server response...", "lightblue")

        threading.Thread(target=self.start_streaming, daemon=True).start()
        self.input_text.delete(0, tk.END)

    def start_streaming(self):
        try:
            response, _ = self.client.recvfrom(1024)

            if response != b'OK':
                self.add_log("Error: File not found on server!", "red")
                return

            self.add_log("Streaming started...", "yellow")

            with open(self.output_file, "wb") as f:
                while True:
                    try:
                        data, _ = self.client.recvfrom(2048)

                        if data == b"EOF":
                            self.add_log("Streaming complete!", "yellow")
                            break

                        f.write(data)
                        f.flush()
                        self.bytes_received += len(data)

                        self.add_log(f"Received: {self.bytes_received} bytes", "lightblue")

                        if self.bytes_received >= BUFFER_SIZE and not self.player_launched:
                            self.player_launched = True
                            self.add_log(
                                f"\nBuffer reached {BUFFER_SIZE} bytes. You can now play:",
                                "lightgreen"
                            )
                            self.add_log(self.output_file, "lightgreen")

                    except socket.timeout:
                        self.add_log("Stream timeout!", "red")
                        break

        except Exception as e:
            self.add_log(f"Error: {str(e)}", "red")


#              MAIN FUNCTION (RUN ALL)

if __name__ == "__main__":
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Start GUI client
    root = tk.Tk()
    app = UDPStreamingClient(root)
    root.mainloop()
