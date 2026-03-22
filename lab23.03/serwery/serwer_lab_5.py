#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2914


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_task_5_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	print(f"[{now_str()}] UDP reverse DNS server is waiting for incoming datagrams on {host}:{port}...")

	try:
		while True:
			try:
				data, address = server.recvfrom(4096)
			except ConnectionResetError as error:
				print(f"[{now_str()}] UDP reset ignored: {error}")
				continue

			ip_text = data.decode("utf-8", errors="replace").strip()
			print(f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {ip_text}")

			if not ip_text:
				answer = "ERROR: empty ip"
			else:
				try:
					hostname, _, _ = socket.gethostbyaddr(ip_text)
					answer = hostname
				except OSError:
					answer = "ERROR: hostname not found"

			sent = server.sendto(answer.encode("utf-8"), address)
			print(f"[{now_str()}] Sent {sent} bytes back to {address}. Data: {answer}")
	finally:
		server.close()


def main() -> None:
	run_task_5_server(HOST, PORT)


if __name__ == "__main__":
	main()
