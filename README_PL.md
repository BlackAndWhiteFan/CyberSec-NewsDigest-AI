[English](README.md) | [Polski](README_PL.md)

_**CyberSec NewsDigest AI**_

Zautomatyzowany, codzienny przegląd wiadomości z obszaru cyberbezpieczeństwa, tworzony z wykorzystaniem Pythona, GitHub Actions, kanałów RSS i przetwarzania treści przez AI.

**Cel projektu**

CyberSec NewsDigest AI ma za zadanie pobierać wiadomości o cyberbezpieczeństwie z wybranych kanałów RSS, identyfikować istotne artykuły, generować ich krótkie podsumowania i dostarczać codzienny przegląd na Discordzie.

Projekt ma działać przy budżecie operacyjnym 0 PLN, w miarę możliwości korzystając z bezpłatnych planów usług.

Aktualny stan projektu

Etap 1 — pobieranie RSS i kontrola jakości: zakończony.

**Obecna implementacja:**

Pobiera wpisy RSS lub Atom z sześciu skonfigurowanych źródeł wiadomości o cyberbezpieczeństwie.

Odczytuje tytuły artykułów, linki i opisy.

Pomija wpisy bez tytułów lub z nieprawidłowymi adresami URL.

Wykrywa powtarzające się linki w obrębie jednego uruchomienia.

Kontynuuje pracę, gdy pobranie pojedynczego kanału RSS się nie powiedzie.

Wyświetla statystyki pobierania i przetwarzania wpisów.

Obecny workflow GitHub Actions uruchamia testy jednostkowe, a następnie wykonuje skrypt pobierający wiadomości RSS.

Ostatni zweryfikowany przebieg:

Wpisy znalezione w kanałach RSS: 150

Unikalne linki do artykułów: 150

Duplikaty linków: 0

Pominięte nieprawidłowe wpisy: 0

Nieudane kanały RSS: 0

Testy jednostkowe: 12 zaliczonych

Powyższe liczby dotyczą jednego udanego uruchomienia i mogą się zmieniać. Brak identycznych linków nie gwarantuje, że różne adresy URL nie prowadzą do informacji o tym samym wydarzeniu.

**Planowane funkcje**

Trwała historia przetworzonych artykułów pomiędzy uruchomieniami workflow.

Filtrowanie i ustalanie priorytetów wiadomości o cyberbezpieczeństwie.

Tworzenie krótkich podsumowań artykułów z wykorzystaniem AI.

Dostarczanie codziennego przeglądu wiadomości na Discorda.

Automatyczne uruchamianie o ustalonej porze każdego dnia.

Dokumentacja operacyjna i instrukcje rozwiązywania problemów.

Funkcje planowane nie są uznawane za wdrożone, dopóki nie zostaną zaimplementowane i zweryfikowane.

**Architektura**

Docelowy przepływ przetwarzania: 

Pobranie artykułów ze skonfigurowanych kanałów RSS.

Walidacja danych i wykrywanie duplikatów.

Porównanie artykułów z trwałą historią przetwarzania.

Wybór i ustalenie priorytetów istotnych wiadomości.

Wygenerowanie krótkich podsumowań przy użyciu usługi AI.

Sformatowanie i dostarczenie przeglądu wiadomości na Discorda.

Zapis wyników przetwarzania i utrzymywanie historii operacyjnej.

GitHub Actions odpowiada za wykonywanie workflow, a Python implementuje logikę przetwarzania.

**Struktura repozytorium**

.github/workflows/daily-digest.yml — workflow GitHub Actions.

src/main.py — główny skrypt pobierania i przetwarzania RSS.

src/deduplication.py — logika deduplikacji artykułów.

src/rss_helpers.py — funkcje pomocnicze do walidacji URL-i i wykrywania duplikatów linków.

src/test_deduplication.py — testy jednostkowe deduplikacji.

src/test_url_validation.py — testy walidacji URL-i i wykrywania duplikatów.

**Konfiguracja i sekrety**

Konfiguracja działania i dane uwierzytelniające będą przechowywane w sekretach GitHub Actions lub w innych odpowiednich, bezpiecznych mechanizmach konfiguracji, gdy będą potrzebne.

Nigdy nie zapisuj w repozytorium kluczy API, adresów webhooków Discorda, haseł ani innych danych uwierzytelniających.

**Rozwój i testowanie**

Testy jednostkowe można uruchomić lokalnie z katalogu głównego repozytorium:

python -m unittest discover -s src -p "test_*.py"

Workflow GitHub Actions również uruchamia testy przed wykonaniem skryptu pobierającego wiadomości RSS.

**Dokumentacja
**
Dokumentacja projektu będzie utrzymywana razem z kodem w tym repozytorium. Zmiany techniczne powinny być odzwierciedlane w odpowiednich dokumentach w miarę rozwoju implementacji.
