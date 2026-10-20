[English](README.md) | [Polski](README_PL.md)

_# CyberSec NewsDigest AI_

Zautomatyzowany przegląd wiadomości z obszaru cyberbezpieczeństwa, tworzony z wykorzystaniem Pythona, GitHub Actions, kanałów RSS oraz planowanego przetwarzania treści z wykorzystaniem AI.

## Cel projektu

CyberSec NewsDigest AI ma za zadanie pobierać wiadomości o cyberbezpieczeństwie z wybranych kanałów RSS, identyfikować istotne artykuły, generować ich krótkie podsumowania i dostarczać codzienny przegląd na Discordzie.

Projekt ma działać przy budżecie operacyjnym 0 PLN, w miarę możliwości korzystając z bezpłatnych planów usług.

## Aktualny stan projektu

**Etap 1 — pobieranie RSS, walidacja adresów URL i kontrola jakości: zakończony.**

**Etap 2 — trwała historia artykułów i filtrowanie uwzględniające publikację: zaimplementowane; workflow i testy jednostkowe zweryfikowane.**

**Etap 3 — kategoryzacja artykułów i ustalanie priorytetów na podstawie reguł: zaimplementowane i zweryfikowane w pełnym uruchomieniu workflow.**

**Etap 4 — dostarczanie prasówki na Discorda (bez AI): zaimplementowane i zweryfikowane w uruchomieniach workflow.**

**Etap 5 — jakość selekcji (polskie słowa kluczowe, próg trafności, limity źródeł, filtr promocji): zaimplementowane i zweryfikowane w uruchomieniach workflow.**

**Etap 6 — automatyczny harmonogram (próby o 6:17, 7:17, 8:17 i 9:17 czasu polskiego, od poniedziałku do soboty, jedna prasówka dziennie): skonfigurowany; GitHub uruchamia harmonogramy nieregularnie, dlatego są cztery próby i strażnik; blokada kolejnych prób oczekuje na potwierdzenie na `main`.**

**Etap 7 — miesięczne archiwum dostarczonych artykułów: zaimplementowane i zweryfikowane w uruchomieniu, które dostarczyło artykuł.**

**Etap 8 — wykrywanie tego samego wydarzenia opisanego przez różne serwisy: zaimplementowane; zweryfikowane testami i symulacjami, grupowanie na żywo jeszcze nie wystąpiło.**

**Etap 9 — miesięczne top 10 wydarzeń na osobnym kanale Discorda: zaimplementowane i zweryfikowane w ręcznym uruchomieniu, które dostarczyło zestawienie na kanał; pierwsze automatyczne uruchomienie zaplanowano na 1.11.2026.**

**Etap 10 — streszczenia AI po polsku z obowiązkowym słowniczkiem zgodnym z glosariuszem CyberSec Mozaika: zaimplementowane i zweryfikowane w uruchomieniu, które dostarczyło prasówkę ze streszczeniami.**

**Etap 11 — kanał testowy dla uruchomień z gałęzi (bez zapisu w historii i archiwum): zaimplementowane i zweryfikowane w uruchomieniu, które dostarczyło prasówkę na kanał testowy.**

**Etap 12 — tygodniowe top 5 i jednorazowa wysyłka zestawień (cztery próby, znacznik `data/last_top.json`) ze streszczeniami AI: zaimplementowane; zestawienie miesięczne zweryfikowane na kanale testowym, pierwsze tygodniowe oczekuje na potwierdzenie po scaleniu.**

### Obecna implementacja

