import socket
import time
from typing import Callable


TASK_TOGGLES: dict[int, bool] = {
	1: False,
	2: False,
	3: False,
	4: True,
}

BUFFER_SIZE = 1024

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 5000

TASK3_HOST = "127.0.0.1"
TASK3_TCP_PORT = 5000
TASK3_KNOCK_PORTS = (3666, 4666, 5666)
TASK3_KNOCK_MESSAGE = "PING"

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 5000
TASK4_MESSAGE = b"ping"
TASK4_ITERATIONS = 10000

#task 1 to jest wywolanie serwera z task2
def task_1() -> None:
	print(f"[Zadanie 1] Test klienta do serwera: {TASK2_HOST}:{TASK2_PORT}")
	print("[Zadanie 1] Wpisuj kolejne liczby (q aby zakonczyc).")

	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=5) as connection:
			while True:
				guess = input("[Zadanie 1] Podaj liczbe do wyslania: ").strip()

				if guess.lower() in {"q", "quit", "exit"}:
					print("[Zadanie 1] Koniec pracy klienta.")
					break

				if not guess:
					print("[Zadanie 1] Nic nie wpisano.")
					continue

				connection.sendall(guess.encode("utf-8"))
				response = connection.recv(BUFFER_SIZE)

				if not response:
					print("[Zadanie 1] Serwer zamknal polaczenie.")
					break

				response_text = response.decode("utf-8", errors="replace")
				print(f"[Zadanie 1] Wyslano: {guess}")
				print(f"[Zadanie 1] Odpowiedz serwera: {response_text}")

				if "Brawo!" in response_text:
					print("[Zadanie 1] Liczba odgadnieta. Koniec klienta.")
					break
	except OSError as error:
		print(f"[Zadanie 1] Blad polaczenia/komunikacji: {error}")
	

#tutaj zadnaiem jest serwer wiec wykorzystam do pokazania ze dziala zadanie1. Printy 
# podczas strzelanai sie zgadzac nie beda, ale nie widze sensu tego poprawiac
def task_2() -> None:
	print("[Zadanie 2] Alias do zadania 1.")
	task_1()


def task_3() -> None:
	print("[Zadanie 3] Test port-knockingu na localhost.")
	print(f"[Zadanie 3] Sekwencja UDP: {', '.join(str(port) for port in TASK3_KNOCK_PORTS)}")

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
			udp_socket.settimeout(3)

			for port in TASK3_KNOCK_PORTS:
				udp_socket.sendto(TASK3_KNOCK_MESSAGE.encode("utf-8"), (TASK3_HOST, port))
				response, _ = udp_socket.recvfrom(BUFFER_SIZE)
				response_text = response.decode("utf-8", errors="replace")
				print(f"[Zadanie 3] UDP {port} -> {response_text}")

		connection = None
		for _ in range(10):
			try:
				connection = socket.create_connection((TASK3_HOST, TASK3_TCP_PORT), timeout=1)
				break
			except OSError:
				time.sleep(0.2)

		if connection is None:
			print("[Zadanie 3] Nie udalo sie polaczyc z ukrytym TCP.")
			return

		with connection:
			connection.settimeout(5)
			connection.sendall(b"HELLO") #synchronizacja z serwerem, nie ma znaczenia co wyslemy, wazne zeby cos wyslac i odebrac odpowiedz
			welcome = connection.recv(BUFFER_SIZE)
			if not welcome:
				print("[Zadanie 3] Serwer TCP nie odeslal odpowiedzi.")
				return

			print(f"[Zadanie 3] TCP odpowiedz: {welcome.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 3] Blad podczas testu port-knockingu: {error}")


def task_4() -> None:
	def recv_exact(connection: socket.socket, expected_len: int) -> bytes:
		chunks: list[bytes] = []
		received_len = 0

		while received_len < expected_len:
			part = connection.recv(expected_len - received_len)
			if not part:
				raise OSError("Połączenie zostało zamknięte podczas odbierania danych.")
			chunks.append(part)
			received_len += len(part)

		return b"".join(chunks)

	print("[Zadanie 4] Porównanie czasu TCP i UDP na localhost.")
	print(f"[Zadanie 4] Host/port: {TASK4_HOST}:{TASK4_PORT}")
	print(f"[Zadanie 4] Liczba pakietów: {TASK4_ITERATIONS}")

	try:
		with socket.create_connection((TASK4_HOST, TASK4_PORT), timeout=5) as tcp_connection:
			tcp_connection.settimeout(5)
			tcp_start = time.perf_counter()
			for _ in range(TASK4_ITERATIONS):
				tcp_connection.sendall(TASK4_MESSAGE)
				recv_exact(tcp_connection, len(TASK4_MESSAGE))
			tcp_end = time.perf_counter()

		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
			udp_socket.settimeout(5)
			udp_start = time.perf_counter()
			for _ in range(TASK4_ITERATIONS):
				udp_socket.sendto(TASK4_MESSAGE, (TASK4_HOST, TASK4_PORT))
				udp_socket.recvfrom(BUFFER_SIZE)
			udp_end = time.perf_counter()

		tcp_time = tcp_end - tcp_start
		udp_time = udp_end - udp_start

		print(f"[Zadanie 4] TCP czas: {tcp_time:.6f}s")
		print(f"[Zadanie 4] UDP czas: {udp_time:.6f}s")

		if tcp_time < udp_time:
			print("[Zadanie 4] Krótszy czas miał TCP.")
		elif udp_time < tcp_time:
			print("[Zadanie 4] Krótszy czas miało UDP.")
		else:
			print("[Zadanie 4] Czasy są takie same.")
	except OSError as error:
		print(f"[Zadanie 4] Blad podczas pomiaru czasu: {error}")



def main() -> None:
	task_handlers: dict[int, Callable[[], None]] = {
		1: task_1,
		2: task_2,
		3: task_3,
		4: task_4,
	}

	any_task_enabled = False

	for task_number in range(1, 5):
		if not TASK_TOGGLES.get(task_number, False):
			continue

		any_task_enabled = True
		handler = task_handlers.get(task_number)

		if handler is None:
			print(f"[Zadanie {task_number}] Brak implementacji.")
			continue

		handler()

	if not any_task_enabled:
		print("brak taskow")


if __name__ == "__main__":
	main()
