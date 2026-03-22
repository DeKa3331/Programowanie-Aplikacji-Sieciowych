import socket
from typing import Callable


TASK_TOGGLES: dict[int, bool] = {
	1: True,
	2: True,
	3: True,
	4: True,
	5: True,
	6: True,
	7: True,
	8: True,
	9: True,
	10: True,
	11: True,
}

TASK1_HOST = "127.0.0.1"
TASK1_PORT = 2910
TASK1_MESSAGE = "jaka jest data i czas?"

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 2911
TASK2_MESSAGE = "echo tcp - test"

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 2912
TASK3_MESSAGE = "echo udp - test"

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 2913

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 2914

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 2915

TASK7_HOST = "127.0.0.1"
TASK7_PORT = 2916
TASK7_MAX_LEN = 20

TASK8_HOST = "127.0.0.1"
TASK8_PORT = 2917
TASK8_EXACT_LEN = 20

TASK9_HOST = "127.0.0.1"
TASK9_PORT = 2918
TASK9_UDP_HEX = (
	"ed 74 0b 55 00 24 ef fd 70 72 6f 67 72 61 "
	"6d 6d 69 6e 67 20 69 6e 20 70 79 74 68 6f "
	"6e 20 69 73 20 66 75 6e"
)

TASK10_HOST = "127.0.0.1"
TASK10_PORT = 2919
TASK10_TCP_HEX = (
	"0b 54 89 8b 1f 9a 18 ec bb b1 64 f2 80 18 "
	"00 e3 67 71 00 00 01 01 08 0a 02 c1 a4 ee "
	"00 1a 4c ee 68 65 6c 6c 6f 20 3a 29"
)

TASK11_HOST = "127.0.0.1"
TASK11_PORT = 2920
TASK11_IP_HEX = (
	"45 00 00 4e f7 fa 40 00 38 06 9d 33 d4 b6 18 1b "
	"c0 a8 00 02 0b 54 b9 a6 fb f9 3c 57 c1 0a 06 c1 "
	"80 18 00 e3 ce 9c 00 00 01 01 08 0a 03 a6 eb 01 "
	"00 0b f8 e5 6e 65 74 77 6f 72 6b 20 70 72 6f 67 "
	"72 61 6d 6d 69 6e 67 20 69 73 20 66 75 6e"
)


def run_task(task_number: int) -> None:
	print(f"[Zadanie {task_number}] TODO: uzupełnij aktualną treść zadania.")


def task_1() -> None:
	try:
		with socket.create_connection((TASK1_HOST, TASK1_PORT), timeout=5) as connection:
			payload = TASK1_MESSAGE.encode("utf-8")
			connection.sendall(payload)
			response = connection.recv(4096).decode("utf-8", errors="replace")

		print(f"[Zadanie 1] Wysłano: {TASK1_MESSAGE}")
		print(f"[Zadanie 1] Otrzymano datę/czas: {response}")
	except OSError as error:
		print(f"[Zadanie 1] Błąd połączenia/komunikacji: {error}")


def task_2() -> None:
	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=5) as connection:
			payload = TASK2_MESSAGE.encode("utf-8")
			connection.sendall(payload)
			response = connection.recv(4096).decode("utf-8", errors="replace")

		print(f"[Zadanie 2] Wysłano: {TASK2_MESSAGE}")
		print(f"[Zadanie 2] Otrzymano echo: {response}")
	except OSError as error:
		print(f"[Zadanie 2] Błąd połączenia/komunikacji: {error}")


def task_3() -> None:
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			payload = TASK3_MESSAGE.encode("utf-8")
			sock.sendto(payload, (TASK3_HOST, TASK3_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 3] Wysłano: {TASK3_MESSAGE}")
		print(f"[Zadanie 3] Otrzymano echo: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 3] Błąd połączenia/komunikacji: {error}")


def task_4() -> None:
	print("[Zadanie 4] Klient UDP kalkulatora")

	first_number = input("Podaj pierwszą liczbę: ").strip()
	operator = input("Podaj operator (+, -, *, /): ").strip()
	second_number = input("Podaj drugą liczbę: ").strip()

	if operator not in {"+", "-", "*", "/"}:
		print("[Zadanie 4] Niepoprawny operator. Dozwolone: +, -, *, /")
		return

	try:
		float(first_number)
		float(second_number)
	except ValueError:
		print("[Zadanie 4] Obie wartości muszą być liczbami.")
		return

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			target = (TASK4_HOST, TASK4_PORT)
			sock.sendto(first_number.encode("utf-8"), target)
			sock.sendto(operator.encode("utf-8"), target)
			sock.sendto(second_number.encode("utf-8"), target)
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 4] Wynik z serwera: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 4] Błąd połączenia/komunikacji: {error}")


