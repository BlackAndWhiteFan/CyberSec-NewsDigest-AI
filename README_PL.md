[English](README.md) | [Polski](README_PL.md)

_# CyberSec NewsDigest AI_

Zautomatyzowany przegląd wiadomości z obszaru cyberbezpieczeństwa, tworzony z wykorzystaniem Pythona, GitHub Actions, kanałów RSS oraz planowanego przetwarzania treści z wykorzystaniem AI.

## Cel projektu

CyberSec NewsDigest AI ma za zadanie pobierać wiadomości o cyberbezpieczeństwie z wybranych kanałów RSS, identyfikować istotne artykuły, generować ich krótkie podsumowania i dostarczać codzienny przegląd na Discordzie.

Projekt ma działać przy budżecie operacyjnym 0 PLN, w miarę możliwości korzystając z bezpłatnych planów usług.

## Aktualny stan projektu

**Etap 1 — pobieranie RSS, walidacja adresów URL i kontrola jakości: zakończony.**

**Etap 2 — trwała historia artykułów i filtrowanie uwzględniające publikację: zaimplementowane; workflow i testy jednostkowe zweryfikowane.**

**Etap 3 — kategoryzacja artykułów i ustalanie priorytetów na podstawie reguł: zaimplementowane; pełne działanie selekcji podczas uruchomienia wymaga jeszcze potwierdzenia.**

Generowanie podsumowań przez AI, dostarczanie wiadomości na Discorda i automatyczny harmonogram dzienny nie zostały jeszcze wdrożone.

### Obecna implementacja

- Pobiera wpisy RSS lub Atom z sześciu skonfigurowanych źródeł wiadomości o cyberbezpieczeństwie.
- Odczytuje tytuły artykułów, linki i opisy.
- Pomija wpisy bez tytułów lub z nieprawidłowymi adresami URL.
- Wykrywa powtarzające się linki w obrębie jednego uruchomienia i śledzi źródła, w których pojawia się dany artykuł.
- Prowadzi trwałą historię artykułów w pliku `data/seen_articles.json`, rozdzielając linki wcześniej zauważone od linków opublikowanych.
- Odrzuca artykuły, których linki znajdują się już na liście `published_links`, zamiast wykluczać wszystkie wcześniej zauważone artykuły.
- Kategoryzuje artykuły na podstawie słów kluczowych, przypisując je do kategorii najważniejszych wiadomości, podatności i wiadomości związanych z Polską.
- Przydziela wstępne punkty priorytetu na podstawie dopasowanych kategorii.
- Wybiera maksymalnie 20 artykułów o najwyższym priorytecie spośród artykułów kwalifikujących się do selekcji.
- Kontynuuje pracę, gdy pobranie pojedynczego kanału RSS się nie powiedzie.
- Wyświetla informacje diagnostyczne o pobranych, pominiętych i przetwarzanych wpisach oraz wynikach selekcji artykułów.
- Uruchamia testy jednostkowe przed wykonaniem skryptu pobierającego wiadomości RSS.
- Wykorzystuje GitHub Actions do zatwierdzania i wysyłania zmian w historii artykułów, gdy zawartość tego pliku ulegnie zmianie.

Obecny workflow można uruchomić ręcznie w GitHub Actions. Codzienny harmonogram nie został jeszcze skonfigurowany.

### Ostatnie zweryfikowane wyniki

Ostatnie zgłoszone uruchomienie testów jednostkowych zakończyło się powodzeniem:

- Testy jednostkowe: **30 zaliczonych**.
- Trwała historia zawiera 150 zapisanych linków do artykułów.
- Lista `published_links` jest obecnie pusta, ponieważ publikowanie na Discordzie nie zostało jeszcze wdrożone.

Aktualny kod zawiera filtrowanie uwzględniające status publikacji oraz regułową selekcję artykułów. Jednak w dotychczas udostępnionych logach z ostatniego uruchomienia nie było oczekiwanego podsumowania RSS ani statystyk selekcji. Pełne działanie zaktualizowanego przepływu podczas uruchomienia wymaga więc jeszcze potwierdzenia.

We wcześniejszych testach pobierania RSS uzyskano 150 wpisów ze skonfigurowanych kanałów. Są to wyniki konkretnych uruchomień i mogą się zmieniać.

Deduplikacja oparta na linkach nie gwarantuje, że różne adresy URL nie prowadzą do informacji o tym samym wydarzeniu.

### Ważne ograniczenia historii i selekcji

Lista `seen_links` rejestruje linki napotkane podczas pobierania RSS. Nie oznacza to, że artykuły zostały opublikowane.

Lista `published_links` ma przechowywać linki do artykułów pomyślnie dostarczonych w ramach digestu. Artykuły, których linki znajdują się już na tej liście, są wykluczane z kolejnych selekcji.

Obecna implementacja nie przechowuje pełnej treści artykułów w osobnej kolejce oczekujących. W związku z tym artykuł kwalifikujący się do selekcji, który zniknie z kanałów RSS, zanim zostanie wybrany, może nie być już dostępny w kolejnym digescie.

Punkty priorytetu są wstępnymi wskaźnikami opartymi na słowach kluczowych. Nie stanowią oceny AI ani gwarancji, że artykuł jest istotny z redakcyjnego punktu widzenia.

## Planowane funkcje

- Generowanie krótkich podsumowań wybranych artykułów z wykorzystaniem AI.
- Formatowanie i dostarczanie codziennego przeglądu wiadomości na Discorda.
- Zapisywanie linków do pomyślnie opublikowanych artykułów
