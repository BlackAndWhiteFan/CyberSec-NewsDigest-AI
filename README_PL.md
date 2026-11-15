[English](README.md) | [Polski](README_PL.md)

# CyberSec NewsDigest AI

Automatyczna codzienna prasówka o cyberbezpieczeństwie po polsku, tworzona w Pythonie i GitHub Actions z kanałów RSS i streszczeń AI, dostarczana na Discorda.

## Cel projektu

CyberSec NewsDigest AI pobiera wiadomości o cyberbezpieczeństwie z polskich i angielskich kanałów RSS, wybiera istotne artykuły, łączy doniesienia o tym samym wydarzeniu, pisze do każdego artykułu konkretne streszczenie po polsku i dostarcza codzienną prasówkę na Discorda, a do tego tygodniowe top 5 i miesięczne top 10.

Projekt działa przy budżecie 0 PLN, wyłącznie na bezpłatnych planach usług (GitHub Actions, Groq, Google Gemini bez płatności, Mistral (plan darmowy), publiczne API LanguageTool, cron-job.org).

## Aktualny stan projektu

Prasówka działa produkcyjnie od października 2026 (wersja v36). Każda zmiana jest opisana razem z weryfikacją w pliku [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

| Etap | Zakres | Stan |
|---|---|---|
| 1 | Pobieranie RSS, walidacja adresów URL, kontrola jakości | zakończony (v1–v10) |
| 2 | Trwała historia artykułów, filtrowanie opublikowanych linków | zakończony i zweryfikowany |
| 3 | Kategoryzacja i punktacja na podstawie reguł | zakończony i zweryfikowany |
| 4 | Dostarczanie prasówki na Discorda | zakończony i zweryfikowany |
| 5 | Jakość selekcji: polskie słowa kluczowe, próg trafności, limity źródeł, filtr promocji; 11 źródeł i filtr wieku 3 dni (v26) | zakończony i zweryfikowany |
| 6 | Automatyczne uruchamianie: zewnętrzny budzik cron-job.org, harmonogram GitHuba jako zapas, jedna prasówka dziennie (v14, v19, v24) | zakończony; pierwsza prasówka z budzika potwierdzona 23.10.2026 |
| 7 | Miesięczne archiwum dostarczonych artykułów (v15) | zakończony i zweryfikowany |
| 8 | Łączenie artykułów o tym samym wydarzeniu i sekcja „🔁 Ciąg dalszy” (v16, v26, v29, v31) | zakończony; łączenie widoczne w prasówkach na żywo |
| 9 | Miesięczne top 10 na osobnym kanale (v17) | zakończony; zweryfikowany w uruchomieniach ręcznych, pierwsze automatyczne 1.11.2026 |
| 10 | Streszczenia AI po polsku z obowiązkowym słowniczkiem z CyberSec Mozaika (v18, v21, v25) | zakończony i zweryfikowany |
| 11 | Kanał testowy dla uruchomień z gałęzi (v20) | zakończony i zweryfikowany |
| 12 | Tygodniowe top 5 i jednorazowa wysyłka zestawień (v22, v23) | zakończony; pierwszy podgląd na żywo dotarł na `#top-tygodnia` 21.10.2026, pierwsze automatyczne 26.10.2026 |
| 13 | Pełna treść ze strony artykułu i odmiana terminów (v27) | zakończony i zweryfikowany |
| 14 | Znacznik 🔥 dla luk z katalogu CISA KEV (v28) | zakończony i zweryfikowany |
| 15 | Jakość językowa: lista stylu, kontrola językowa, korekta przez Google Gemini z podpowiedziami LanguageTool (v29, v30) | zakończony i zweryfikowany |
| 16 | „Weekendowa lektura” rozbierana na linki, łączenie po nazwach firm, alarm o błędzie workflow (v31) | zakończony i zweryfikowany |
| 17 | Dziennik języka: poprawki streszczeń zapisywane w archiwum (v32) | zakończony; zweryfikowany testami jednostkowymi i prawdziwymi błędami z logów |
| 18 | Jakość streszczeń i zestawień: bez formułek, określenia tylko z pokryciem w artykule, łączenie w zestawieniach po CVE, polscy liderzy, porządek i korekta streszczeń w zestawieniach (v33) | zakończony; zweryfikowany na gałęzi testowej i w symulacji na archiwum |
| 19 | Streszczenia z sensem i łatwe w czytaniu: co – dlaczego ważne – co zrobić, kontekst wcześniejszych doniesień, CISA KEV dla AI, streszczenia wydarzeń w zestawieniach (v34) | zakończony; zweryfikowany na gałęzi testowej (prasówka i top 5) |
| 20 | Jedna luka, jedna pozycja: łączenie po numerach CVE po pobraniu stron i po streszczeniach; korekta językowa tylko przez Gemini; zalecenia tylko konkretne (v35) | zakończony; sprawdzony na prasówkach z 27–28.10.2026 |
| 21 | Miękkie problemy nie tną streszczenia, bez urwanych fragmentów, płynniejsze zdania, bez dopisanego phishingu (v36) | zakończony; sprawdzony na prasówce z 29.10.2026 |
| 22 | Korekta językowa codziennie: porcje po 5 streszczeń, lżejsze modele Gemini, Mistral jako zapas; bez pustych „innych luk” (v37a) | zakończony; zweryfikowany testami jednostkowymi |
| 23 | Zestawienia na tym samym łańcuchu co prasówka: historie wydarzeń w porcjach, Mistral przed Groq (v37b) | zakończony; zweryfikowany testami jednostkowymi |
| 24 | Dane dla mostu do CyberSec Mozaika: hasła w archiwum (`terms`), zapis zestawień w `data/tops/`, test kontraktu danych i miejsca plików, mirror v90, eksporter przeniesiony do `cybersec-most` (v38) | zakończony; zweryfikowany testami jednostkowymi |
| 25 | Straż danych dla mostu: test kontraktu zestawień (`data/tops/`) i listy kalk, pole `proofread` w archiwum (v39) | zakończony; zweryfikowany testami jednostkowymi |
| 26 | Objaśnienia w nawiasach tylko przy „podwyższeniu uprawnień” i „poświadczeniach”: mirror v92 po decyzji autora z mostu (v40) | zakończony; zweryfikowany testami jednostkowymi |
| 27 | Karton Prasówki w repo (`docs/karton.html`) ze strażnikiem wersji (v41) | zakończony; zweryfikowany testami jednostkowymi |
| 28 | Czysta polszczyzna: Morfeusz 2 łapie angielskie słowa bez przekładu i literówki z korekty; Gemini lite na końcu kolejki korekty (v42) | zakończony; zweryfikowany testami jednostkowymi |
| 29 | Słownik kalek: 29 nowych wierszy listy kalk zaakceptowanych przez JW, polskie nazwy miesięcy w datach (v43) | zakończony; zweryfikowany testami jednostkowymi |
| 30 | Bez echa: jedna sprawa, jedna pozycja – łączenie po nazwach firm, wersjach produktów i kwotach w streszczeniach (v44) | zakończony; zweryfikowany testami jednostkowymi |
| 31 | Mniej, a lepiej: najwyżej 10 pozycji w prasówce dziennej, bez tekstów sponsorowanych (v45) | zakończony; zweryfikowany testami jednostkowymi |
| 32 | Szlif: dokument reguł języka w promptach, gramatyka z Morfeuszem 2, uzus branżowy ponad purystyką (v46) | zakończony; zweryfikowany testami jednostkowymi |
| 33 | Osobne sprawy: w zestawieniach nazwa firmy nie łączy wydarzeń z różnymi CVE (v47) | zakończony; zweryfikowany testami jednostkowymi |
| 34 | Wspólne platformy: odmienione nazwy platform („Androida”) nie łączą różnych spraw (v48) | zakończony; zweryfikowany testami jednostkowymi |
| 35 | Hashe: „hash” to uzus branżowy, przy pierwszym wystąpieniu „hashe (skróty haseł)” (v49) | zakończony; zweryfikowany testami jednostkowymi |
| 36 | Jeden wtorek: Patch Tuesday jako jedna pozycja, ciąg dalszy z 7 dni, pozycja bez streszczenia na końcu limitu (v50) | zakończony; zweryfikowany testami jednostkowymi |
| 37 | Bez pustych zdań: o łatce i CVE tylko przy lukach, bez poprawek Microsoftu do własnych aktualizacji (v51) | zakończony; zweryfikowany testami jednostkowymi |

## Obecna implementacja

### Źródła i selekcja

- Pobiera wpisy RSS lub Atom z jedenastu źródeł: polskich (Niebezpiecznik, Sekurak, Zaufana Trzecia Strona, CyberDefence24, CERT Polska, Kapitan Hack) i angielskich (BleepingComputer, The Hacker News, SecurityWeek, The Record, Krebs on Security). Pomija wpisy starsze niż 3 dni. Błąd jednego kanału nie zatrzymuje uruchomienia.
- Odczytuje tytuły, linki i opisy (dekodując encje HTML w tytułach) i pomija wpisy bez tytułu lub z nieprawidłowym adresem URL.
- Prowadzi trwałą historię w pliku `data/seen_articles.json`: `seen_links` (napotkane) i `published_links` (dostarczone). Z kolejnych prasówek wykluczane są tylko linki już dostarczone.
- Kategoryzuje artykuły jako najważniejsze wiadomości, podatności i wiadomości związane z Polską na podstawie angielskich i polskich słów kluczowych zapisanych jako rdzenie (polskie rdzenie sprawdzone z formami wygenerowanymi przez analizator morfologiczny Morfeusz 2).
- Przydziela punkty (najważniejsze +3, podatności +2, Polska +1) i odejmuje 2 punkty tytułom w kontekście wydarzeń, raportów lub poradników (konferencje, eksperci, poradniki, kary regulacyjne).
- Wyklucza tytuły promocyjne (webinary, szkolenia, e-booki, rabaty, treści sponsorowane) i angielskie przeglądy (ThreatsDay, Weekly Recap, In Other News), których tematy trafiają do prasówki osobno.
- Streszcza do 14 kandydatów z wynikiem co najmniej 2, a po połączeniu duplikatów wysyła najwyżej 10 pozycji (v45: wyżej stoją KEV, numery CVE, inne źródła tej samej sprawy i polskie źródła). Każde źródło ma limit 4 artykułów (Niebezpiecznik 2, SecurityWeek i The Record 3); limity są ustawiane w `src/article_selection.py`.
- Rozbiera „Weekendową lekturę” (Zaufana Trzecia Strona) na pojedyncze linki: każdy link do innego serwisu staje się kandydatem do prasówki z komentarzem ZTS jako opisem i przechodzi tę samą punktację. Pytajnik w tytule linku oznacza publicystykę (−2), linki do publikacji badawczych (Unit 42, Securelist, ESET, Mandiant, Microsoft Security Blog, Talos, CERT Polska i inne) dostają +2, a linki do wideo, czatów i mediów społecznościowych są pomijane. Najwyżej 3 takie linki w prasówce, podpisane „via Zaufana Trzecia Strona”.

### Wydarzenia i znaczniki

- Łączy artykuły o tym samym wydarzeniu w jedną pozycję z dopiskiem „także:” i linkami do pozostałych źródeł. Reguły: podobne tytuły; wspólny numer CVE lub nazwa wydarzenia z cyframi (np. PHP2Shell), także w obrębie jednego serwisu; wspólna nazwa firmy lub produktu („Quest Diagnostics”, „Capcom”), gdy teksty artykułów pokazują, że to nazwa. Nazwy platform występujące w wielu różnych historiach (Microsoft, Windows, Chrome, Python…) same nie łączą. Od v35 wybrane artykuły są łączone jeszcze raz po numerach CVE po pobraniu stron artykułów (wiele kanałów daje tylko zajawkę bez numeru CVE) i ponownie po streszczeniach, więc jedna luka to jedna pozycja.
- Artykuły o wydarzeniach dostarczonych w ciągu ostatnich 7 dni (od v50; wcześniej 3) pokazuje w osobnej sekcji „🔁 Ciąg dalszy”, także wtedy, gdy wspólny numer CVE jest dopiero w streszczeniu (przy linkach z lektury także na stronie linku).
- Oznacza 🔥 artykuły o lukach z katalogu CISA KEV (potwierdzone wykorzystywanie w atakach). Znacznik ustawia kod, nie AI: numery CVE z tytułu i początku tekstu artykułu są porównywane z katalogiem pobieranym przy każdym uruchomieniu (z CISA, zapasowo z lustra CISA na GitHubie). Zestawienia sprawdzają zapisane numery CVE jeszcze raz z aktualnym katalogiem. Bez katalogu prasówka idzie bez znaczników.

### Streszczenia AI po polsku

- Każdy artykuł dostaje konkretne streszczenie po polsku (2–3 krótkie zdania, do około 420 znaków; 1 zdanie, gdy materiałem jest tylko krótka zajawka), które pisze Groq `gpt-oss-120b`, a zapasowo `qwen3.8-27b`. Od v34 streszczenie odpowiada na pytania praktyka SOC: co się stało i kogo dotyczy (zwykłymi słowami, bez numerów CVE na początku), dlaczego to ważne (wykorzystywanie w atakach, publiczny exploit, skala, łatka albo jej brak) i co zrobić, jeśli artykuł to podaje. AI dostaje informację, że luka jest w katalogu CISA KEV, a każdy artykuł – najnowsze wcześniejsze doniesienie o tym samym wydarzeniu z archiwum z 14 dni jako kontekst (historia; „co nowego”). Zdania dłuższe niż 25 słów i więcej niż 2 numery CVE wracają do poprawki (miękko: nigdy nie skracają streszczenia); zdanie bez konkretu (liczby, daty, numeru CVE, nazwy), za to ze słownictwem oceniającym („poważne zagrożenie”, „współpracuje z ekspertami”), to ogólnik. „Aktywnie wykorzystywana” i „brak łatki” są dozwolone tylko wtedy, gdy materiał to mówi. Zapytania są rozłożone w czasie (co najmniej 20 s odstępu), a partia, której nie obsłużył żaden model, jest ponawiana raz na końcu.
- Materiał: pełny tekst lub opis z kanału; gdy kanał daje mniej niż 600 znaków, tekst artykułu jest pobierany z jego strony (akapity bez menu, reklam i stopki). Tekst strony jest tylko materiałem dla AI i nigdzie nie jest zapisywany.
- Terminy są zgodne ze słowniczkiem `data/glosariusz_mirror.csv` – mirrorem glosariusza CyberSec Mozaika. Proste formy zakazane poprawia kod bez zapytania do AI („poprawka” → „łatka”, „zdalne wykonanie kodu” → „RCE”); objaśnienia w nawiasach dopisuje kod przy pierwszym wystąpieniu 2 wybranych terminów, w tym samym przypadku co termin („podwyższenia (eskalacji) uprawnień”, „poświadczeń (danych logowania)”; od v40).
- Kontrola jakości (`src/summary_quality.py`): niezgodność ze słowniczkiem, ogólniki („co podkreśla wagę…”, „nie została podana”), względne określenia czasu, nieodmienione terminy po przyimku, liczby i numery CVE spoza materiału, określenia „zero-day” i „natychmiast”, gdy artykuł ich nie używa, formułki bez konkretu („Zaleca się natychmiastową aktualizację.”), streszczenia za długie, po angielsku albo powtarzające tylko tytuł oraz kalki z edytowalnej listy stylu `data/styl_unikaj.csv`. Streszczenie z problemem wraca do AI na jedną poprawkę; jeśli problem zostaje, kod usuwa błędne zdania. Streszczenie jest odrzucane tylko wtedy, gdy nie zostaje w nim żadne poprawne zdanie (albo nadal jest po angielsku).
- Korekta językowa: od v37a w porcjach po 5 streszczeń, z podpowiedziami gramatycznymi z LanguageTool; kolejno Google Gemini (`gemini-3.8-flash`, `gemini-3.5-flash`, potem lżejsze `-flash-lite`), a od drugiej rundy także Mistral (`ministral-14b-2512`, darmowy plan); do trzech rund z przerwą 30 s i 60 s. Bez Groq od v35, bo psuł polszczyznę; gdy wszystkie modele zawiodą, streszczenia zostają bez korekty. Poprawka jest przyjmowana tylko wtedy, gdy zachowuje liczby, numery CVE i długość; każda trafia do logu jako „przed” / „po”.
- Dziennik języka (v32): każda poprawka streszczenia jest zapisywana razem z artykułem w archiwum (pole `language`): formy zakazane ze słowniczka z numerem hasła, kalki z listy stylu, nieodmienione terminy, zamiany zrobione przez kod i zmiany z korekty, każda z wynikiem (poprawiło AI, poprawił kod, forma została, streszczenie odrzucone). Notatki opisują tylko to, co napisało AI: niczego nie zmieniają i nigdy nie zapisują do glosariusza.

### Wysyłka i zestawienia

- Wysyła prasówkę na Discorda przez webhook: artykuły pogrupowane według najważniejszej kategorii, z klikalnymi tytułami, domeną źródła i podpisem „via”, podzielone na wiadomości mieszczące się w limicie długości Discorda.
- Dopisuje linki do `published_links` dopiero po udanej wysyłce i archiwizuje każdy dostarczony artykuł (data, tytuł, link, źródło, kategorie, punkty, streszczenie, numery CVE, KEV, via, notatki językowe) w pliku `data/archive/RRRR-MM.json`. Historia i archiwum są zapisywane także wtedy, gdy krok prasówki zakończy się błędem (chyba że uruchomienie zostanie anulowane).
- W poniedziałek wysyła na `#top-tygodnia` 5 najważniejszych wydarzeń poprzedniego tygodnia, a 1. dnia miesiąca na osobny kanał 10 najważniejszych wydarzeń poprzedniego miesiąca (według liczby artykułów, następnie serwisów i punktacji), ze streszczeniami z archiwum. Każde zestawienie idzie tylko raz (znacznik `data/last_top.json`). Od v33 zestawienia łączą też rekordy ze wspólnym numerem CVE albo nazwą wydarzenia z cyframi w dowolnym tytule (także artykułów powiązanych), pokazują wydarzenie pod najlepszym rekordem (najwyższa punktacja, potem polskie źródło, potem najwięcej powiązanych artykułów), pomijają przeglądy, porządkują streszczenia z archiwum kodem (streszczenie po angielsku albo powtarzające tytuł zastępuje streszczenie kolejnego artykułu) i przepuszczają je przez korektę językową (od v37b ten sam łańcuch co prasówka: Gemini, lite, Mistral); każda zmiana zrobiona przez kod trafia do logu jako „PORZĄDEK”. Od v34 jedno zapytanie na zestawienie pisze krótką historię całego wydarzenia (co się wysypało, jak to szło, co dzieje się teraz i czy eskaluje, jak łatać) z polskich streszczeń wszystkich jego artykułów i tytułów artykułów powiązanych; jest użyte tylko wtedy, gdy przejdzie kontrolę względem tego materiału (log „ZESTAWIENIE AI”).
- Uruchomienia z gałęzi innych niż `main` idą wyłącznie na kanał testowy z nagłówkiem „🧪 TEST” i niczego nie zapisują.
- Gdy workflow prasówki albo zestawienia zakończy się błędem, na kanał testowy przychodzi alarm z linkiem do logu.

### Wyzwalacze

Głównym wyzwalaczem jest zewnętrzny budzik: cron-job.org wywołuje API GitHuba (workflow_dispatch z polem `budzik`) o 6:17 czasu polskiego od poniedziałku do soboty, a zestawienia uruchamia w poniedziałek (tygodniowe) i 1. dnia miesiąca (miesięczne) o 8:17. Używa tokenu fine-grained PAT ograniczonego do tego repozytorium i uprawnienia Actions (Read and write), przechowywanego tylko w cron-job.org; token trzeba odnowić przed wygaśnięciem (po roku). Harmonogram GitHuba zostaje jako zapas (prasówka: próby 6:17–9:17, zestawienia: 8:17–11:17, `Europe/Warsaw`), bo GitHub pomija lub opóźnia wiele zaplanowanych uruchomień. Pierwsze zakończone uruchomienie z budzika albo harmonogramu wysyła prasówkę, a kolejne tego dnia kończą się bez wysyłki (znacznik `data/last_digest.json`). Uruchomienie ręczne (bez zaznaczania pola `budzik`) nigdy nie jest blokowane i również „zalicza dzień”. Grupa współbieżności zapobiega nakładaniu się uruchomień.

## Ostatnie zweryfikowane wyniki

Wersja v35 (28.10.2026):

- Testy jednostkowe: **404 zaliczone** (v36, 29.10.2026: miękkie problemy nie tną streszczenia, bez urwanych fragmentów, płynniejsze zdania, poprawne „z/ze”, bez dopisanego phishingu).
- Na archiwum: Brotli (27.10, trzy pozycje) i Apple CVE-2026-86950 (28.10, dwie pozycje) stają się jedną pozycją; połączenia w całym październiku są trafne. 10 ze 110 październikowych streszczeń miało numery CVE z niełamliwymi łącznikami, których kod nie widział – teraz są rozpoznawane.
- Nowe reguły ogólników oznaczają na 107 streszczeniach tylko prawdziwą watę (bez fałszywych trafień); autopoprawka przyimków („we wtyczce”, „ze wsparciem”) zmienia tylko błędne formy.

Wersja v33 (26.10.2026):

- Testy jednostkowe: **346 zaliczonych**.
- Top 5 za 19–25.10 uruchomiony z gałęzi: PHP2Shell jako jedno wydarzenie (17 artykułów, 7 serwisów) pod polskim tytułem, bez duplikatu, bez połączenia Fortinet/FortiSIEM i bez przeglądów; korekta Gemini poprawiła stare streszczenia.
- Reguły łapią formułki i „nie są znane” w streszczeniach z 26.10; lista stylu złapała sześć kalk w prasówce testowej.

Wersja v32 (25.10.2026):

- Testy jednostkowe: **307 zaliczonych**.
- Notatki językowe sprawdzone na prawdziwych błędach z logów 22–25.10.2026 („rekordy pacjentów”, „AI‑zarządzanego”, „patchują”, „przed exploit”, „eksploatując”, „intruzji”): wszystkie zapisane, z numerami haseł H166 i H153 tam, gdzie słowniczek je ma.

Wersja v31 (25.10.2026):

- Test na gałęzi `v31-lektura`: „Weekendowa lektura” nr 699 rozebrana na 53 części, 3 weszły do prasówki; po poprawkach ranking stawia analizy badawcze (Unit 42, Mandiant) przed publicystyką.
- Archiwum październikowe (70 artykułów): zestawienie łączy Quest Diagnostics, Capcom i Arista VCO bez nowych błędnych połączeń.

Wcześniej: w teście v30 korekta Gemini poprawiła 6 z 6 streszczeń; w teście v28 🔥 dostały 2 z 20 artykułów (katalog 1754 pozycji). Liczby dotyczą konkretnych uruchomień; szczegóły każdej wersji są w changelogu.

## Znane ograniczenia

- Punkty priorytetu są wskaźnikami opartymi na słowach kluczowych, a nie oceną AI istotności redakcyjnej.
- Łączenie wydarzeń działa na regułach i rzadko może połączyć dwie różne historie albo przeoczyć parę; takie przypadki są obserwowane i poprawiane na prawdziwych przykładach.
- AI wciąż może popełnić błąd, którego kontrole nie wykryją, np. fakt obecny w materiale, ale w złym kontekście (rok z tytułu w dacie). Prasówka oznacza streszczenia jako przygotowane przez AI.
- Tytuły artykułów zostają w języku źródła.
- Nie ma kolejki oczekujących artykułów: artykuł, który zniknie z kanału, zanim zostanie wybrany, nie jest już dostępny.
- `seen_links` znaczy „napotkane”, a nie „opublikowane”; z kolejnych prasówek wyklucza tylko `published_links`.

## Plan rozwoju

- **Most do CyberSec Mozaika:** cotygodniowy raport (`bridge_report.py` w prywatnym repo `cybersec-most`) z propozycjami dla pliku-matki: formy łamane, kalki, żywe przykłady, rozbieżności konwencji. Prasówka od v38 dostarcza dane (pole `terms` w archiwum, zestawienia w `data/tops/`) i pilnuje ich kształtu testem kontraktu; raport tylko proponuje, a plik-matka Mozaiki pozostaje jedynym źródłem prawdy.
- Ochrona gałęzi `main`.

- Eksperyment z modelem piszącym: Google Gemini pisze streszczenia dzienne (Groq jako zapas) i dostaje więcej materiału z artykułu; porównanie na zwykłych prasówkach dnia roboczego z obecnym układem.

Planowane funkcje nie są uznawane za wdrożone, dopóki nie zostaną opracowane i zweryfikowane.

## Architektura

1. Pobranie wpisów z kanałów RSS/Atom i pominięcie wpisów starszych niż 3 dni.
2. Walidacja wpisów, usunięcie powtórzonych linków, rozebranie „Weekendowej lektury” na linki.
3. Aktualizacja historii i wykluczenie linków już opublikowanych.
4. Kategoryzacja, punktacja, wykluczenie promocji i przeglądów.
5. Wybór do 14 kandydatów w limitach źródeł (po połączeniu najwyżej 10 pozycji, v45); łączenie artykułów o tym samym wydarzeniu; oznaczenie ciągów dalszych z ostatnich 7 dni (v50).
6. Pobranie stron artykułów, gdy tekst z kanału jest za krótki; oznaczenie luk z CISA KEV.
7. Streszczenia AI, ich kontrola, poprawki i korekta językowa; zapis notatek językowych.
8. Sformatowanie i wysłanie prasówki na Discorda.
9. Zapis opublikowanych linków, archiwum dostarczonych artykułów i znacznika dnia.

Zestawienia tygodniowe i miesięczne czytają archiwum. GitHub Actions uruchamia workflow, a Python realizuje logikę.

## Struktura repozytorium

Workflow (`.github/workflows/`):

- `daily-digest.yml` — codzienna prasówka: pole budzika, zapasowy harmonogram, testy jednostkowe, uruchomienie prasówki, zapis historii i archiwum, alarm o błędzie.
- `weekly-top.yml` — tygodniowe top 5 (poniedziałki).
- `monthly-top.yml` — miesięczne top 10 (1. dzień miesiąca).
- `backfill-summaries.yml` — jednorazowe ręczne uzupełnienie streszczeń w archiwum (podgląd, potem zapis).

Kod (`src/`):

- `main.py` — uruchomienie codziennej prasówki.
- `rss_helpers.py` — walidacja URL, powtórzone linki, porządkowanie tytułów, wiek artykułu.
- `deduplication.py` — deduplikacja i śledzenie źródeł.
- `article_history.py` — trwała historia linków napotkanych i opublikowanych.
- `article_selection.py` — słowa kluczowe, kategorie, punktacja, filtr promocji i przeglądów, limity źródeł, ranking lektury.
- `roundup_parts.py` — rozbieranie „Weekendowej lektury” na linki.
- `event_grouping.py` — łączenie artykułów o tym samym wydarzeniu i ciągi dalsze.
- `article_pages.py` — tekst artykułu ze strony artykułu.
- `kev.py` — znacznik 🔥: katalog CISA KEV i numery CVE.
- `ai_summaries.py` — streszczenia AI (Groq), poprawki i korekta językowa.
- `gemini.py` — Google Gemini do korekty językowej.
- `mistral.py` — Mistral, ostatni zapas korekty językowej (v37a).
- `languagetool.py` — podpowiedzi gramatyczne z LanguageTool.
- `glossary.py` — reguły słowniczka z mirrora: hasła do promptu, formy zakazane, autopoprawki, objaśnienia w nawiasach.
- `summary_quality.py` — kontrola jakości i języka streszczeń, naprawa przez kod.
- `polish_words.py` — kontrola słów Morfeuszem 2: angielskie słowa bez przekładu i słowa wymyślone przez korektę (od v42).
- `language_notes.py` — dziennik języka: poprawki streszczeń jako notatki do archiwum.
- `discord_output.py` — formatowanie prasówki, podział na wiadomości, wysyłka.
- `article_archive.py` — miesięczne archiwum.
- `weekly_top.py`, `monthly_top.py` — zestawienia z archiwum.
- `run_guard.py`, `top_guard.py` — jedna prasówka dziennie, jedno zestawienie na tydzień i miesiąc.
- `test_mode.py` — uruchomienia testowe z gałęzi.
- `backfill_summaries.py` — uzupełnianie streszczeń w archiwum.
- `test_*.py` — testy jednostkowe (bez dostępu do sieci), po jednym pliku na moduł.

Dane i narzędzia:

- `data/seen_articles.json` — historia linków napotkanych i opublikowanych.
- `data/archive/RRRR-MM.json` — miesięczne archiwum dostarczonych artykułów; od v38 z hasłami glosariusza (`terms`), od v39 z modelem korekty językowej (`proofread`, pusty tekst = bez korekty).
- `data/last_digest.json`, `data/last_top.json` — znaczniki ostatniej prasówki i zestawień.
- `data/tops/RRRR-Www.json`, `data/tops/RRRR-MM.json` — wysłane zestawienia tygodniowe i miesięczne z historiami wydarzeń (od v38; materiał dla mostu do CyberSec Mozaika).
- `data/glosariusz_mirror.csv` — mirror glosariusza CyberSec Mozaika (plik-matka v100, 6 kolumn). Eksportuje go prywatne repozytorium mostu `cybersec-most` (od v38; wcześniej `tools/eksport_mirrora.py` w tym repo).
- `data/styl_unikaj.csv` — lista stylu: kalki i anglicyzmy z propozycjami, edytowana ręcznie (`*` = dowolna końcówka).
- `data/reguly_jezyka.md` — Reguły języka Prasówki, edytowane przez JW: sekcja „Nakazy dla modeli” trafia do promptów (od v46).
- `data/slowa_angielskie_ok.csv` — angielskie słowa, które mogą zostać w streszczeniach bez przekładu, edytowane ręcznie (`*` = dowolna końcówka; od v42).
- `docs/karton.html` — Karton Prasówki, interaktywna mapa prasówki, ze znacznikami wersji czytanymi przez Raport Mostu (od v41).

## Konfiguracja i sekrety

Sekrety repozytorium (Settings → Secrets and variables → Actions):

- `DISCORD_WEBHOOK_URL` — webhook kanału prasówki. Bez niego wysyłka jest pomijana bez błędu.
- `DISCORD_WEEKLY_WEBHOOK_URL` — webhook kanału `#top-tygodnia` (tygodniowe top 5).
- `DISCORD_MONTHLY_WEBHOOK_URL` — webhook kanału miesięcznego top 10.
- `DISCORD_TEST_WEBHOOK_URL` — webhook kanału testowego: uruchomienia z gałęzi i alarmy o błędach. Bez niego uruchomienia z gałęzi niczego nie wysyłają.
- `GROQ_API_KEY` — klucz API Groq do streszczeń AI (od v33 także do zapasowej korekty streszczeń w zestawieniach). Bez niego prasówka idzie bez streszczeń.
- `GEMINI_API_KEY` — klucz API Google Gemini (darmowy limit, bez płatności) do korekty językowej prasówki i zestawień; opcjonalny. Bez niego korektę robią modele Groq. Opcjonalna zmienna repozytorium `GEMINI_MODEL` (nazwy po przecinku) podmienia nazwy modeli, a `GEMINI_LITE_MODEL` – nazwy lżejszych modeli (v37a).
- `MISTRAL_API_KEY` — klucz API Mistral (darmowy plan, bez karty) – ostatni zapas korekty językowej prasówki (v37a); opcjonalny. Opcjonalna zmienna `MISTRAL_MODEL` podmienia model.

Każdy sekret trafia tylko do kroku workflow, który go potrzebuje. Token budzika jest przechowywany wyłącznie w cron-job.org. Nigdy nie zapisuj w repozytorium kluczy API, adresów webhooków, tokenów ani haseł.

## Rozwój i testy

Testy jednostkowe uruchamia się z katalogu głównego repozytorium:

```bash
python -m unittest discover -s src -p "test_*.py"
```

Kontrola słów potrzebuje Morfeusza 2 (`pip install morfeusz2`; workflow instalują go same, od v42); bez niego jest pomijana. Każdy workflow uruchamia testy przed swoim głównym krokiem. Zmiany powstają na gałęzi, są testowane na kanale testowym, opisywane w changelogu (PL/EN) i scalane przez Squash and merge.

## Dokumentacja

Dokumentacja jest prowadzona po angielsku i po polsku; każda zmiana techniczna trafia do obu wersji README i do pliku [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

**Karton Prasówki** (`docs/karton.html`) to interaktywna mapa prasówki. Od v41 każda wersja aktualizuje go w tej samej rundzie (zasada 9 ekosystemu „Karton zawsze aktualny”): znaczniki `prasowka-wersja` i `plik-matka-wersja`, widoczny stan i liczbę testów. `src/test_v41.py` zapala się na czerwono, gdy Karton nie zgadza się z changelogiem, mirrorem albo liczbą testów.

## Licencja słowniczka

Plik `data/glosariusz_mirror.csv` (formy, objaśnienia w nawiasach i reguły) pochodzi z glosariusza CyberSec Mozaika: treści na licencji CC BY-NC-ND 4.0, © 2026 Jan Wolski.