- Pobiera wpisy RSS lub Atom z sześciu skonfigurowanych źródeł wiadomości o cyberbezpieczeństwie.
- Odczytuje tytuły artykułów, linki i opisy, dekodując encje HTML pozostawione w tytułach przez niektóre kanały.
- Pomija wpisy bez tytułów lub z nieprawidłowymi adresami URL.
- Wykrywa powtarzające się linki w obrębie jednego uruchomienia i śledzi źródła, w których pojawia się dany artykuł.
- Prowadzi trwałą historię artykułów w pliku `data/seen_articles.json`, rozdzielając linki wcześniej zauważone od linków opublikowanych.
- Odrzuca artykuły, których linki znajdują się już na liście `published_links`, zamiast wykluczać wszystkie wcześniej zauważone artykuły.
- Kategoryzuje artykuły jako najważniejsze wiadomości, podatności i wiadomości związane z Polską na podstawie angielskich i polskich słów kluczowych zapisanych jako rdzenie wyrazów; polskie rdzenie sprawdzono z formami fleksyjnymi wygenerowanymi przez analizator morfologiczny Morfeusz 2.
- Przydziela punkty priorytetu (najważniejsze +3, podatności +2, Polska +1) i odejmuje 2 punkty tytułom w kontekście wydarzeń, raportów lub poradników (np. konferencje, eksperci, poradniki, odporność, kary regulacyjne).
- Wyklucza tytuły promocyjne (webinary, bezpłatne szkolenia, e-booki, rabaty, treści sponsorowane, wykłady, zapisy).
- Wybiera maksymalnie 20 artykułów z wynikiem co najmniej 2, więc artykuły związane z Polską bez sygnału bezpieczeństwa nie są wybierane, a prasówka może liczyć mniej niż 20 pozycji.
- Ogranicza każde źródło do 4 artykułów (Niebezpiecznik: 2); limity są ustawiane w `src/article_selection.py`.
- Wysyła prasówkę na kanał Discorda przez webhook: artykuły pogrupowane według najważniejszej kategorii, z klikalnymi tytułami i domeną źródła, podzielone na wiadomości mieszczące się w limicie długości Discorda.
- Dopisuje linki do `published_links` dopiero po udanej wysyłce; błąd wysyłki kończy uruchomienie błędem, więc workflow zostaje oznaczony jako nieudany.
- Archiwizuje każdy dostarczony artykuł (data, tytuł, link, źródło, kategorie, punkty) w miesięcznym pliku `data/archive/RRRR-MM.json`. Błąd archiwum jest zapisywany w logu i kończy uruchomienie błędem, ale historia artykułów zostaje zapisana, więc dostarczone linki nie są wysyłane ponownie.
- Zapisuje historię artykułów i archiwum także wtedy, gdy krok prasówki zakończy się błędem, chyba że uruchomienie zostanie anulowane.
- Łączy artykuły z różnych serwisów o tym samym wydarzeniu w jedną pozycję z dopiskiem „także:” i linkami do pozostałych źródeł, a artykuły o wydarzeniach dostarczonych w ciągu ostatnich 3 dni pokazuje w osobnej sekcji „🔁 Ciąg dalszy”.
- Pierwszego dnia miesiąca wysyła na osobny kanał Discorda 10 najważniejszych wydarzeń poprzedniego miesiąca, a w poniedziałek na kanał `#top-tygodnia` 5 najważniejszych wydarzeń poprzedniego tygodnia (według liczby artykułów, następnie serwisów i punktacji), ze streszczeniami AI. Każde zestawienie ma cztery próby startu i idzie tylko raz (znacznik `data/last_top.json`); zestawienie tygodniowe wymaga sekretu `DISCORD_WEEKLY_WEBHOOK_URL`.
- Dodaje do każdego artykułu streszczenie po polsku (do 2 zdań) przygotowane przez AI (Groq: `gpt-oss-120b`, zapasowo `qwen3.8-27b`) z pełnego tekstu z kanału albo opisu RSS. Terminy muszą być zgodne ze słowniczkiem `data/glosariusz_mirror.csv` (mirror glosariusza CyberSec Mozaika): streszczenie niezgodne wraca do AI do poprawki, a potem jest odrzucane; objaśnienia w nawiasach dopisuje kod przy pierwszym wystąpieniu terminu w prasówce, tylko dla 7 wybranych terminów (np. ransomware, exploit, MFA, podwyższenie (eskalacja) uprawnień). Bez sekretu `GROQ_API_KEY` prasówka idzie bez streszczeń.
- Wymaga sekretu repozytorium `DISCORD_WEBHOOK_URL` (adres webhooka kanału); bez niego wysyłka jest pomijana bez błędu. Zestawienie miesięczne wymaga sekretu `DISCORD_MONTHLY_WEBHOOK_URL`. Uruchomienia z gałęzi innych niż `main` idą wyłącznie na kanał testowy (sekret `DISCORD_TEST_WEBHOOK_URL`) z nagłówkiem „🧪 TEST” i niczego nie zapisują; bez tego sekretu nic nie wysyłają.
- Kontynuuje pracę, gdy pobranie pojedynczego kanału RSS się nie powiedzie.
- Wyświetla informacje diagnostyczne o pobranych, pominiętych i przetwarzanych wpisach oraz wynikach selekcji artykułów.
- Uruchamia testy jednostkowe przed wykonaniem skryptu pobierającego wiadomości RSS.
- Wykorzystuje GitHub Actions do zatwierdzania i wysyłania zmian w historii artykułów, gdy zawartość tego pliku ulegnie zmianie.

