import socket


HOST = "127.0.0.1"
PORT = 1117
USERNAME = "student@localhost"
PASSWORD = "test123"

MESSAGES = [
    b"From: lab8a@example.com\r\nTo: student@localhost\r\nSubject: Lab8 A\r\n\r\nWiadomosc A dla zadania 8.\r\n",
    b"From: lab8b@example.com\r\nTo: student@localhost\r\nSubject: Lab8 B\r\n\r\nWiadomosc B dla zadania 8, odrobine dluzsza.\r\n",
    b"From: lab8c@example.com\r\nTo: student@localhost\r\nSubject: Lab8 C\r\n\r\nWiadomosc C dla zadania 8.\r\n",
    b"From: lab8d@example.com\r\nTo: student@localhost\r\nSubject: Lab8 D\r\n\r\nWiadomosc D dla zadania 8.\r\n",
]


def send_line(conn: socket.socket, text: str) -> None:
    conn.sendall((text + "\r\n").encode("utf-8"))


def read_line(conn_file: socket.SocketIO) -> str:
    raw = conn_file.readline()
    if not raw:
        return ""
    return raw.decode("utf-8", errors="replace").rstrip("\r\n")


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    print(f"[serwer_lab8] Klient polaczony: {addr[0]}:{addr[1]}")

    conn_file = conn.makefile("rb")
    user_ok = False
    authed = False
    deleted: set[int] = set()

    send_line(conn, "+OK POP3 lab8 ready")

    while True:
        line = read_line(conn_file)
        if not line:
            break

        print(f"[serwer_lab8] C: {line}")
        parts = line.split(" ", 1)
        command = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ""

        active = [(idx, msg) for idx, msg in enumerate(MESSAGES, start=1) if idx not in deleted]
        total_octets = sum(len(msg) for _, msg in active)

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
        elif not authed:
            send_line(conn, "-ERR not authenticated")
        elif command == "STAT":
            send_line(conn, f"+OK {len(active)} {total_octets}")
        elif command == "LIST":
            send_line(conn, f"+OK {len(active)} messages ({total_octets} octets)")
            for idx, msg in active:
                send_line(conn, f"{idx} {len(msg)}")
            send_line(conn, ".")
        elif command == "RETR":
            try:
                msg_id = int(arg)
            except ValueError:
                send_line(conn, "-ERR invalid message id")
                continue

            if msg_id < 1 or msg_id > len(MESSAGES) or msg_id in deleted:
                send_line(conn, "-ERR no such message")
                continue

            body = MESSAGES[msg_id - 1]
            send_line(conn, f"+OK {len(body)} octets")
            for raw_line in body.split(b"\r\n"):
                if raw_line == b"":
                    send_line(conn, "")
                    continue
                line_out = raw_line.decode("utf-8", errors="replace")
                if line_out.startswith("."):
                    line_out = "." + line_out
                send_line(conn, line_out)
            send_line(conn, ".")
        elif command == "DELE":
            try:
                msg_id = int(arg)
            except ValueError:
                send_line(conn, "-ERR invalid message id")
                continue

            if msg_id < 1 or msg_id > len(MESSAGES) or msg_id in deleted:
                send_line(conn, "-ERR no such message")
                continue

            deleted.add(msg_id)
            send_line(conn, "+OK message marked as deleted")
        elif command == "QUIT":
            send_line(conn, "+OK goodbye")
            break
        else:
            send_line(conn, "-ERR command not supported")

    print(f"[serwer_lab8] Klient rozlaczony: {addr[0]}:{addr[1]}")


def main() -> None:
    print(f"[serwer_lab8] Start on {HOST}:{PORT}")
    print(f"[serwer_lab8] Login: {USERNAME}")
    print(f"[serwer_lab8] Haslo: {PASSWORD}")

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
