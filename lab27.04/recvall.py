#!/usr/bin/env python3

import re
import socket


_SOCKET_BUFFERS: dict[int, bytearray] = {}


def _buffer_for(sock: socket.socket) -> bytearray:
    key = sock.fileno()
    if key < 0:
        raise OSError("Socket is closed")

    if key not in _SOCKET_BUFFERS:
        _SOCKET_BUFFERS[key] = bytearray()

    return _SOCKET_BUFFERS[key]


def recv_all_until(sock: socket.socket, terminator: bytes, chunk_size: int = 4096) -> bytes:
    if not terminator:
        raise ValueError("terminator cannot be empty")

    data = _buffer_for(sock)

    while True:
        pos = data.find(terminator)
        if pos != -1:
            line = bytes(data[:pos])
            del data[: pos + len(terminator)]
            return line

        chunk = sock.recv(chunk_size)
        if not chunk:
            raise OSError("Connection closed before terminator was received")

        data.extend(chunk)


def recv_exact(sock: socket.socket, size: int) -> bytes:
    if size < 0:
        raise ValueError("size cannot be negative")

    buffer = _buffer_for(sock)
    data = bytearray()

    while len(data) < size:
        if buffer:
            take = min(size - len(data), len(buffer))
            data.extend(buffer[:take])
            del buffer[:take]
            continue

        chunk = sock.recv(max(1, size - len(data)))
        if not chunk:
            raise OSError("Connection closed before enough data was received")

        if len(chunk) <= size - len(data):
            data.extend(chunk)
        else:
            needed = size - len(data)
            data.extend(chunk[:needed])
            buffer.extend(chunk[needed:])

    return bytes(data)


def recv_line(sock: socket.socket) -> bytes:
    return recv_all_until(sock, b"\r\n")


def decode_line(line: bytes) -> str:
    return line.decode("utf-8", errors="replace")


def send_imap_command(sock: socket.socket, tag: str, command: str) -> None:
    sock.sendall((f"{tag} {command}\r\n").encode("utf-8"))


_STATUS_RE = re.compile(r"MESSAGES\s+(\d+).+UNSEEN\s+(\d+)", re.IGNORECASE)
_LITERAL_RE = re.compile(r"\{(\d+)\}$")


def parse_status_counts(line: str) -> tuple[int, int]:
    match = _STATUS_RE.search(line)
    if not match:
        raise RuntimeError(f"Cannot parse STATUS response: {line}")
    return int(match.group(1)), int(match.group(2))


def parse_literal_size(line: str) -> int:
    match = _LITERAL_RE.search(line)
    if not match:
        raise RuntimeError(f"Cannot parse IMAP literal size: {line}")
    return int(match.group(1))


