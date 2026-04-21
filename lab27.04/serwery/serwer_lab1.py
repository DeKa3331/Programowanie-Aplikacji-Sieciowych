import re
import socket


HOST = "127.0.0.1"
PORT = 1310
USERNAME = "student@localhost"
PASSWORD = "test123"
TAG = "serwer_lab1"


def make_message(text: str, seen: bool = False) -> dict[str, object]:
    flags: set[str] = set()
    if seen:
        flags.add("\\Seen")
    else:
        flags.add("\\Recent")
    return {"body": text.encode("utf-8"), "flags": flags}


MAILBOXES = {
    "INBOX": [
        make_message(
            "From: inbox1@example.com\r\nSubject: Inbox 1\r\n\r\nPierwsza wiadomosc w INBOX.\r\n"
        ),
        make_message(
            "From: inbox2@example.com\r\nSubject: Inbox 2\r\n\r\nDruga wiadomosc w INBOX.\r\n",
            seen=True,
        ),
        make_message(
            "From: inbox3@example.com\r\nSubject: Inbox 3\r\n\r\nTrzecia wiadomosc w INBOX.\r\n"
        ),
    ],
    "Sent": [
        make_message(
            "From: sent1@example.com\r\nSubject: Sent 1\r\n\r\nWiadomosc wyslana 1.\r\n",
            seen=True,
        ),
    ],
    "Archive": [
        make_message(
            "From: arch1@example.com\r\nSubject: Archive 1\r\n\r\nArchiwalna wiadomosc 1.\r\n",
            seen=True,
        ),
        make_message(
            "From: arch2@example.com\r\nSubject: Archive 2\r\n\r\nArchiwalna wiadomosc 2.\r\n",
            seen=True,
        ),
    ],
}

MAILBOX_ORDER = list(MAILBOXES.keys())


def send_line(conn: socket.socket, text: str) -> None:
    conn.sendall((text + "\r\n").encode("utf-8"))


def read_line(conn_file: socket.SocketIO) -> str:
    raw = conn_file.readline()
    if not raw:
        return ""
    return raw.decode("utf-8", errors="replace").rstrip("\r\n")


def normalize_mailbox_name(token: str) -> str:
    value = token.strip().strip('"')
    for mailbox_name in MAILBOXES:
        if mailbox_name.lower() == value.lower():
            return mailbox_name
    return value


def active_messages(mailbox_name: str) -> list[dict[str, object]]:
    return [message for message in MAILBOXES[mailbox_name] if "\\Deleted" not in message["flags"]]


def mailbox_stats(mailbox_name: str) -> tuple[int, int, int]:
    active = active_messages(mailbox_name)
    recent = sum(1 for message in active if "\\Recent" in message["flags"])
    unseen = sum(1 for message in active if "\\Seen" not in message["flags"])
    return len(active), recent, unseen


def format_flags(message: dict[str, object]) -> str:
    flags = sorted(message["flags"])
    return "(" + " ".join(flags) + ")" if flags else "()"


def parse_flags(token: str) -> set[str]:
    text = token.strip().strip("()")
    if not text:
        return set()
    return {flag for flag in text.split() if flag.startswith("\\")}


def selected_message(mailbox_name: str, seq: int) -> dict[str, object] | None:
    active = active_messages(mailbox_name)
    if seq < 1 or seq > len(active):
        return None
    return active[seq - 1]