Workflow próbuje uruchomić się automatycznie o 6:17, 7:17, 8:17 i 9:17 czasu polskiego (`Europe/Warsaw`) od poniedziałku do soboty; pierwsza zakończona próba wysyła prasówkę, a kolejne tego dnia kończą się bez wysyłki (znacznik `data/last_digest.json`). Można go też uruchomić ręcznie w GitHub Actions – uruchomienie ręczne nigdy nie jest blokowane i również „zalicza dzień”. GitHub nie gwarantuje startu zaplanowanych uruchomień (wiele z nich pomija lub opóźnia), więc prasówka może przyjść później albo trzeba ją uruchomić ręcznie. Grupa współbieżności zapobiega nakładaniu się dwóch uruchomień.

### Ostatnie zweryfikowane wyniki

Ostatnie zweryfikowane uruchomienia (v13, 17.10.2026) zakończyły się powodzeniem:

- Testy jednostkowe: **69 zaliczonych**.
- Pierwsze uruchomienie: 20 artykułów wybranych spośród 105, w tym 13 ze źródeł polskich; żadne źródło nie przekroczyło limitu.
- Drugie uruchomienie: 8 artykułów wybranych spośród 85; 1 artykuł odrzucono jako promocję, a 76 znalazło się poniżej progu trafności, więc prasówka nie została uzupełniona do 20 pozycji.
- Lista `published_links` zawiera po tych uruchomieniach 88 linków.

Są to wyniki konkretnych uruchomień i mogą się zmieniać. Wyniki weryfikacji każdej zmiany są zapisywane w pliku [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

Deduplikacja oparta na linkach nie gwarantuje, że różne adresy URL nie prowadzą do informacji o tym samym wydarzeniu.

### Ważne ograniczenia historii i selekcji

Lista `seen_links` rejestruje linki napotkane podczas pobierania RSS. Nie oznacza to, że artykuły zostały opublikowane.

Lista `published_links` przechowuje linki do artykułów pomyślnie dostarczonych na Discord. Artykuły, których linki znajdują się już na tej liście, są wykluczane z kolejnych selekcji.

Obecna implementacja nie przechowuje pełnej treści artykułów w osobnej kolejce oczekujących. W związku z tym artykuł kwalifikujący się do selekcji, który zniknie z kanałów RSS, zanim zostanie wybrany, może nie być już dostępny w kolejnym digescie.

Punkty priorytetu są wskaźnikami opartymi na słowach kluczowych. Nie stanowią oceny AI ani gwarancji, że artykuł jest istotny z redakcyjnego punktu widzenia.

## Planowane funkcje

- Dokumentacja operacyjna i instrukcje rozwiązywania problemów.
- Weryfikacja pełnego przepływu od początku do końca.

Planowane funkcje nie są uznawane za wdrożone, dopóki nie zostaną opracowane i zweryfikowane.