class ImapSession:
    def __init__(self, connection: socket.socket, log_prefix: str) -> None:
        self.connection = connection
        self.log_prefix = log_prefix
        self.tag_index = 0

    def next_tag(self) -> str:
        self.tag_index += 1
        return f"A{self.tag_index:03d}"

    def read_until_tag(self, tag: str) -> list[str]:
        lines: list[str] = []

        while True:
            line = decode_line(recv_line(self.connection))
            print(f"[{self.log_prefix}] S: {line}")
            lines.append(line)
            if line.startswith(f"{tag} "):
                if not line.startswith(f"{tag} OK"):
                    raise RuntimeError(f"Unexpected IMAP response: {line}")
                return lines

    def command(self, command: str) -> list[str]:
        tag = self.next_tag()
        print(f"[{self.log_prefix}] C: {tag} {command}")
        send_imap_command(self.connection, tag, command)
        return self.read_until_tag(tag)

    def command_allow_failure(self, command: str) -> list[str]:
        tag = self.next_tag()
        print(f"[{self.log_prefix}] C: {tag} {command}")
        send_imap_command(self.connection, tag, command)

        lines: list[str] = []
        while True:
            line = decode_line(recv_line(self.connection))
            print(f"[{self.log_prefix}] S: {line}")
            lines.append(line)
            if line.startswith(f"{tag} "):
                if not (line.startswith(f"{tag} OK") or line.startswith(f"{tag} NO") or line.startswith(f"{tag} BAD")):
                    raise RuntimeError(f"Unexpected IMAP response: {line}")
                return lines

    def login(self, email: str, password: str) -> None:
        self.command(f"LOGIN {email} {password}")

    def logout(self) -> None:
        self.command("LOGOUT")

    def list_mailboxes(self) -> list[str]:
        lines = self.command('LIST "" "*"')
        mailboxes: list[str] = []
        for line in lines:
            if not line.startswith("* LIST "):
                continue
            parts = line.split('"')
            if len(parts) >= 2:
                mailboxes.append(parts[-2])
        return mailboxes

    def status(self, mailbox: str) -> tuple[int, int]:
        lines = self.command(f'STATUS "{mailbox}" (MESSAGES UNSEEN)')
        for line in lines:
            if line.startswith("* STATUS "):
                return parse_status_counts(line)
        raise RuntimeError(f"STATUS response missing for {mailbox}")

    def select_mailbox(self, mailbox: str) -> int:
        lines = self.command(f'SELECT "{mailbox}"')
        for line in lines:
            if line.startswith("* ") and line.endswith(" EXISTS"):
                parts = line.split()
                return int(parts[1])
        raise RuntimeError(f"SELECT response missing EXISTS for {mailbox}")

    def search(self, criteria: str) -> list[int]:
        lines = self.command(f"SEARCH {criteria}")
        for line in lines:
            if line.startswith("* SEARCH"):
                parts = line.split()[2:]
                result: list[int] = []
                for item in parts:
                    try:
                        result.append(int(item))
                    except ValueError:
                        continue
                return result
        return []

    def fetch_message(self, seq: int) -> str:
        tag = self.next_tag()
        print(f"[{self.log_prefix}] C: {tag} FETCH {seq} BODY[]")
        send_imap_command(self.connection, tag, f"FETCH {seq} BODY[]")

        header = decode_line(recv_line(self.connection))
        print(f"[{self.log_prefix}] S: {header}")
        if not header.startswith(f"* {seq} FETCH "):
            raise RuntimeError(f"Unexpected FETCH header: {header}")

        literal_size = parse_literal_size(header)
        body_bytes = recv_exact(self.connection, literal_size)
        body_text = body_bytes.decode("utf-8", errors="replace")

        print(f"[{self.log_prefix}] S: [message body]")
        for line in body_text.rstrip("\r\n").splitlines():
            print(f"[{self.log_prefix}] S: {line}")

        closing = decode_line(recv_line(self.connection))
        print(f"[{self.log_prefix}] S: {closing}")
        if closing != ")":
            raise RuntimeError(f"Unexpected FETCH closing line: {closing}")

        tagged = decode_line(recv_line(self.connection))
        print(f"[{self.log_prefix}] S: {tagged}")
        if not tagged.startswith(f"{tag} OK"):
            raise RuntimeError(f"Unexpected FETCH completion: {tagged}")

        return body_text

    def store_flags(self, seq: int, operation: str, flags: str) -> None:
        self.command(f"STORE {seq} {operation} ({flags})")

    def expunge(self) -> None:
        self.command("EXPUNGE")


def connect_and_login(host: str, port: int, email: str, password: str, prefix: str) -> ImapSession:
    connection = socket.create_connection((host, port), timeout=15)
    connection.settimeout(15)
    session = ImapSession(connection, prefix)

    greeting = decode_line(recv_line(connection))
    print(f"[{prefix}] S: {greeting}")
    if not greeting.startswith("* OK"):
        raise RuntimeError(f"Unexpected IMAP greeting: {greeting}")

    session.login(email, password)
    return session