def task_5() -> None:
	ip_text = input("[Zadanie 5] Podaj adres IP: ").strip()

	if not ip_text:
		print("[Zadanie 5] Adres IP nie może być pusty.")
		return

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(ip_text.encode("utf-8"), (TASK5_HOST, TASK5_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 5] Dla IP {ip_text} hostname: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 5] Błąd połączenia/komunikacji: {error}")


def task_6() -> None:
	hostname_text = input("[Zadanie 6] Podaj nazwę hosta: ").strip()

	if not hostname_text:
		print("[Zadanie 6] Nazwa hosta nie może być pusta.")
		return

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(hostname_text.encode("utf-8"), (TASK6_HOST, TASK6_PORT))
			response, _ = sock.recvfrom(4096)

		print(
			f"[Zadanie 6] Dla hosta {hostname_text} adres IP: {response.decode('utf-8', errors='replace')}"
		)
	except OSError as error:
		print(f"[Zadanie 6] Błąd połączenia/komunikacji: {error}")


def task_7() -> None:
	def recv_exact(connection: socket.socket, expected_len: int) -> bytes:
		chunks: list[bytes] = []
		received_len = 0

		while received_len < expected_len:
			part = connection.recv(expected_len - received_len)
			if not part:
				break
			chunks.append(part)
			received_len += len(part)

		return b"".join(chunks)

	print(f"[Zadanie 7] TCP max {TASK7_MAX_LEN} znaków")
	message = input("Podaj wiadomość: ")
	message_to_send = message.ljust(TASK7_MAX_LEN)[:TASK7_MAX_LEN]

	try:
		with socket.create_connection((TASK7_HOST, TASK7_PORT), timeout=5) as connection:
			payload = message_to_send.encode("utf-8")
			connection.sendall(payload)
			response = recv_exact(connection, TASK7_MAX_LEN)

		print(f"[Zadanie 7] Wysłano ({len(message_to_send)} znaków): {repr(message_to_send)}")
		print(f"[Zadanie 7] Odebrano ({len(response)} bajtów): {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 7] Błąd połączenia/komunikacji: {error}")


def task_8() -> None:
	def send_exact(connection: socket.socket, data: bytes) -> None:
		total_sent = 0
		while total_sent < len(data):
			sent = connection.send(data[total_sent:])
			if sent == 0:
				raise OSError("Połączenie zostało zamknięte podczas wysyłania danych.")
			total_sent += sent

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

	print(f"[Zadanie 8] TCP z gwarancją pełnych {TASK8_EXACT_LEN} bajtów")
	message = input("Podaj wiadomość: ")
	message_to_send = message.ljust(TASK8_EXACT_LEN)[:TASK8_EXACT_LEN]
	payload = message_to_send.encode("utf-8")

	try:
		with socket.create_connection((TASK8_HOST, TASK8_PORT), timeout=5) as connection:
			send_exact(connection, payload)
			response = recv_exact(connection, TASK8_EXACT_LEN)

		print(f"[Zadanie 8] Wysłano dokładnie {len(payload)} bajtów.")
		print(f"[Zadanie 8] Odebrano dokładnie {len(response)} bajtów.")
		print(f"[Zadanie 8] Odpowiedź: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 8] Błąd połączenia/komunikacji: {error}")


