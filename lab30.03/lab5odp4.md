Przeprowadzilem kilka testow porownujacych czas przesylu danych za pomoca TCP i UDP na localhost.
W kazdym teście wysylalem 1000 pakietow i mierzyłem czas przesylu. 
Wyniki byly nastepujace:

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.235490s
[Zadanie 4] UDP czas: 0.203925s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.240228s
[Zadanie 4] UDP czas: 0.203478s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.214543s
[Zadanie 4] UDP czas: 0.207141s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.237421s
[Zadanie 4] UDP czas: 0.257028s
[Zadanie 4] Krótszy czas miał TCP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.217906s
[Zadanie 4] UDP czas: 0.253305s
[Zadanie 4] Krótszy czas miał TCP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 1000
[Zadanie 4] TCP czas: 0.211880s
[Zadanie 4] UDP czas: 0.206703s
[Zadanie 4] Krótszy czas miało UDP.


dla 10000:
[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 10000
[Zadanie 4] TCP czas: 2.345913s
[Zadanie 4] UDP czas: 2.234596s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 10000
[Zadanie 4] TCP czas: 2.278184s
[Zadanie 4] UDP czas: 2.038088s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 10000
[Zadanie 4] TCP czas: 2.273746s
[Zadanie 4] UDP czas: 2.252510s
[Zadanie 4] Krótszy czas miało UDP.

[Zadanie 4] Porównanie czasu TCP i UDP na localhost.
[Zadanie 4] Host/port: 127.0.0.1:5000
[Zadanie 4] Liczba pakietów: 10000
[Zadanie 4] TCP czas: 2.385076s
[Zadanie 4] UDP czas: 2.161800s
[Zadanie 4] Krótszy czas miało UDP.


Jak widac w większości testów UDP był szybszy, ale zdarzały się też przypadki, gdzie TCP miał krótszy czas.
Wyniki te pokazują, że w warunkach lokalnych UDP może być szybszy niż TCP.
Jednak test nie jest dokonca miarodajny ze wzgledu na niewielkie czasy.
Spwolniene w przypatku UDP moglbym sam python, czego nie jestem w stanie zweryfikowac.
Natomiast w przypadku duzej liczby pakietów (10000) różnica czasów była bardziej zauważalna, a UDP konsekwentnie osiągał krótszy czas niż TCP.
Wnioskujac z mojej wiedzy zeby pokazac kiedy TCP dominuje nad udp musialbym napisac serwer z ktorym sie lacze
potem wysylac wiadomosci, ze wzgledu na juz ustawione polaczenie TCP, powinno byc szybsze


Wady/Zalety UDP:
Zalety:
 - brak zestawiania połączenia, więc mniejszy narzut i zwykle krótszy czas startu,
 - prostszy protokół, bez potwierdzeń i retransmisji,
 - nadaje się do transmisji czasu rzeczywistego, gdzie ważniejsza jest szybkość niż pełna niezawodność.

Wady:
 - brak gwarancji dostarczenia pakietu,
 - brak kolejności pakietów,
 - brak kontroli przeciążenia i retransmisji po stronie protokołu.

Wady/Zalety TCP:
Zalety:
 - gwarantuje dostarczenie danych,
 - pilnuje kolejności pakietów,
 - automatycznie retransmituje utracone dane,
 - jest bardziej niezawodny przy przesyłaniu plików i danych wymagających pełnej poprawności.

Wady:
 - większy narzut, bo wymaga zestawienia połączenia,
 - zwykle działa wolniej niż UDP przy prostych, krótkich transmisjach,
 - bardziej złożony mechanizm kontroli i potwierdzeń.