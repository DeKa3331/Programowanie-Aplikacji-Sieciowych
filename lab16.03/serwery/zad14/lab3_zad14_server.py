#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2910


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def check_msg_syntax(text: str) -> str:
    parts = text.split(";")
    if len(parts) != 7:
        return "BAD_SYNTAX"

    if not (
        parts[0] == "zad14odp"
        and parts[1] == "src"
        and parts[3] == "dst"
        and parts[5] == "data"
    ):
        return "BAD_SYNTAX"

    try:
        src_port = int(parts[2])
        dst_port = int(parts[4])
    except ValueError:
        return "BAD_SYNTAX"

    payload = parts[6]
    if src_port == 2900 and dst_port == 35211 and payload == "hello :)":
        return "TAK"
    return "NIE"


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((HOST, PORT))
    except OSError as error:
        print(f"Bind failed: {error}")
        sys.exit(1)

    print(f"[{now_str()}] UDP server is waiting for incoming datagrams...")

    try:
        while True:
            data, address = sock.recvfrom(1024)
            decoded = data.decode("utf-8", errors="replace")
            print(
                f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {decoded}"
            )

            if not data:
                continue

            answer = check_msg_syntax(decoded)
            sent = sock.sendto(answer.encode("utf-8"), address)
            print(f"[{now_str()}] Sent {sent} bytes back to {address}.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()


