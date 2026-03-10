import socket
from datetime import datetime


HOST = "127.0.0.1"
PORT = 13013


def main() -> None:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((HOST, PORT))
		server.listen(10)

		print(f"Serwer daty/czasu działa na {HOST}:{PORT}")
		print("Zatrzymanie: Ctrl+C")

		while True:
			client, address = server.accept()
			with client:
				now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
				client.sendall(now_text.encode("ascii", errors="replace"))
				print(f"Obsłużono klienta {address}: {now_text.strip()}")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nSerwer zatrzymany.")