def expunge_mailbox(mailbox_name: str) -> list[int]:
    removed: list[int] = []
    mailbox = MAILBOXES[mailbox_name]
    for index in range(len(mailbox) - 1, -1, -1):
        if "\\Deleted" in mailbox[index]["flags"]:
            removed.append(index + 1)
            del mailbox[index]
    return removed


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    print(f"[{TAG}] Klient polaczony: {addr[0]}:{addr[1]}")

    conn_file = conn.makefile("rb")
    authenticated = False
    selected_mailbox: str | None = None

    send_line(conn, f"* OK {TAG} ready")

    while True:
        raw_line = read_line(conn_file)
        if not raw_line:
            break

        print(f"[{TAG}] C: {raw_line}")
        parts = raw_line.split(" ", 2)
        if len(parts) < 2:
            send_line(conn, f"{parts[0]} BAD command not supported")
            continue

        tag = parts[0]
        command = parts[1].upper()
        args = parts[2] if len(parts) > 2 else ""

        if command == "LOGIN":
            login_parts = args.split(" ", 1)
            if len(login_parts) < 2:
                send_line(conn, f"{tag} NO LOGIN failed")
                continue

            username = login_parts[0]
            password = login_parts[1]
            if username == USERNAME and password == PASSWORD:
                authenticated = True
                send_line(conn, f"{tag} OK LOGIN completed")
            else:
                send_line(conn, f"{tag} NO LOGIN failed")

        elif not authenticated:
            send_line(conn, f"{tag} NO authenticate first")

        elif command == "LIST":
            for mailbox_name in MAILBOX_ORDER:
                send_line(conn, f'* LIST (\\HasNoChildren) "/" "{mailbox_name}"')
            send_line(conn, f"{tag} OK LIST completed")

        elif command == "STATUS":
            mailbox_name = normalize_mailbox_name(args.split(" ", 1)[0])
            if mailbox_name not in MAILBOXES:
                send_line(conn, f"{tag} NO no such mailbox")
                continue
            messages, recent, unseen = mailbox_stats(mailbox_name)
            send_line(conn, f'* STATUS "{mailbox_name}" (MESSAGES {messages} RECENT {recent} UNSEEN {unseen})')
            send_line(conn, f"{tag} OK STATUS completed")

        elif command in {"SELECT", "EXAMINE"}:
            mailbox_name = normalize_mailbox_name(args)
            if mailbox_name not in MAILBOXES:
                send_line(conn, f"{tag} NO no such mailbox")
                continue
            selected_mailbox = mailbox_name
            messages, recent, _ = mailbox_stats(mailbox_name)
            send_line(conn, f"* {messages} EXISTS")
            send_line(conn, f"* {recent} RECENT")
            mode = "READ-WRITE" if command == "SELECT" else "READ-ONLY"
            send_line(conn, f"{tag} OK [{mode}] {command} completed")

        elif command == "SEARCH":
            if selected_mailbox is None:
                send_line(conn, f"{tag} NO select a mailbox first")
                continue
            criteria = args.upper().strip()
            active = active_messages(selected_mailbox)
            result: list[int] = []
            for index, message in enumerate(active, start=1):
                if criteria == "ALL":
                    result.append(index)
                elif criteria == "UNSEEN" and "\\Seen" not in message["flags"]:
                    result.append(index)
            send_line(conn, "* SEARCH" + ("" if not result else " " + " ".join(str(item) for item in result)))
            send_line(conn, f"{tag} OK SEARCH completed")

        elif command == "FETCH":
            if selected_mailbox is None:
                send_line(conn, f"{tag} NO select a mailbox first")
                continue
            fetch_parts = args.split(" ", 1)
            if not fetch_parts:
                send_line(conn, f"{tag} BAD invalid FETCH")
                continue
            try:
                seq = int(fetch_parts[0])
            except ValueError:
                send_line(conn, f"{tag} BAD invalid message sequence")
                continue
            message = selected_message(selected_mailbox, seq)
            if message is None:
                send_line(conn, f"{tag} NO no such message")
                continue
            body = message["body"]
            send_line(conn, f"* {seq} FETCH (BODY[] {{{len(body)}}}")
            conn.sendall(body)
            send_line(conn, ")")
            send_line(conn, f"{tag} OK FETCH completed")

        elif command == "STORE":
            if selected_mailbox is None:
                send_line(conn, f"{tag} NO select a mailbox first")
                continue
            store_parts = args.split(" ", 2)
            if len(store_parts) < 3:
                send_line(conn, f"{tag} BAD invalid STORE")
                continue
            try:
                seq = int(store_parts[0])
            except ValueError:
                send_line(conn, f"{tag} BAD invalid message sequence")
                continue
            operation = store_parts[1].upper()
            flags = parse_flags(store_parts[2])
            message = selected_message(selected_mailbox, seq)
            if message is None:
                send_line(conn, f"{tag} NO no such message")
                continue
            message_flags = message["flags"]
            if operation == "+FLAGS":
                message_flags.update(flags)
            elif operation == "-FLAGS":
                for flag in flags:
                    message_flags.discard(flag)
            else:
                send_line(conn, f"{tag} BAD unsupported STORE operation")
                continue
            send_line(conn, f"* {seq} FETCH (FLAGS {format_flags(message)})")
            send_line(conn, f"{tag} OK STORE completed")

        elif command in {"EXPUNGE", "CLOSE"}:
            if selected_mailbox is None:
                send_line(conn, f"{tag} NO select a mailbox first")
                continue
            removed = expunge_mailbox(selected_mailbox)
            for seq in removed:
                send_line(conn, f"* {seq} EXPUNGE")
            send_line(conn, f"{tag} OK {command} completed")
            if command == "CLOSE":
                selected_mailbox = None

        elif command == "LOGOUT":
            send_line(conn, f"* BYE {TAG} logging out")
            send_line(conn, f"{tag} OK LOGOUT completed")
            break

        else:
            send_line(conn, f"{tag} NO command not supported")

    print(f"[{TAG}] Klient rozlaczony: {addr[0]}:{addr[1]}")


def main() -> None:
    print(f"[{TAG}] Start on {HOST}:{PORT}")
    print(f"[{TAG}] Login: {USERNAME}")
    print(f"[{TAG}] Haslo: {PASSWORD}")

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
