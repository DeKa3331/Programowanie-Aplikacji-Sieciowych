#!/usr/bin/env python
import sys
import socket

# Toggles dla zadań
zad1toggle = True
zad2toggle = True
zad3toggle = True
zad4toggle = True
zad5toggle = True
zad6toggle = True
zad7toggle = True


#zad1
if zad1toggle:
	source = input("Podaj nazwę pliku do skopiowania: ")
	
	with open(source, 'r') as src, open('lab1zad1.txt', 'w') as dst:
		for line in src:
			dst.write(line)
	
	print("Plik został skopiowany do lab1zad1.txt")

#zad2
if zad2toggle:
	source_img = input("Podaj nazwę pliku graficznego: ")
	
	with open(source_img, 'rb') as src, open('lab1zad2.png', 'wb') as dst:
		dst.write(src.read())
	
	print("Plik graficzny został skopiowany do lab1zad2.png")

#zad3
if zad3toggle:
	ip_address = input("Podaj adres IP: ")
	
	parts = ip_address.split('.')
	
	if len(parts) == 4:
		valid = True
		for part in parts:
			if not part.isdigit() or not (0 <= int(part) <= 255):
				valid = False
				break
		
		if valid:
			print("Adres IP jest poprawny")
		else:
			print("Adres IP jest niepoprawny")
	else:
		print("Adres IP jest niepoprawny")

#zad4
#lab02.03.py 127.0.0.1
if zad4toggle:
	if len(sys.argv) > 1:
		ip_address = sys.argv[1]
		try:
			hostname = socket.gethostbyaddr(ip_address)[0]
			print(f"Hostname dla {ip_address}: {hostname}")
		except socket.herror:
			print(f"Nie można znaleźć hostname dla {ip_address}")
		except Exception as e:
			print(f"Błąd: {e}")
	else:
		print("brak argumentu: podaj adres IP jako argument")

#zad5
#lab02.03.py localhost
if zad5toggle:
	if len(sys.argv) > 1:
		hostname = sys.argv[1]
		try:
			ip_address = socket.gethostbyname(hostname)
			print(f"Adres IP dla {hostname}: {ip_address}")
		except socket.gaierror:
			print(f"Nie można znaleźć adresu IP dla {hostname}")
		except Exception as e:
			print(f"Błąd: {e}")
	else:
		print("brak argumentu: podaj hostname jako argument")

#zad6
#w oddzielnej konsoli uruchomilem serwer python -m http.server 8000
#aby testowac python lab02.03.py localhost 8000

if zad6toggle:
	if len(sys.argv) > 2:
		server_address = sys.argv[1]
		port = sys.argv[2]
		
		try:
			port_number = int(port)
			
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(3)
			
			result = sock.connect_ex((server_address, port_number))
			
			if result == 0:
				print(f"Udało się nawiązać połączenie z {server_address}:{port_number}")
			else:
				print(f"Nie udało się nawiązać połączenia z {server_address}:{port_number}")
			
			sock.close()
			
		except ValueError:
			print("Numer portu musi być liczbą")
		except socket.gaierror:
			print(f"Nie można rozwiązać adresu: {server_address}")
		except Exception as e:
			print(f"Błąd: {e}")
	else:
		print("brak argumentów: podaj adres serwera i numer portu")

#zad7
#python lab02.03.py localhost
if zad7toggle:
	if len(sys.argv) > 1:
		server_address = sys.argv[1]
		
		common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
		all_ports = range(1, 65536)
		print(f"Skanowanie portów dla {server_address}...")
		open_ports = []
		
		#for port in common_ports:
		for port in all_ports:
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(1)
				
				result = sock.connect_ex((server_address, port))
				
				if result == 0:
					open_ports.append(port)
					print(f"Port {port} - OTWARTY")
				
				sock.close()
				
			except socket.gaierror:
				print(f"Nie można rozwiązać adresu: {server_address}")
				break
			except Exception as e:
				print(f"Błąd dla portu {port}: {e}")
		
		print(f"\nZnaleziono {len(open_ports)} otwartych portów: {open_ports}")
	else:
		print("brak argumentu: podaj adres serwera")

