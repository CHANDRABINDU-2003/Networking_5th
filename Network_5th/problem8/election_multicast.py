import socket
import struct
import threading

GROUP = "224.1.1.1"
PORT = 5007
TOTAL = 5

votes = {}

def receiver(sock):
    global votes
    while len(votes) < TOTAL:
        data, _ = sock.recvfrom(1024)
        msg = data.decode().strip()
        if ":" in msg:
            user, vote = msg.split(":")
            if user not in votes:
                votes[user] = vote
                print(f"📥 Received vote from {user}: {vote}")

def main():
    global votes

    name = input("Enter electorate name (E1–E5): ").strip()

    vote = ""
    while vote not in ["A", "B"]:
        vote = input("Cast vote (A/B): ").upper().strip()

    # Create multicast socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sock.bind(("", PORT))

    # Join multicast group
    mreq = struct.pack("4s4s", socket.inet_aton(GROUP), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receiver thread
    t = threading.Thread(target=receiver, args=(sock,))
    t.daemon = True
    t.start()

    # Send own vote
    message = f"{name}:{vote}".encode()
    sock.sendto(message, (GROUP, PORT))
    print(f"📤 Sent vote: {vote}")

    # Wait for 5 votes
    while len(votes) < TOTAL:
        pass

    print("\n==================== RESULTS ====================")
    print(votes)

    A = list(votes.values()).count("A")
    B = list(votes.values()).count("B")

    print(f"Votes for A = {A}")
    print(f"Votes for B = {B}")

    if A > B:
        print("🏆 Winner = A")
    elif B > A:
        print("🏆 Winner = B")
    else:
        print("🤝 It's a tie!")

if __name__ == "__main__":
    main()