def task_9() -> None:
	def parse_udp_datagram(hex_payload: str) -> tuple[int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 8:
			raise ValueError("Datagram UDP musi mieć co najmniej 8 bajtów nagłówka.")

		src_port = int.from_bytes(raw[0:2], byteorder="big")
		dst_port = int.from_bytes(raw[2:4], byteorder="big")
		total_len = int.from_bytes(raw[4:6], byteorder="big")

		if total_len < 8 or total_len > len(raw):
			raise ValueError("Niepoprawne pole length w nagłówku UDP.")

		data = raw[8:total_len]
		return src_port, dst_port, data

	try:
		src_port, dst_port, data_bytes = parse_udp_datagram(TASK9_UDP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 9] Błąd parsowania datagramu: {error}")
		return

	message = f"zad13odp;src;{src_port};dst;{dst_port};data;{data_text}"

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(message.encode("utf-8"), (TASK9_HOST, TASK9_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 9] Wysłano: {message}")
		print(f"[Zadanie 9] Odpowiedź serwera: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 9] Błąd połączenia/komunikacji: {error}")


def task_10() -> None:
	def parse_tcp_segment(hex_payload: str) -> tuple[int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 20:
			raise ValueError("Segment TCP musi mieć co najmniej 20 bajtów nagłówka.")

		src_port = int.from_bytes(raw[0:2], byteorder="big")
		dst_port = int.from_bytes(raw[2:4], byteorder="big")
		data_offset = (raw[12] >> 4)
		header_len = data_offset * 4

		if header_len < 20 or header_len > len(raw):
			raise ValueError("Niepoprawne pole data offset w nagłówku TCP.")

		data = raw[header_len:]
		return src_port, dst_port, data

	try:
		src_port, dst_port, data_bytes = parse_tcp_segment(TASK10_TCP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 10] Błąd parsowania segmentu: {error}")
		return

	message = f"zad14odp;src;{src_port};dst;{dst_port};data;{data_text}"

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(message.encode("utf-8"), (TASK10_HOST, TASK10_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 10] Wysłano: {message}")
		print(f"[Zadanie 10] Odpowiedź serwera: {response.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 10] Błąd połączenia/komunikacji: {error}")


def task_11() -> None:
	def parse_ip_packet(hex_payload: str) -> tuple[int, str, str, int, int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 20:
			raise ValueError("Pakiet IP musi mieć co najmniej 20 bajtów nagłówka.")

		version = raw[0] >> 4
		ip_header_len = (raw[0] & 0x0F) * 4
		protocol = raw[9]
		src_ip = ".".join(str(b) for b in raw[12:16])
		dst_ip = ".".join(str(b) for b in raw[16:20])

		transport = raw[ip_header_len:]
		if len(transport) < 20:
			raise ValueError("Za krótki segment transportowy.")

		src_port = int.from_bytes(transport[0:2], byteorder="big")
		dst_port = int.from_bytes(transport[2:4], byteorder="big")

		if protocol == 6:
			tcp_data_offset = (transport[12] >> 4) * 4
			data = transport[tcp_data_offset:]
		elif protocol == 17:
			udp_len = int.from_bytes(transport[4:6], byteorder="big")
			data = transport[8:udp_len]
		else:
			data = transport[20:]

		return version, src_ip, dst_ip, protocol, src_port, dst_port, data

	try:
		version, src_ip, dst_ip, protocol, src_port, dst_port, data_bytes = parse_ip_packet(TASK11_IP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 11] Błąd parsowania pakietu: {error}")
		return

	msg_a = f"zad15odpA;ver;{version};srcip;{src_ip};dstip;{dst_ip};type;{protocol}"

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(msg_a.encode("utf-8"), (TASK11_HOST, TASK11_PORT))
			response_a, _ = sock.recvfrom(4096)
			answer_a = response_a.decode("utf-8", errors="replace")

			print(f"[Zadanie 11] Wysłano A: {msg_a}")
			print(f"[Zadanie 11] Odpowiedź A: {answer_a}")

			if answer_a == "TAK":
				msg_b = f"zad15odpB;srcport;{src_port};dstport;{dst_port};data;{data_text}"
				sock.sendto(msg_b.encode("utf-8"), (TASK11_HOST, TASK11_PORT))
				response_b, _ = sock.recvfrom(4096)
				print(f"[Zadanie 11] Wysłano B: {msg_b}")
				print(f"[Zadanie 11] Odpowiedź B: {response_b.decode('utf-8', errors='replace')}")
	except OSError as error:
		print(f"[Zadanie 11] Błąd połączenia/komunikacji: {error}")


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
		9: task_9,
		10: task_10,
		11: task_11,
	}

	any_task_enabled = False

	for task_number in range(1, 12):
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