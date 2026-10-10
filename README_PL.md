[English](README.md) | [Polski](README_PL.md)


# _CyberSec NewsDigest AI_

Zautomatyzowany, codzienny przegląd wiadomości z obszaru cyberbezpieczeństwa, tworzony z wykorzystaniem Pythona, GitHub Actions, kanałów RSS i przetwarzania treści przez AI.

## Cel projektu

CyberSec NewsDigest AI ma za zadanie pobierać wiadomości o cyberbezpieczeństwie z wybranych kanałów RSS, identyfikować istotne artykuły, generować ich krótkie podsumowania i dostarczać codzienny przegląd na Discordzie.

Projekt ma działać przy budżecie operacyjnym 0 PLN, w miarę możliwości korzystając z bezpłatnych planów usług.

## Aktualny stan projektu

**Etap 1 — pobieranie RSS i kontrola jakości: zakończony.**

**Etap 2 — trwała historia artykułów i deduplikacja między uruchomieniami: zaimplementowany i zweryfikowany.**

### Obecna implementacja

- Pobiera wpisy RSS lub Atom z sześciu skonfigurowanych źródeł wiadomości o cyberbezpieczeństwie.
- Odczytuje tytuły artykułów, linki i opisy.
- Pomija wpisy bez tytułów lub z nieprawidłowymi adresami URL.
- Wykrywa powtarzające się linki w obrębie jednego uruchomienia.
- Pomija artykuły, których linki znajdują się już w trwałej historii.
- Zapisuje linki do nowo przetworzonych artykułów w pliku `data/seen_articles.json`.
- Kontynuuje pracę, gdy pobranie pojedynczego kanału RSS się nie powiedzie.
- Wyświetla statystyki pobierania i przetwarzania wpisów.
- Uruchamia testy jednostkowe przed wykonaniem skryptu pobierającego wiadomości RSS.
- Wykorzystuje GitHub Actions do zatwierdzania i wysyłania zmian w historii artykułów, gdy zawartość tego pliku ulegnie zmianie.

Obecny workflow można uruchomić ręcznie w GitHub Actions. Codzienny harmonogram nie został jeszcze skonfigurowany.

### Ostatnie zweryfikowane wyniki

Test pobierania RSS zwrócił 150 wpisów ze skonfigurowanych kanałów, bez nieprawidłowych wpisów i nieudanych pobrań. Kolejne uruchomienie potwierdziło, że wszystkie 150 zapisanych linków zostało wczytanych z trwałej historii i rozpoznanych jako wcześniej widziane.

- Początkowe pobranie: 150 wpisów i 150 unikalnych linków do artykułów.
- Początkowa liczba duplikatów: 0.
- Pominięte nieprawidłowe wpisy: 0.
- Nieudane kanały RSS: 0.
- Kolejne uruchomienie: rozpoznano 150 wcześniej widzianych artykułów.
- Testy jednostkowe: 18 zaliczonych.

Podane liczby dotyczą zweryfikowanych uruchomień i mogą się zmieniać. Deduplikacja oparta na linkach nie gwarantuje, że różne adresy URL nie prowadzą do informacji o tym samym wydarzeniu.

## Planowane funkcje

- Filtrowanie i ustalanie priorytetów wiadomości o cyberbezpieczeństwie.
- Tworzenie krótkich podsumowań artykułów z wykorzystaniem usługi AI.
- Dostarczanie codziennego przeglądu wiadomości na Discorda.
- Automatyczne uruchamianie o ustalonej porze każdego dnia.
- Dokumentacja operacyjna i instrukcje rozwiązywania problemów.

Funkcje planowane nie są uznawane za wdrożone, dopóki nie zostaną zaimplementowane i zweryfikowane.

## Architektura

Docelowy przepływ przetwarzania:

1. Pobranie artykułów ze skonfigurowanych kanałów RSS.
2. Walidacja danych i wykrywanie duplikatów.
3. Porównanie linków do artykułów z trwałą historią przetwarzania.
4. Wybór istotnych wiadomości i ustalenie ich priorytetów.
5. Wygenerowanie krótkich podsumowań przy użyciu usługi AI.
6. Sformatowanie i dostarczenie przeglądu wiadomości na Discorda.
7. Zapis wyników przetwarzania i utrzymywanie historii artykułów.

GitHub Actions odpowiada za wykonywanie workflow, a Python implementuje logikę przetwarzania. Obecna implementacja obejmuje pobieranie RSS, walidację, deduplikację i trwałą historię linków.

## Struktura repozytorium

- `.github/workflows/daily-digest.yml` — workflow GitHub Actions.
- `data/seen_articles.json` — trwała historia wcześniej widzianych linków do artykułów.
- `src/main.py` — główny skrypt pobierania i przetwarzania RSS.
- `src/deduplication.py` — logika deduplikacji artykułów.
- `src/rss_helpers.py` — funkcje pomocnicze do walidacji URL-i i wykrywania duplikatów linków.
- `src/article_history.py` — wczytywanie i zapisywanie trwałej historii artykułów.
- `src/test_deduplication.py` — testy jednostkowe deduplikacji.
- `src/test_url_validation.py` — testy walidacji URL-i

**Dokumentacja projektu będzie utrzymywana razem z kodem w tym repozytorium. Zmiany techniczne powinny być odzwierciedlane w odpowiednich dokumentach w miarę rozwoju implementacji.
