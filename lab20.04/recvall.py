#!/usr/bin/env python3

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


def recv_line(sock: socket.socket) -> bytes:
    return recv_all_until(sock, b"\r\n")


def recv_pop3_multiline(sock: socket.socket) -> list[bytes]:
    lines: list[bytes] = []

    while True:
        line = recv_line(sock)
        if line == b".":
            break

        if line.startswith(b".."):
            line = line[1:]

        lines.append(line)

    return lines


def decode_line(line: bytes) -> str:
    return line.decode("utf-8", errors="replace")

def require_ok(response_line: str) -> None:
    if not response_line.startswith("+OK"):
        raise RuntimeError(f"Unexpected POP3 response: {response_line}")


def send_pop3_command(sock: socket.socket, command: str) -> None:
    sock.sendall((command + "\r\n").encode("utf-8"))


def pop3_roundtrip(sock: socket.socket, command: str, log_prefix: str) -> str:
    print(f"[{log_prefix}] C: {command}")
    send_pop3_command(sock, command)
    response = decode_line(recv_line(sock))
    print(f"[{log_prefix}] S: {response}")
    require_ok(response)
    return response


def pop3_login(sock: socket.socket, email: str, password: str, log_prefix: str) -> None:
    pop3_roundtrip(sock, f"USER {email}", log_prefix)
    pop3_roundtrip(sock, f"PASS {password}", log_prefix)


def parse_stat_response(response: str) -> tuple[int, int]:
    parts = response.split()
    if len(parts) < 3:
        raise RuntimeError(f"Cannot parse STAT response: {response}")

    try:
        message_count = int(parts[1])
        total_octets = int(parts[2])
    except ValueError as error:
        raise RuntimeError(f"Cannot parse STAT numbers: {response}") from error

    return message_count, total_octets


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 1110

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect((HOST, PORT))
        greeting = decode_line(recv_line(sock))
        print(f"Connected: {greeting}")
