#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2918


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def check_msg_syntax(text: str) -> str:
	parts = text.split(";")
	if len(parts) != 7:
		return "BAD_SYNTAX"

	if not (
		parts[0] == "zad13odp"
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
	if src_port == 60788 and dst_port == 2901 and payload == "programming in python is fun":
		return "TAK"
	return "NIE"


def run_task_9_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	if sys.platform == "win32" and hasattr(socket, "SIO_UDP_CONNRESET"):
		try:
			server.ioctl(socket.SIO_UDP_CONNRESET, False)
		except OSError:
			pass

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	print(f"[{now_str()}] UDP validation server (zad9) is waiting on {host}:{port}...")

	try:
		while True:
			try:
				data, address = server.recvfrom(4096)
			except ConnectionResetError:
				continue

			decoded = data.decode("utf-8", errors="replace")
			print(f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {decoded}")

			if not data:
				continue

			answer = check_msg_syntax(decoded)
			sent = server.sendto(answer.encode("utf-8"), address)
			print(f"[{now_str()}] Sent {sent} bytes back to {address}. Data: {answer}")
	finally:
		server.close()


def main() -> None:
	run_task_9_server(HOST, PORT)


if __name__ == "__main__":
	main()
