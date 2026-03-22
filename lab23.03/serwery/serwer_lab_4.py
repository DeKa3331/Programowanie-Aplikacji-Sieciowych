#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2913


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def calculate(first: float, operator: str, second: float) -> str:
	if operator == "+":
		return str(first + second)
	if operator == "-":
		return str(first - second)
	if operator == "*":
		return str(first * second)
	if operator == "/":
		if second == 0:
			return "ERROR: division by zero"
		return str(first / second)
	return "ERROR: unsupported operator"


def run_task_4_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	print(f"[{now_str()}] UDP calc server is waiting for incoming datagrams on {host}:{port}...")

	try:
		while True:
			first_data, address = server.recvfrom(4096)
			first_text = first_data.decode("utf-8", errors="replace").strip()
			print(f"[{now_str()}] Received first value from {address}: {first_text}")

			operator_data, address_op = server.recvfrom(4096)
			operator_text = operator_data.decode("utf-8", errors="replace").strip()
			print(f"[{now_str()}] Received operator from {address_op}: {operator_text}")

			second_data, address_second = server.recvfrom(4096)
			second_text = second_data.decode("utf-8", errors="replace").strip()
			print(f"[{now_str()}] Received second value from {address_second}: {second_text}")

			if address != address_op or address != address_second:
				answer = "ERROR: inconsistent client address"
			else:
				try:
					first = float(first_text)
					second = float(second_text)
				except ValueError:
					answer = "ERROR: number expected"
				else:
					answer = calculate(first, operator_text, second)

			sent = server.sendto(answer.encode("utf-8"), address)
			print(f"[{now_str()}] Sent {sent} bytes back to {address}. Data: {answer}")
	finally:
		server.close()


def main() -> None:
	run_task_4_server(HOST, PORT)


if __name__ == "__main__":
	main()
