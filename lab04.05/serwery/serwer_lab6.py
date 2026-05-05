from __future__ import annotations

import base64
import socket
from email.utils import formatdate


HOST = "127.0.0.1"
PORT = 8006
IMAGE_PATH = "/image.jpg"
LAST_MODIFIED = formatdate(usegmt=True)

JPEG_BYTES = base64.b64decode(
	"/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUQEhIVFhUVFRUVFRUVFRUVFRUVFRUWFhUVFRUYHSggGBolGxUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGhAQGzclHyU3LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAAEAAQMBIgACEQEDEQH/xAAbAAACAwEBAQAAAAAAAAAAAAAEBQADBgIBB//EADYQAAIBAwMBBQYEBQQDAQAAAAECAwAEEQUSITFBBhMiUWEUMnGBkaGx0RQjQlJy4fAHFSRCYpL/xAAZAQEAAwEBAAAAAAAAAAAAAAAAAQIDBAX/xAAgEQEAAwACAgMBAAAAAAAAAAAAAQIRAyExEkEEE0Jx/9oADAMBAAIRAxEAPwD7+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//Z"
)


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
	return "\r\n".join(lines).encode("iso-8859-1") + b"\r\n" + body


def _parse_range(range_header: str, total_size: int) -> tuple[int, int]:
	if not range_header.startswith("bytes=") or "-" not in range_header:
		raise ValueError(range_header)

	range_spec = range_header.removeprefix("bytes=")
	start_text, end_text = range_spec.split("-", 1)
	start = int(start_text)
	end = int(end_text)
	if start < 0 or end < start or end >= total_size:
		raise ValueError(range_header)
	return start, end


def _handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
	request_text = _read_request(connection)
	request_line = request_text.split("\r\n", 1)[0]
	print(f"[serwer_lab6] Client connected: {address[0]}:{address[1]}")
	print(f"[serwer_lab6] C: {request_line}")

	request_headers: dict[str, str] = {}
	for raw_line in request_text.split("\r\n")[1:]:
		if not raw_line:
			break
		if ":" in raw_line:
			name, value = raw_line.split(":", 1)
			request_headers[name.strip().lower()] = value.strip()

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

	if path != IMAGE_PATH:
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

	total_size = len(JPEG_BYTES)
	if request_headers.get("if-modified-since") == LAST_MODIFIED:
		response = _build_response(
			"HTTP/1.1 304 Not Modified",
			{
				"Last-Modified": LAST_MODIFIED,
				"Accept-Ranges": "bytes",
				"Connection": "close",
			},
		)
		connection.sendall(response)
		print("[serwer_lab6] Session finished (not modified)")
		return

	range_header = request_headers.get("range")
	if range_header:
		try:
			start, end = _parse_range(range_header, total_size)
		except ValueError:
			response = _build_response(
				"HTTP/1.1 416 Range Not Satisfiable",
				{
					"Content-Range": f"bytes */{total_size}",
					"Content-Length": "0",
					"Connection": "close",
				},
			)
			connection.sendall(response)
			return

		body = JPEG_BYTES[start : end + 1]
		response = _build_response(
			"HTTP/1.1 206 Partial Content",
			{
				"Content-Type": "image/jpeg",
				"Accept-Ranges": "bytes",
				"Last-Modified": LAST_MODIFIED,
				"Content-Range": f"bytes {start}-{end}/{total_size}",
				"Content-Length": str(len(body)),
				"Connection": "close",
			},
			body if method == "GET" else b"",
		)
		connection.sendall(response)
		print("[serwer_lab6] Session finished (range)")
		return

	body = JPEG_BYTES
	response = _build_response(
		"HTTP/1.1 200 OK",
		{
			"Content-Type": "image/jpeg",
			"Accept-Ranges": "bytes",
			"Last-Modified": LAST_MODIFIED,
			"Content-Length": str(len(body)),
			"Connection": "close",
		},
		body if method == "GET" else b"",
	)
	connection.sendall(response)
	print("[serwer_lab6] Session finished")


def main() -> None:
	print(f"[serwer_lab6] HTTP server listening on {HOST}:{PORT}")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((HOST, PORT))
		server_socket.listen(5)

		while True:
			connection, address = server_socket.accept()
			with connection:
				try:
					_handle_client(connection, address)
				except (OSError, ValueError) as error:
					print(f"[serwer_lab6] Socket error: {error}")


if __name__ == "__main__":
	main()