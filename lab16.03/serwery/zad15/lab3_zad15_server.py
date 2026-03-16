#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2911


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def check_msg_a_syntax(text: str) -> str:
    parts = text.split(";")
    if len(parts) != 9:
        return "BAD_SYNTAX"

    if not (
        parts[0] == "zad15odpA"
        and parts[1] == "ver"
        and parts[3] == "srcip"
        and parts[5] == "dstip"
        and parts[7] == "type"
    ):
        return "BAD_SYNTAX"

    try:
        version = int(parts[2])
        packet_type = int(parts[8])
    except ValueError:
        return "NIE"

    src_ip = parts[4]
    dst_ip = parts[6]
    if (
        version == 4
        and packet_type == 6
        and src_ip == "212.182.24.27"
        and dst_ip == "192.168.0.2"
    ):
        return "TAK"
    return "NIE"


def check_msg_b_syntax(text: str) -> str:
    parts = text.split(";")
    if len(parts) != 7:
        return "BAD_SYNTAX"

    if not (
        parts[0] == "zad15odpB"
        and parts[1] == "srcport"
        and parts[3] == "dstport"
        and parts[5] == "data"
    ):
        return "BAD_SYNTAX"

    try:
        src_port = int(parts[2])
        dst_port = int(parts[4])
    except ValueError:
        return "NIE"

    payload = parts[6]
    if src_port == 2900 and dst_port == 47526 and payload == "network programming is fun":
        return "TAK"
    return "NIE"


def route_message(text: str) -> str:
    parts = text.split(";")
    if not parts:
        return "BAD_SYNTAX"

    if parts[0] == "zad15odpA":
        return check_msg_a_syntax(text)
    if parts[0] == "zad15odpB":
        return check_msg_b_syntax(text)
    return "BAD_SYNTAX"


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

            answer = route_message(decoded)
            sent = sock.sendto(answer.encode("utf-8"), address)
            print(f"[{now_str()}] Sent {sent} bytes back to {address}.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
