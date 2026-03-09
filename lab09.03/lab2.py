import socket
import sys
from typing import Callable


HOST1 = "ntp.task.gda.pl"
PORT1 = 13

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 2900

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 2900

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 2901
TASK4_MESSAGE = "Hi from task 4 client"

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 2901

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 2902


TASK_TOGGLES: dict[int, bool] = {
	1: False, #not working
	2: False,
	3: False,
	4: False,
	5: False,
	6: False,
	7: False,
	8: True,
	9: False, #TBD
	10: False, #TBD
	11: False, #TBD
	12: False, #TBD
}

#not working
def task_1() -> None:
	try:
		with socket.create_connection((HOST1, PORT1), timeout=5) as connection:
			connection.sendall(b"\r\n")
			response = connection.recv(4096)

		print(f"[Zadanie 1] Data i czas: {response.decode('ascii', errors='replace').strip()}")
	except OSError as error:
		print(f"[Zadanie 1] Błąd połączenia/komunikacji: {error}")


def task_2() -> None:
	TASK2_MESSAGE = "Hi from task 2 client"
	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=5) as connection:
			payload = TASK2_MESSAGE.encode("utf-8")
			connection.sendall(payload)
			response = connection.recv(4096).decode("utf-8", errors="replace")

		print(f"[Zadanie 2] Wysłano: {TASK2_MESSAGE}")
		print(f"[Zadanie 2] Odebrano: {response}")
	except OSError as error:
		print(f"[Zadanie 2] Błąd połączenia/komunikacji: {error}")


def task_3() -> None:
	print("[Zadanie 3] Łączenie z serwerem 212.182.24.27:2900...")

	try:
		with socket.create_connection((TASK3_HOST, TASK3_PORT), timeout=5) as connection:
			print("[Zadanie 3] Połączono. Wpisz tekst i naciśnij Enter.")
			print("[Zadanie 3] Aby zakończyć wpisz: exit")

			while True:
				message = input("Ty> ")

				if message.strip().lower() == "exit":
					print("[Zadanie 3] Zakończono połączenie.")
					break

				connection.sendall(message.encode("utf-8"))
				response = connection.recv(4096)

				if not response:
					print("[Zadanie 3] Serwer zamknął połączenie.")
					break

				print(f"Serwer> {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 3] Błąd połączenia/komunikacji: {error}")


def task_4() -> None:
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			payload = TASK4_MESSAGE.encode("utf-8")
			sock.sendto(payload, (TASK4_HOST, TASK4_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 4] Wysłano: {TASK4_MESSAGE}")
		print(f"[Zadanie 4] Odebrano: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 4] Błąd połączenia/komunikacji: {error}")


def task_5() -> None:
	print("[Zadanie 5] Klient UDP uruchomiony dla 212.182.24.27:2901")
	print("[Zadanie 5] Wpisz wiadomość i Enter (exit aby zakończyć).")

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)

			while True:
				message = input("Ty> ")

				if message.strip().lower() == "exit":
					print("[Zadanie 5] Zakończono.")
					break

				sock.sendto(message.encode("utf-8"), (TASK5_HOST, TASK5_PORT))
				response, _ = sock.recvfrom(4096)
				print(f"Serwer> {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 5] Błąd połączenia/komunikacji: {error}")


def task_6() -> None:
	print("[Zadanie 6] Klient UDP kalkulatora dla 212.182.24.27:2902")

	first_number = input("Podaj pierwszą liczbę: ").strip()
	operator = input("Podaj operator (+, -, *, /): ").strip()
	second_number = input("Podaj drugą liczbę: ").strip()

	if operator not in {"+", "-", "*", "/"}:
		print("[Zadanie 6] Niepoprawny operator. Dozwolone: +, -, *, /")
		return

	try:
		float(first_number)
		float(second_number)
	except ValueError:
		print("[Zadanie 6] Obie wartości muszą być liczbami.")
		return

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			target = (TASK6_HOST, TASK6_PORT)
			first_payload = first_number.encode("ascii")
			operator_payload = operator.encode("ascii")
			second_payload = second_number.encode("ascii")

			sock.sendto(first_payload, target)
			sock.sendto(operator_payload, target)
			sock.sendto(second_payload, target)

			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 6] Wynik z serwera: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 6] Błąd połączenia/komunikacji: {error}")


def get_tcp_service_name(port_number: int) -> str:
	try:
		return socket.getservbyport(port_number, "tcp")
	except OSError:
		return "nieznana"


def task_7() -> None:
	print("[Zadanie 7] Sprawdzanie portu TCP i usługi")

	if len(sys.argv) < 3:
		print("[Zadanie 7] Użycie: python lab2.py <host> <port>")
		print("[Zadanie 7] Przykład: python lab2.py localhost 80")
		return

	server_address = sys.argv[1]
	port = sys.argv[2]

	try:
		port_number = int(port)
	except ValueError:
		print("[Zadanie 7] Numer portu musi być liczbą.")
		return

	service_name = get_tcp_service_name(port_number)

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.settimeout(3)
			result = sock.connect_ex((server_address, port_number))

			if result == 0:
				print(f"[Zadanie 7] Port {port_number} jest OTWARTY.")
				print(f"[Zadanie 7] Usługa na porcie {port_number}: {service_name}")
			else:
				print(f"[Zadanie 7] Port {port_number} jest ZAMKNIĘTY.")
				print(f"[Zadanie 7] Typowa usługa dla portu {port_number}: {service_name}")
	except socket.gaierror:
		print(f"[Zadanie 7] Nie można rozwiązać adresu: {server_address}")
	except OSError as error:
		print(f"[Zadanie 7] Błąd połączenia: {error}")


def task_8() -> None:
	print("[Zadanie 8] Skanowanie zakresu portów TCP i usług")

	if len(sys.argv) < 4:
		print("[Zadanie 8] Użycie: python lab2.py <host> <port_od> <port_do>")
		print("[Zadanie 8] Przykład: python lab2.py localhost 20 100")
		return

	server_address = sys.argv[1]
	port_start_raw = sys.argv[2]
	port_end_raw = sys.argv[3]

	try:
		port_start = int(port_start_raw)
		port_end = int(port_end_raw)
	except ValueError:
		print("[Zadanie 8] port_od i port_do muszą być liczbami.")
		return

	if port_start < 1 or port_end > 65535 or port_start > port_end:
		print("[Zadanie 8] Podaj poprawny zakres: 1..65535 i port_od <= port_do.")
		return

	for port_number in range(port_start, port_end + 1):
		service_name = get_tcp_service_name(port_number)

		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				sock.settimeout(0.5)
				result = sock.connect_ex((server_address, port_number))

				if result == 0:
					print(f"[Zadanie 8] Port {port_number}: OTWARTY | usługa: {service_name}")
				else:
					print(f"[Zadanie 8] Port {port_number}: ZAMKNIĘTY | usługa: {service_name}")
		except socket.gaierror:
			print(f"[Zadanie 8] Nie można rozwiązać adresu: {server_address}")
			return
		except OSError as error:
			print(f"[Zadanie 8] Port {port_number}: błąd sprawdzania ({error})")

		


def main() -> None:
	task_handlers: dict[int, Callable[[], None]] = {
		1: task_1,
		2: task_2,
		3: task_3,
		4: task_4,
		5: task_5,
		6: task_6,
		7: task_7,
		8: task_8,
	}

	any_task_enabled = False

	for task_number in range(1, 13):
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
