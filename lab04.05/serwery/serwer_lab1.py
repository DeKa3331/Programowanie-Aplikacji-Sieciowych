from __future__ import annotations

import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8001
HTML_PATH = Path(__file__).resolve().parents[1] / "examples" / "index.html"


def _read_request(connection: socket.socket) -> str:
	buffer = bytearray()
	separator = b"\r\n\r\n"
	while separator not in buffer:
		chunk = connection.recv(4096)
		if not chunk:
			break
		buffer.extend(chunk)
	return buffer.decode("iso-8859-1", errors="replace")


def _build_response(status_line: str, headers: dict[str, str], body: bytes = b"") -> bytes:
	lines = [status_line]
	for name, value in headers.items():
		lines.append(f"{name}: {value}")
	lines.append("")
	headers_blob = "\r\n".join(lines).encode("iso-8859-1") + b"\r\n"
	return headers_blob + body


def _handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
	request_text = _read_request(connection)
	request_line = request_text.split("\r\n", 1)[0]
	print(f"[serwer_lab1] Client connected: {address[0]}:{address[1]}")
	print(f"[serwer_lab1] C: {request_line}")

	parts = request_line.split()
	method = parts[0] if len(parts) >= 1 else ""
	path = parts[1] if len(parts) >= 2 else ""

	if method not in {"GET", "HEAD"}:
		response = _build_response(
			"HTTP/1.1 405 Method Not Allowed",
			{
				"Content-Length": "0",
				"Connection": "close",
				"Allow": "GET, HEAD",
			},
		)
		connection.sendall(response)
		return

	if path != "/html":
		body = b"Not Found"
		response = _build_response(
			"HTTP/1.1 404 Not Found",
			{
				"Content-Type": "text/plain; charset=utf-8",
				"Content-Length": str(len(body)),
				"Connection": "close",
			},
			body if method == "GET" else b"",
		)
		connection.sendall(response)
		return

	body = HTML_PATH.read_bytes()
	response = _build_response(
		"HTTP/1.1 200 OK",
		{
			"Content-Type": "text/html; charset=utf-8",
			"Content-Length": str(len(body)),
			"Connection": "close",
		},
		body if method == "GET" else b"",
	)
	connection.sendall(response)
	print("[serwer_lab1] Session finished")


def main() -> None:
	print(f"[serwer_lab1] HTTP server listening on {HOST}:{PORT}")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((HOST, PORT))
		server_socket.listen(5)

		while True:
			connection, address = server_socket.accept()
			with connection:
				try:
					_handle_client(connection, address)
				except OSError as error:
					print(f"[serwer_lab1] Socket error: {error}")


if __name__ == "__main__":
	main()
