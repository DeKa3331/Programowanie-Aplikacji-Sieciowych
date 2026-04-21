import socket


HOST = "127.0.0.1"
PORT = 1110
USERNAME = "student@localhost"
PASSWORD = "test123"

MESSAGES = [
    b"From: a@example.com\r\nTo: student@localhost\r\nSubject: Lab1\r\n\r\nWiadomosc 1.\r\n",
    b"From: b@example.com\r\nTo: student@localhost\r\nSubject: Lab1\r\n\r\nWiadomosc 2.\r\n",
]


def send_line(conn: socket.socket, text: str) -> None:
    conn.sendall((text + "\r\n").encode("utf-8"))


def read_line(conn_file: socket.SocketIO) -> str:
    raw = conn_file.readline()
    if not raw:
        return ""
    return raw.decode("utf-8", errors="replace").rstrip("\r\n")


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    print(f"[serwer_lab1] Klient polaczony: {addr[0]}:{addr[1]}")

    conn_file = conn.makefile("rb")
    authed = False
    user_ok = False

    message_sizes = [len(item) for item in MESSAGES]
    total_octets = sum(message_sizes)

    send_line(conn, "+OK POP3 lab1 ready")

    while True:
        line = read_line(conn_file)
        if not line:
            break

        print(f"[serwer_lab1] C: {line}")
        parts = line.split(" ", 1)
        command = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "USER":
            if arg == USERNAME:
                user_ok = True
                send_line(conn, "+OK user accepted")
            else:
                send_line(conn, "-ERR unknown user")
        elif command == "PASS":
            if not user_ok:
                send_line(conn, "-ERR send USER first")
            elif arg == PASSWORD:
                authed = True
                send_line(conn, "+OK mailbox locked and ready")
            else:
                send_line(conn, "-ERR invalid password")
        elif command == "STAT":
            if not authed:
                send_line(conn, "-ERR not authenticated")
            else:
                send_line(conn, f"+OK {len(MESSAGES)} {total_octets}")
        elif command == "QUIT":
            send_line(conn, "+OK goodbye")
            break
        else:
            send_line(conn, "-ERR command not supported")

    print(f"[serwer_lab1] Klient rozlaczony: {addr[0]}:{addr[1]}")


def main() -> None:
    print(f"[serwer_lab1] Start on {HOST}:{PORT}")
    print(f"[serwer_lab1] Login: {USERNAME}")
    print(f"[serwer_lab1] Haslo: {PASSWORD}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        while True:
            conn, addr = server_socket.accept()
            with conn:
                handle_client(conn, addr)


if __name__ == "__main__":
    main()
