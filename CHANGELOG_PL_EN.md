# Changelog

Historia rozwoju produktu **CyberSec-NewsDigest-AI** -- automatycznego
pobierania i przetwarzania wiadomości cyberbezpieczeństwa z kanałów
RSS/Atom.

Najnowsze wersje na górze. Numery v1--v10 porządkują istotne etapy
funkcjonalne odtworzone z historii Git; nie są oficjalnymi tagami wydań.
Ich daty wskazują datę autora odpowiednich commitów w historii Git, a
nie czas utworzenia lokalnego pliku ani osobno potwierdzony moment
wydania. Powiązane commity scalono w jeden wpis. Pominięto zmiany czysto
kosmetyczne, tymczasowe diagnostyki i eksperymenty usunięte później.

Od v11 wpisy są dodawane na bieżąco, razem z każdą zmianą, przed jej
scaleniem do gałęzi `main`. Jedna wersja odpowiada jednej logicznej
zmianie; automatyczne aktualizacje historii artykułów przez workflow nie
otrzymują osobnych wersji. Od v24 drobne poprawki (np. zmiana jednego
objaśnienia) nie dostają osobnego numeru: są opisywane w najbliższej
wersji jako osobny akapit.

Format inspirowany [Keep a Changelog](https://keepachangelog.com/).
Źródło wpisów v1--v10: historia Git (113 commitów), opisy commitów i
przeanalizowane diffy.

------------------------------------------------------------------------

## v29 --- 25.10.2026

**Zaostrzona kontrola językowa streszczeń, ochrona przed limitem
zapytań, przeglądy zbiorcze i precyzyjniejszy 🔥.**

Powód: lektura prasówek z 23–24.10.2026. Cztery streszczenia po
angielsku; kalki („rekordy pacjentów”, „AI‑zarządzanego frameworka”,
„do intruzji”, „eksploatując”, „Kompromisy wystąpiły”, „rootowy kod”);
błędy gramatyczne („Publikuje się natychmiastowa łatka”, „nazwanego
łatki”, „iPhoneie”); „RCE (RCE)” po autokorekcie z v27; streszczenia
powtarzające tytuł („Node2Shell… umożliwia RCE przez dekompresję
Brotli”); dwa artykuły bez streszczenia, bo partia dostała błąd 429 od
obu modeli; przeglądy zbiorcze (ThreatsDay, In Other News, Weekendowa
lektura) streszczane jednym tematem, a Weekendowa lektura z 🔥; 🔥 przy
Ariście za starsze numery CVE z dalszej części strony; PHP trzy razy
(różne tytuły, te same CVE).

Zmiany:

- **Lista stylu `data/styl_unikaj.csv`** (nowa, edytowana przez JW):
  kalka i podpowiedź, `*` = dowolna końcówka. Lista trafia do promptu i
  do kontroli; kalka wraca do poprawki, ale nigdy nie powoduje ucięcia
  ani odrzucenia streszczenia (problem „miękki”).
- **Kontrola języka** (`src/summary_quality.py`): streszczenie po
  angielsku wraca do poprawki, a jeśli nadal jest po angielsku –
  odpada (lepiej sam tytuł niż angielski tekst); streszczenie
  powtarzające tytuł (najwyżej dwa nowe słowa) wraca do poprawki;
  uwagi „Nie podano…” i samo „w tygodniu” (bez dat) zgłaszane jak
  ogólniki i względne określenia czasu.
- **Runda korekty językowej** (`src/ai_summaries.py`): po wszystkich
  streszczeniach jedno zapytanie do drugiego modelu (osobne limity):
  „popraw wyłącznie gramatykę, interpunkcję, literówki i kalki, nie
  zmieniaj faktów”. Poprawka jest przyjmowana tylko, gdy zachowuje
  liczby i numery CVE, długość (60–140%), nie wprowadza nowych
  problemów; inaczej zostaje wersja sprzed korekty. Log: „KOREKTA: …”.
- **Limit zapytań**: zapytania do jednego modelu są rozłożone w czasie
  (co najmniej 20 s odstępu), a partia, której nie obsłużył żaden model,
  jest ponawiana na końcu po 60 s.
- **Autokorekta**: „zdalne wykonanie kodu (RCE)” daje „RCE” (bez
  „RCE (RCE)”), słowo powtórzone w nawiasie za sobą jest usuwane,
  „iPhoneie” → „iPhonie”.
- **Przeglądy zbiorcze**: ThreatsDay, Weekly Recap i In Other News są
  pomijane jak treści promocyjne (ich tematy i tak są w prasówce
  osobno; licznik „Odrzucone jako promocja” obejmuje je w logu).
  „Weekendowa lektura” zostaje (decyzja z v12), ale jako przegląd:
  stały opis zamiast streszczenia AI, bez 🔥 i bez łączenia po
  numerach CVE.
- **Precyzyjniejszy 🔥 i łączenie po CVE** (`src/kev.py`,
  `src/event_grouping.py`): liczą się tylko numery CVE z tytułu i
  pierwszych 600 znaków tekstu; wspólny taki numer łączy artykuły w to
  samo wydarzenie (także z jednego serwisu).

Nowe i zmienione pliki: `data/styl_unikaj.csv` (nowy),
`src/summary_quality.py`, `src/ai_summaries.py`, `src/glossary.py`,
`src/article_selection.py`, `src/kev.py`, `src/event_grouping.py`,
`src/test_ai_summaries.py`, `src/test_summary_quality.py`,
`src/test_glossary.py`, `src/test_article_selection.py`,
`src/test_kev.py`, `src/test_event_grouping.py`, README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe (268) zakończone powodzeniem,
w tym przykłady z prasówek z 23–24.10.2026. Test na gałęzi oczekuje na
wykonanie. Łączenie tematów po nazwach firm w tytułach (Quest
Diagnostics, Capcom) zostaje na kolejną wersję.

## v28 --- 23.10.2026

**🔥 przy lukach z katalogu CISA KEV.**

Katalog Known Exploited Vulnerabilities (CISA) zawiera luki z
potwierdzonym wykorzystywaniem w atakach; w 2025 r. dodano do niego 245
pozycji (ok. 4–5 tygodniowo). Dla analityka SOC to sygnał „łatać
najpierw”.

- **Znacznik ustawia kod, nie AI** (nowy `src/kev.py`): katalog (JSON)
  jest pobierany raz na uruchomienie z CISA, a gdy to się nie uda – z
  lustra CISA na GitHubie. Numery CVE są szukane w tytule, tekście z
  kanału i tekście ze strony artykułu, także w artykułach połączonych w
  to samo wydarzenie. Artykuł z numerem CVE z katalogu dostaje 🔥 przed
  tytułem, a pod prasówką pojawia się objaśnienie „🔥 luka z katalogu
  CISA KEV – potwierdzone wykorzystywanie w atakach”. Bez dostępu do
  katalogu prasówka idzie bez znaczników (log: „CISA KEV: …”).
- **Archiwum** zapisuje numery CVE artykułu (`cves`) i te z katalogu
  (`kev`).
- **Zestawienia tygodniowe i miesięczne** pobierają katalog jeszcze raz i
  sprawdzają zapisane numery CVE (oraz numery w tytule i streszczeniu),
  bo CISA często dodaje lukę kilka dni po pierwszych artykułach. 🔥 i
  objaśnienie pojawiają się także tam.

Nowe i zmienione pliki: `src/kev.py` (nowy), `src/test_kev.py` (nowy),
`src/main.py`, `src/discord_output.py`, `src/article_archive.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/test_monthly_top.py` i
`src/test_weekly_top.py` (testy nie pobierają katalogu), README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe (250) zakończone powodzeniem.
Test na gałęzi `v28-kev` 23.10.2026 (01:34): katalog pobrany z
www.cisa.gov (1754 pozycje), oznaczone 2 z 20 artykułów (Arista
VeloCloud Orchestrator CVE-2026-114625, BeyondTrust Remote Support
CVE-2026-102764), objaśnienie 🔥 pod prasówką; streszczenia AI 20 z 20
(jedna poprawka po błędzie 429 u obu modeli uratowana naprawą przez
kod). Do dalszej obserwacji: uwagi w formie „Nie podano informacji…” /
„Nie podano zaleceń” nie są jeszcze wykrywane, a przegląd typu
„ThreatsDay” streszczany jest jednym tematem z wielu.

## v27 --- 22.10.2026

**Odmiana terminów i objaśnień oraz pełna treść artykułów ze stron.**

Powód: w teście v26 (22.10.2026) pojawiło się „ostrzegają przed exploit
(kod wykorzystujący podatność)”: termin bez odmiany i objaśnienie w
mianowniku. Część kanałów (BleepingComputer, The Hacker News, The
Record) daje tylko jedno-dwa zdania zajawki, więc AI miało mało
materiału.

Zmiany:

- **Objaśnienia w nawiasach w tym samym przypadku co termin**
  (`src/glossary.py`): exploit, botnet i infostealer odmieniają się jak
  polskie rzeczowniki, a objaśnienie idzie za nimi: „przed exploitem
  (kodem wykorzystującym podatność)”, „członkowie botnetu (sieci
  zainfekowanych urządzeń)”, „ochrona przed infostealerami (programami
  kradnącymi dane)”. Morfeusz 2 nie zna tych słów, więc ich formy
  odpowiadają polskim wzorom wygenerowanym przez Morfeusz 2 (exploit jak
  „kotlet” – exploicie, botnet jak „budżet” – botnecie, infostealer jak
  „komputer” – infostealerze); objaśnienia też wygenerowano Morfeuszem 2.
  Forma „exploita”/„infostealera” może być dopełniaczem albo biernikiem:
  dopełniacz jest wybierany po przyimku (do, od, bez, z…), po
  przeczeniu („nie wykryto exploita”), po „użyć/używać”, „szukać”,
  „potrzebować” i po rzeczowniku odczasownikowym („wykorzystanie
  exploita”); w pozostałych przypadkach biernik (zgodnie z decyzją z
  19.10.2026 dla form niejednoznacznych). Ransomware jest nieodmienne.
- **Kontrola nieodmienionych terminów** (`src/summary_quality.py`):
  exploit, botnet, infostealer, backdoor, keylogger, rootkit, loader,
  dropper, trojan, phishing w formie podstawowej po przyimku lub
  wyrażeniu wymagającym innego przypadku („przed exploit”, „przy użyciu
  botnet”, „przed nowym infostealer”) wracają do AI do poprawki.
  Prompt wymaga odmiany z przykładami, a prośba o poprawkę słowniczka
  mówi, żeby odmienić wymaganą formę tak jak użytą („eksploitem” →
  „exploitem”).
- **Pełna treść ze strony artykułu** (nowy `src/article_pages.py`): gdy
  materiał z kanału ma mniej niż 600 znaków, strona artykułu jest
  pobierana raz (limit czasu 15 s, do 2 MB, tylko HTML), a z niej
  zbierane są akapity (`<p>`), najlepiej z wnętrza `<article>`, bez
  skryptów, menu, stopki, bocznych ramek, krótkich akapitów i
  typowych dopisków (newsletter, cookies, „czytaj też”, reklama). Tekst
  strony jest danymi jak tekst z kanału i służy tylko jako materiał
  dla AI i kontroli faktów; nie trafia do historii ani archiwum. Błąd
  strony (np. 403 z ochrony przed botami) zostawia artykuł z materiałem
  z kanału. Log: „Pełna treść ze stron: N z M…” oraz „PEŁNA TREŚĆ: …”
  przy błędach.

Zmienione i nowe pliki: `src/glossary.py`, `src/summary_quality.py`,
`src/ai_summaries.py`, `src/test_ai_summaries.py`, `src/main.py`,
`src/article_pages.py` (nowy),
`src/test_article_pages.py` (nowy), `src/test_glossary.py`,
`src/test_summary_quality.py`, `src/discord_output.py`,
`src/test_discord_output.py`, README (PL/EN).

Pierwszy test na gałęzi `v27-odmiana-strony` 22.10.2026: pełna treść
pobrana z 10 z 11 stron (jedna: przekroczony czas połączenia), w tym z
BleepingComputer, The Hacker News, SecurityWeek, Kapitana Hacka, CERT
Polska i Krebsa; streszczenia AI 15 z 15, odmiana poprawna („przed
exploitem (kodem wykorzystującym podatność)”). Streszczenia stały się
konkretne (numery CVE, wersje z łatką, liczby z operacji Interpolu), ale
też za długie: jedno zdanie łączone średnikami, dwa ucięte na limicie
450 znaków, do tego dopisane zalecenia i uwaga, czego raport nie podaje.

Poprawki po teście:

- Kontrola (`src/summary_quality.py`) zgłasza streszczenie dłuższe niż
  400 znaków, średnik łączący zdania oraz uwagi o braku informacji
  („nie podaje informacji o…”, „brak informacji o…”).
- Prompt: najwyżej 350 znaków, krótkie zdania bez średników, najwyżej 3
  numery CVE lub wersje; zalecenia tylko, gdy wymienia je artykuł; bez
  uwag o tym, czego artykuł nie podaje.
- Prośba o poprawkę słowniczka nie każe „odmieniać” skrótów (RCE).
- Uzupełnienie v26: pliki z poprawką dopisku „także:”
  (`src/discord_output.py`, `src/test_discord_output.py`) nie trafiły do
  scalenia v26, choć changelog v26 ją opisuje; w teście v27 nadal było
  „thehackernews.com, thehackernews.com…”. Pliki dochodzą w v27.

Drugi test na gałęzi 22.10.2026: streszczenia krótsze, w zdaniach z
kropkami i bez ucięć, ale 8 z 16 artykułów zostało **bez streszczenia**:
nowa kontrola długości i średników zgłosiła więcej streszczeń, a
streszczenie, które po rundzie poprawek nadal miało problem (albo
którego poprawka się nie udała), było w całości odrzucane. Do tego
„patchują” w streszczeniu Aristy i „Raport nie podaje sprawcy” w
streszczeniu o Pegasusie.

Poprawki po drugim teście:

- **Naprawa przez kod zamiast odrzucenia** (`src/ai_summaries.py`,
  `src/summary_quality.py`): gdy poprawione przez AI streszczenie nadal
  ma problem albo prośba o poprawkę się nie udała (np. limit zapytań),
  kod zamienia średniki na kropki, usuwa zdania z problemami i skraca
  tekst do całych zdań w limicie 400 znaków. Odrzucane jest tylko
  streszczenie, w którym nie zostało żadne poprawne zdanie. Log:
  „KONTROLA: streszczenie N naprawione przez kod…”.
- Kontrola uwag o braku informacji obejmuje też „raport/artykuł nie
  podaje…”.
- Słowniczek, drobna zmiana: przy „łatka” (H166) zakazane są też
  spolszczenia „patchować” („patchują”, „spatchowany”);
  `tools/eksport_mirrora.py` (OVERRIDES H166),
  `data/glosariusz_mirror.csv` (tylko wiersz H166).

Pełny log drugiego testu pokazał przyczynę: większość próśb o poprawkę
dotyczyła „poprawki” → „łatka”, „zdalne wykonanie kodu” → „RCE” i
średników, a jedna runda poprawek dostała od Groq błąd 429 (limit
zapytań), więc pięć streszczeń odpadło naraz („brak poprawki”). Jedno
odpadło przez datę „21”, której nie było w materiale.

Dalsze poprawki:

- **Poprawki bez zapytania do AI** (`src/glossary.py`, funkcja
  `autofix`, wywoływana w `clean_summary`): „poprawka” w każdej formie →
  „łatka” w tej samej formie (poprawce → łatce), „zdalne wykonanie
  (dowolnego) kodu” i „remote code execution” → „RCE” (nieodmienne),
  „eksploit…” → „exploit…”, średnik → koniec zdania. Mniej próśb o
  poprawkę to mniejsze ryzyko limitu zapytań.
- **Druga szansa przy błędzie poprawki**: gdy prośba o poprawkę do
  jednego modelu się nie uda (np. 429), pytany jest drugi model Groq
  (osobne limity), a dopiero potem działa naprawa przez kod.
- Ucięcie na limicie znaków nie tworzy już niedokończonego zdania: limit
  bezpieczeństwa w `clean_summary` to 1000 znaków, a długość do 400
  znaków pilnuje kontrola i naprawa przez kod (całe zdania).

Zmianę zweryfikowano: testy jednostkowe (240) zakończone powodzeniem.
Trzeci test na gałęzi 22.10.2026: pełna treść pobrana z 12 z 12 stron,
streszczenia AI **16 z 16**, tylko jedna prośba o poprawkę (uwaga
„Raport nie podaje…”, poprawiona przez AI), bez błędu limitu zapytań i
bez naprawy przez kod. Streszczenia mają 1–3 zdania z kropkami, bez
średników i ucięć, z numerami CVE, wersjami i liczbami ze stron
artykułów; odmiana poprawna („chroniące przed exploitem (kodem
wykorzystującym podatność)”), „także:” wymienia każdy serwis raz.
Zauważony błąd do dalszej obserwacji: w jednym streszczeniu rok
„2024” z tytułu trafił do daty łatki („21 października 2024”); kontrola
faktów tego nie wykrywa, bo liczba występuje w materiale.

## v26 --- 22.10.2026

**Pięć nowych źródeł, filtr wieku artykułów i lepsze łączenie tego
samego wydarzenia.**

Nowe źródła (wybór z 22.10.2026 na podstawie częstotliwości publikacji i
znaczenia w branży): **CERT Polska** i **Kapitan Hack** (polskie),
**SecurityWeek** (ok. 6–7 tekstów dziennie, najlepsze pokrycie łatek
producentów), **The Record** (ok. 4 dziennie, dziennikarstwo: ataki
państwowe, policja, polityka) i **Krebs on Security** (ok. 1 tygodniowo,
własne śledztwa). Odrzucone: Help Net Security (dużo materiałów
producentów), Dark Reading (dużo opinii), Security Affairs i agregatory
(przedruki). Źródeł jest teraz 11 (6 polskich, 5 angielskich).

Zmiany w kodzie:

- **Filtr wieku** (`src/rss_helpers.py`): wpisy starsze niż 3 dni (data
  `pubDate` w RSS albo `published`/`updated` w Atom) są pomijane, bo
  kanały nowych źródeł zawierają też starsze teksty (Krebs: ok. dwa
  miesiące). 3 dni obejmują przerwę niedzielną. Wpisy bez daty lub z
  nieczytelną datą przechodzą. Log pokazuje ich liczbę („Pominięte jako
  starsze niż 3 dni”).
- **Limity źródeł** (`src/article_selection.py`): SecurityWeek i The
  Record po 3 artykuły, żeby częste źródła angielskie nie wypychały
  polskich z dziennej dwudziestki; pozostałe bez zmian (4, Niebezpiecznik
  2).
- **Łączenie wydarzeń** (`src/event_grouping.py`): wspólna nazwa z
  literami i cyframi (np. PHP2Shell, Plex2Shell, Log4j) łączy artykuły
  jak wspólny numer CVE. Dotąd nazwa dużego wydarzenia występowała w
  wielu tytułach dnia, więc nie była „rzadka” i nie łączyła artykułów
  (test 22.10.2026: trzy osobne pozycje o PHP2Shell). Wspólny CVE lub
  taka nazwa łączy też dwa artykuły z jednego serwisu (The Hacker News
  pisał o PHP2Shell dwa razy). Nazwy grup (APT28, UNC…, Storm-…) i
  ogólne nazwy techniczne (Win32, x64…) nie łączą artykułów, bo
  występują w różnych historiach. Ta sama reguła działa w zestawieniach
  tygodniowych i miesięcznych oraz w sekcji „Ciąg dalszy”.

Zmienione i nowe pliki: `src/main.py` (lista źródeł, filtr wieku, log),
`src/rss_helpers.py`, `src/article_selection.py`,
`src/event_grouping.py`, `src/test_event_grouping.py`,
`src/test_article_age.py` (nowy), README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe zakończone powodzeniem, w tym
tytuły z testu 22.10.2026 (cztery artykuły o PHP2Shell łączą się w
jedną pozycję, Plex2Shell zostaje osobno, dwa artykuły o APT28 nie
łączą się). Test na gałęzi `v26-zrodla` 22.10.2026: wszystkie 11
kanałów pobrane bez błędów (CERT Polska 100 wpisów, Kapitan Hack 10,
SecurityWeek 10, The Record 5, Krebs 10); 173 wpisy pominięte jako
starsze niż 3 dni; prasówka z 15 artykułami (dotąd ok. 10) z 11 źródeł,
w tym 7 z polskich; 6 artykułów połączonych z innymi (PHP2Shell: 5
artykułów z 3 serwisów w jednej pozycji); streszczenia AI 15 z 15.

Poprawka po teście: dopisek „także:” wymieniał ten sam serwis kilka
razy („thehackernews.com, thehackernews.com, securityweek.com,
securityweek.com”). Teraz każdy inny serwis jest podany raz (z
pierwszym artykułem), a serwis artykułu głównego nie jest powtarzany
(`src/discord_output.py`, `src/test_discord_output.py`; testy: 227).

## v25 --- 22.10.2026

**Ostrzejsze streszczenia AI: konkrety zamiast ogólników, kontrola faktów
i czasu, poprawna wielka litera.**

Powód: prasówka trafia już do kilku osób, w tym mentorów, a w
streszczeniach z 19–22.10 powtarzały się błędy: ogólniki („co stanowi
poważne zagrożenie…”), „Łatki zostaną udostępnione jutro” pokazane
potem w zestawieniu tygodniowym, „98 zero-day” bez rzeczownika,
„exploit tych luk mogą prowadzić” z małej litery po poprawce
słowniczka, „emergency łatki” oraz „podatności (luka)” bez odmiany.

Zmiany:

- **Nowy prompt** (`src/ai_summaries.py`): 2–3 zdania; pierwsze zdanie
  mówi, co się stało i kogo dotyczy (firma, produkt i wersja, grupa,
  CVE), kolejne – skala, skutki i co zrobić, jeśli artykuł o tym pisze;
  zakaz ogólników i względnych określeń czasu; liczby i nazwy dokładnie
  z artykułu; liczby z rzeczownikiem („98 luk zero-day”); bez
  angielskich wtrąceń poza nazwami własnymi i słowniczkiem; 1 zdanie,
  gdy materiałem jest tylko tytuł lub zajawka.
- **Kontrola jakości** (nowy `src/summary_quality.py`), w tej samej
  rundzie poprawek co słowniczek: ogólniki (lista fraz), względne
  określenia czasu („jutro”, „dziś”, „wczoraj”, „w przyszłym
  tygodniu”…, a także dzień tygodnia bez daty, np. „w środę”), numery CVE i liczby większe niż 12, których nie ma w
  tytule ani tekście artykułu (bez sprawdzania bieżącego roku i lat
  sąsiednich; „26 739” i „1,83” porównywane z „26,739” i „1.83M”).
  Streszczenie z problemem wraca raz do AI z opisem problemu, a jeśli
  nadal jest złe, zostaje odrzucone (lepiej bez streszczenia niż z
  błędną liczbą). Log pokazuje każdą kontrolę jako „KONTROLA: …”.
- **Wielka litera na początku zdań** poprawiana przez kod (z wyjątkiem
  skrótów: np., m.in., ok., tys., Inc. itd.).
- **Słowniczek, drobna zmiana bez osobnej wersji:** przy „podatność”
  (H164) AI nie dopisuje już „(luka)”; forma „(luka)” w nawiasie jest
  zakazana, a słowa „luka” można używać zamiennie. Przy RCE (H090)
  zakazana jest też angielska forma „remote code execution”. Zmiany:
  `tools/eksport_mirrora.py` (OVERRIDES H164 i H090),
  `data/glosariusz_mirror.csv` (tylko wiersze H164 i H090).

Nowe i zmienione pliki: `src/summary_quality.py`,
`src/test_summary_quality.py`, `src/ai_summaries.py`,
`src/test_ai_summaries.py`, `src/test_glossary.py`,
`tools/eksport_mirrora.py`, `data/glosariusz_mirror.csv`, README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe (218) zakończone powodzeniem;
kontrola uruchomiona na 33 streszczeniach z archiwum października
wychwyciła 7 z nich („jutro”, „W minionym tygodniu”, „stanowi poważne
zagrożenie dla”, 4 × „podatności (luka)”), a poprawka wielkich liter
naprawiła „exploit tych luk mogą…”. Test na gałęzi
`v25-streszczenia` 22.10.2026: prasówka z 10 artykułami na kanale
testowym, streszczenia AI 10 z 10; kontrola zgłosiła 4 streszczenia
(„poprawka” zamiast „łatka”, „zdalnego wykonania kodu” zamiast „RCE”),
wszystkie poprawione w drugiej rundzie; kontrola faktów nie odrzuciła
żadnego streszczenia. Streszczenia podają daty, liczby i nazwy z
artykułów. Po teście dodano zakaz dnia tygodnia bez daty („przed
wydaniem łatki w środę”) i formy „remote code execution”.

## v24 --- 22.10.2026

**Zewnętrzny budzik (cron-job.org) jako główny wyzwalacz prasówki i
zestawień; MFA bez nawiasu.**

Powód: harmonogram GitHuba w tym repozytorium jest praktycznie
bezużyteczny. Sondy z 19–20.10 dały ok. 4 starty na 70 oczekiwanych, a
20–21.10 nie ruszyła ani jedna z czterech porannych prób; prasówki
trzeba było uruchamiać ręcznie.

Rozwiązanie: serwis cron-job.org wywołuje API GitHuba
(`POST /repos/…/actions/workflows/<plik>/dispatches`, body
`{"ref":"main","inputs":{"budzik":"true"}}`) z tokenem fine-grained PAT
(tylko to repozytorium, uprawnienie Actions: Read and write, ważny rok;
przechowywany wyłącznie w cron-job.org). Trzy zadania w strefie
Europe/Warsaw:

- Daily Digest -- poniedziałek–sobota, 6:17 (`daily-digest.yml`),
- Weekly Top 5 -- poniedziałek, 8:17 (`weekly-top.yml`),
- Monthly Top 10 -- 1. dzień miesiąca, 8:17 (`monthly-top.yml`).

Harmonogram GitHuba zostaje jako zapas. Żeby budzik i zapas nigdy nie
wysłały tego samego dwa razy, wszystkie trzy workflowy mają nowe pole
`budzik` (przełącznik, domyślnie wyłączony) i przekazują zmienną
`TRIGGER` (`budzik` albo nazwa zdarzenia GitHuba). Strażnicy
(`src/run_guard.py`, `src/top_guard.py`) traktują `budzik` jak
uruchomienie z harmonogramu: jeśli dzień, tydzień lub miesiąc został już
obsłużony, uruchomienie kończy się bez wysyłki. Ręczne uruchomienie
(przełącznik `budzik` niezaznaczony) nadal nigdy nie jest blokowane.
Znacznik `data/last_digest.json` zapisuje `"trigger": "budzik"`, więc
widać, co wysłało prasówkę.

Przy okazji (drobna zmiana bez osobnej wersji): **MFA bez nawiasu.**
Skrót jest powszechnie znany („praktycznie wszyscy mamy z tym do
czynienia”), więc kod nie dopisuje już przy nim „(uwierzytelnianie
wieloskładnikowe)”. Objaśnienia w nawiasach ma teraz 6 terminów:
ransomware, infostealer, exploit, botnet, podwyższenie (eskalacja)
uprawnień i poświadczenia (dane logowania). Forma „MFA” i zakaz
rozwiniętej formy polskiej w tekście zostają.

Zmienione pliki: `.github/workflows/daily-digest.yml`, `weekly-top.yml`,
`monthly-top.yml` (pole `budzik`, zmienna `TRIGGER`, komentarze),
`src/run_guard.py`, `src/top_guard.py`, `src/test_run_guard.py`,
`src/test_top_guard.py`, `tools/eksport_mirrora.py` (OVERRIDES H232),
`data/glosariusz_mirror.csv` (tylko wiersz H232), `src/test_glossary.py`
(testy objaśnień przeniesione z MFA na botnet; dopasowanie skrótów
sprawdzane na przykładowym haśle), README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe (203) zakończone powodzeniem;
uruchomienie testowe zadania Weekly Top 5 w cron-job.org 21.10.2026
zwróciło 204 i uruchomiło workflow na `main` (zakończony powodzeniem,
bez wysyłki, bo archiwum nie obejmuje tygodnia 12–18.10). Test na
gałęzi `v24-budzik` 22.10.2026: uruchomienie bez pola `budzik`
dostarczyło prasówkę (2 artykuły) na kanał testowy, a uruchomienie z
zaznaczonym polem `budzik` zakończyło się bez wysyłki z komunikatem
„Dzisiejsza prasówka już poszła – ten zaplanowany start kończy się bez
wysyłki.”. Potwierdzone 23.10.2026: budzik uruchomił prasówkę o 6:17
(`workflow_dispatch` na `main`, zakończone powodzeniem), znacznik
`data/last_digest.json` zapisał `"trigger": "budzik"` i 20 artykułów;
harmonogram GitHuba tego ranka nie uruchomił żadnej próby, więc nie
było czego blokować (sama blokada jest potwierdzona testem na gałęzi).
Była to też pierwsza prawdziwa prasówka z v28: 2 artykuły z 🔥
(Arista VeloCloud Orchestrator, BeyondTrust Remote Support),
streszczenia 20 z 20.

## v23 --- 21.10.2026

**Jednorazowe uzupełnienie streszczeń AI w archiwum dla artykułów
zarchiwizowanych przed v22.**

Powód: archiwum zaczęło zapisywać streszczenia dopiero w v22, więc 11
artykułów z 19–20.10.2026 nie miało streszczeń i zestawienia tygodniowe
i miesięczne pokazywały przy nich same tytuły. Przeoczenie z v17/v18
(zestawienia budowane z archiwum bez streszczeń).

Nowy moduł `src/backfill_summaries.py` i ręczny workflow
`.github/workflows/backfill-summaries.yml` („Backfill AI summaries”):
dla wskazanego miesiąca archiwum wyszukuje rekordy bez streszczenia,
odnajduje te artykuły w aktualnych kanałach RSS (ten sam materiał co w
prasówce: pełny tekst albo opis), przygotowuje streszczenia tym samym
modułem AI z obowiązkowym słowniczkiem i zapisuje je w archiwum.
Artykuły, których nie ma już w kanałach, są streszczane z samego
tytułu (AI pisze wtedy 1 zdanie i niczego nie dodaje); log oznacza je
„tylko tytuł”. Najpierw uruchamia się podgląd (`save = false`, wynik
tylko w logu), potem zapis (`save = true`). Rekordy ze streszczeniem
nie są zmieniane; uruchomienie z gałęzi niczego nie zapisuje; nic nie
trafia na Discord. Workflow ma wspólną grupę współbieżności z prasówką
(`daily-digest`), bo oba zapisują archiwum.

Zmianę zweryfikowano: testy jednostkowe (194) zakończone powodzeniem,
w tym uzupełnianie tylko brakujących streszczeń, podgląd bez zapisu,
brak zapisu z gałęzi i materiał z RSS albo z tytułu.

Podgląd na `main` (21.10.2026, 00:22): 11 artykułów bez streszczenia,
9 odnalezionych w kanałach RSS, 2 już nie (BleepingComputer: F5/NGINX i
Microsoft/Exchange); 10 streszczeń, ale jedno z nich to opis braku
materiału („Brak dostępnych informacji w treści artykułu.”), a przy
jednym AI nie zwróciło nic. Poprawka przed zapisem:
`src/backfill_summaries.py` przy braku materiału podaje AI sam tytuł
jako tekst (AI oddaje go jednym zdaniem po polsku), a
`src/ai_summaries.py` odrzuca odpowiedzi opisujące brak materiału
zamiast streszczenia (zaczynające się od „Brak informacji…” albo
mówiące o „treści/tekście artykułu”) – dotyczy to też codziennej
prasówki. Testy: 196.

Porządki: w PR v23 pliki `backfill_summaries.py` i
`test_backfill_summaries.py` trafiły do głównego katalogu repozytorium
zamiast do `src`; właściwe wersje dodano następnie bezpośrednio na
`main` (dwa commity bez PR), a kopie z głównego katalogu usunięto w
poprawce.

Drugi podgląd (21.10.2026, 00:32): 11 z 11 streszczeń; 8 poprawnych,
3 z błędem: przy artykule z samego tytułu (Microsoft/Exchange) AI
dopisało niepoparte drugie zdanie („Microsoft zaleca zastosowanie
poprawek…”), przy OpenCode „distillation attacks” oddano jako „ataki na
procesy destylacji AI” (a chodzi o ataki polegające na destylacji, czyli
kopiowaniu modelu), przy Plex2Shell PoC przypisano sprawcom zamiast
badaczom; dwa streszczenia użyły „poprawki” zamiast ustalonej „łatki”.
Druga poprawka: przy samym tytule zapisywane jest tylko pierwsze zdanie
streszczenia (`src/backfill_summaries.py`), a „poprawka” trafiła na
listę form zakazanych hasła H166 (`tools/eksport_mirrora.py`,
`data/glosariusz_mirror.csv`), więc kontrola słowniczka wymusza
„łatkę” – także w codziennej prasówce. Błędy interpretacji (OpenCode,
Plex2Shell) poprawiane ręcznie w archiwum po zapisie. Testy: 198.

Zapis na `main` (21.10.2026, 00:42, commit „Backfill AI summaries in
archive”): 11 z 11 streszczeń w archiwum; artykuł Microsoft/Exchange z
samego tytułu ma jedno zdanie, „łatki” zamiast „poprawek”, błędy
OpenCode i Plex2Shell z drugiego podglądu się nie powtórzyły. Ręczna
korekta 2 streszczeń w `data/archive/2026-10.json` (redakcja, bez zmiany
faktów): F5 („out-of-band łatki” → „pozacykliczne łatki”) i oszustwo
„na urząd” (usunięte niepoparte „co umożliwiło szybkie podjęcie działań
obronnych”); dwie inne proponowane korekty (OpenCode Console, przegląd
tygodniowy THN) odrzucono. Podgląd
zestawienia tygodniowego 19–25.10 pokazuje streszczenia przy wszystkich
pozycjach. Workflow uzupełniania zostaje w repozytorium jako narzędzie
na przyszłość (np. po awarii AI).

**Ograniczenia:** workflow można uruchomić dopiero po scaleniu (GitHub
pokazuje przycisk tylko dla workflow z `main`), dlatego przed zapisem
jest podgląd. Streszczenia z samego tytułu są uboższe. Narzędzie jest
jednorazowe; po uzupełnieniu archiwum workflow można usunąć.

## v22 --- 20.10.2026

**Tygodniowe top 5, jednorazowa wysyłka zestawień tygodniowych i
miesięcznych oraz streszczenia AI w zestawieniach.**

Nowy moduł `src/weekly_top.py`: w poniedziałek 5 najważniejszych
wydarzeń poprzedniego tygodnia (poniedziałek–niedziela) trafia na nowy
kanał Discorda `#top-tygodnia` (sekret `DISCORD_WEEKLY_WEBHOOK_URL`).
Grupowanie i ranking są takie same jak w zestawieniu miesięcznym (liczba
artykułów, serwisów, punkty); tydzień na przełomie miesięcy czyta oba
pliki archiwum. Nowy workflow `.github/workflows/weekly-top.yml`: próby o
8:17, 9:17, 10:17 i 11:17 czasu polskiego; ręcznie można podać dowolną
datę z wybranego tygodnia.

Zabezpieczenie przed zawodnym harmonogramem (jak w v19): Monthly Top 10
ma teraz cztery próby 1. dnia miesiąca (8:17–11:17) zamiast jednej. Nowy
moduł `src/top_guard.py` zapisuje w `data/last_top.json`, za jaki
tydzień i miesiąc zestawienie już poszło; kolejne zaplanowane próby
kończą się bez wysyłki. Uruchomienia ręczne nie są blokowane. Nie
zapisują znacznika: uruchomienia testowe z gałęzi, brak webhooka (żeby
późniejsza próba mogła wysłać) oraz podgląd okresu, który jeszcze trwa
(żeby nie zablokował pełnego zestawienia). Oba workflow zestawień mają
uprawnienie zapisu (tylko znacznik) i wspólną grupę współbieżności
`top-reports`; wszystkie trzy workflow przed wysłaniem zmian pobierają
cudze zmiany (`git pull --rebase`), bo w poniedziałki prasówka i
zestawienie tygodniowe mogą zapisywać jednocześnie.

Streszczenia w zestawieniach: archiwum (`src/article_archive.py`)
zapisuje streszczenie AI każdego wysłanego artykułu, a zestawienia
pokazują je pod tytułem jako cytat (streszczenie pierwszego artykułu
wydarzenia, który je ma). Długie zestawienie powtarza nagłówek z
dopiskiem „(cd.)” w każdej kolejnej wiadomości – wcześniej druga
wiadomość zaczynała się od pozycji 9 w środku listy, co Discord źle
numerował. Wspólna wysyłka obu zestawień: funkcja `deliver` w
`src/monthly_top.py`. Testy używają tymczasowych znaczników i nie zależą
od gałęzi ani sposobu uruchomienia.

Zmianę zweryfikowano: testy jednostkowe (189) zakończone powodzeniem
także w środowisku gałęzi i zaplanowanego uruchomienia; podgląd
zestawienia tygodniowego 19–25.10.2026 na prawdziwym archiwum (OpenCode
połączony z dwóch serwisów). Ręczne uruchomienia Monthly Top 10 na
gałęzi `v22-top-tygodnia` (20.10.2026, 23:29 i 23:52, miesiąc 2026-10):
zestawienie wyłącznie na `#prasówka-test`, w drugiej wiadomości
nagłówek „(cd.)”, gałąź bez commita ze znacznikiem. Przy wgrywaniu
4 pliki trafiły najpierw do głównego katalogu repozytorium zamiast do
`src`; usunięto je przed scaleniem.

**Ograniczenia:** zestawienia tygodniowego nie da się uruchomić z gałęzi
przed scaleniem (GitHub pokazuje przycisk tylko dla workflow z `main`) –
pierwsze uruchomienie na żywo po scaleniu (21.10.2026, 00:03, podgląd
tygodnia 19–25.10) dotarło na `#top-tygodnia` i nie zapisało znacznika.
Artykuły zarchiwizowane przed tą zmianą nie miały streszczeń (11 z 11),
więc podgląd pokazał same tytuły – uzupełnienie: v23. Tytuły
angielskie nadal nie są tłumaczone (zaplanowane w kolejnej wersji).

## v21 --- 20.10.2026

**Mirror glosariusza z matki Mozaiki v84 i objaśnienia w nawiasach tylko
przy 7 wybranych terminach.**

`data/glosariusz_mirror.csv` wygenerowano z matki CyberSec Mozaika v84
(727 haseł): doszły H723 wiper, H724 komunikat bezpieczeństwa, H725
obejście uwierzytelniania i H726 DLL sideloading, które zastąpiły
tymczasowe wpisy z arkusza „Hasła do dopisania” (DOP-9…11).

Powód drugiej zmiany: w testach v20 kod objaśniał każdy z około 270
angielskich terminów z mirrora, więc nawiasów było za dużo, a część była
błędna („NATO (translacja adresów sieciowych)” – skrót NAT dopasowany
wewnątrz NATO; „DLL sideloading (instalacja spoza sklepu)” – krótsze
hasło dopasowane wewnątrz dłuższego). Decyzja z 20.10.2026: nawiasy
tylko przy 7 terminach – ransomware (program żądający okupu), infostealer
(program kradnący dane), exploit (kod wykorzystujący podatność), botnet
(sieć zainfekowanych urządzeń), MFA (uwierzytelnianie wieloskładnikowe),
podwyższenie (eskalacja) uprawnień oraz poświadczenia (dane logowania).
„Łatka” (zamiast „poprawka”) i „opłacani przez państwo” – bez nawiasu.
Pozostałe hasła nadal wymuszają formę w tekście i kontrolę form
zakazanych, tylko bez nawiasu.

Zmiany w kodzie: `tools/eksport_mirrora.py` nie dodaje już objaśnień
automatycznie (tylko z listy decyzji prasówki), a przy rozpoznawaniu
nazw „angielski pierwszy” pomija spacje i myślniki („DLL sideloading” =
„DLL side-loading”). `src/glossary.py`: skróty dopasowywane tylko jako
całe słowa (opcjonalnie z końcówką po myślniku, np. „IAB-ów”), dłuższe
terminy sprawdzane przed krótszymi; usunięto reguły odmiany dla
„poprawki” i „opłacanych przez państwo”. Testy zaktualizowano
(`src/test_glossary.py`, `src/test_discord_output.py`); test pilnuje, by
nawiasy miało dokładnie 7 wybranych haseł.

Zmianę zweryfikowano: testy jednostkowe (170) zakończone powodzeniem.
Ręczne uruchomienie na gałęzi `v21-mirror-v84` (20.10.2026, 23:06):
8 artykułów spośród 92, prasówka wyłącznie na `#prasówka-test`;
nawiasy dodane przez kod tylko przy ransomware, exploit i poświadczeniach
(odmienione: „poświadczeń (danych logowania)”), brak błędnych objaśnień.

**Ograniczenia:** AI w jednym streszczeniu napisało „poprawce” zamiast
„łatce” – forma „poprawka” nie jest na liście zakazanych, więc kontrola
jej nie wyłapuje (do rozważenia w wersji o jakości streszczeń). Matka
Mozaiki ma przy H166 „poprawka, łatka”, a w uwagach do H015
„oprogramowanie wymuszające okup” – zgodnie z zasadą ujednolicenia
formy z prasówki można przenieść do matki w kolejnej jej wersji.

## v20 --- 20.10.2026

**Kanał testowy dla uruchomień z gałęzi: test nie trafia na kanał
główny i niczego nie zapisuje.**

Powód: 20.10.2026 test na gałęzi `v19-harmonogram` wysłał 2 artykuły na
kanał główny i zapisał je jako opublikowane tylko na tej gałęzi; 10
minut później spóźnione uruchomienie z harmonogramu na `main` wysłało te
same 2 artykuły drugi raz, bo `main` o nich nie wiedział.

Nowy moduł `src/test_mode.py`: uruchomienie na każdej gałęzi innej niż
`main` (zmienna `GITHUB_REF_NAME`) jest testowe – prasówka idzie na
osobny kanał Discorda `#prasówka-test` (sekret
`DISCORD_TEST_WEBHOOK_URL`), pierwsza wiadomość ma nagłówek „🧪 TEST ·
gałąź … · bez zapisu w historii i archiwum”, a `src/main.py` nie
zapisuje opublikowanych linków, archiwum, historii ani znacznika dnia.
Gałąź zachowuje więc dane `main`, a `main` nigdy nie wyśle ponownie
artykułów sprawdzonych na gałęzi. Bez sekretu testowego uruchomienie z
gałęzi niczego nie wysyła i nigdy nie trafia na kanał główny. To samo
dotyczy miesięcznego top 10 (`src/monthly_top.py`). Oba workflow
przekazują `DISCORD_TEST_WEBHOOK_URL` tylko do kroku wysyłki.
Uruchomienia z `main` (ręczne i z harmonogramu) działają bez zmian.

Przy okazji nowy test `src/test_scripts_compile.py` sprawdza składnię
wszystkich plików w `src`, także tych, których nie ładują inne testy:
pierwsza wersja zmiany w `main.py` miała błąd składni (`elif` po bloku
`try/except`), który testy jednostkowe przepuściły, a uruchomienie
zatrzymało się przed pobraniem czegokolwiek (nic nie wysłano ani nie
zapisano).

Zmianę zweryfikowano: testy jednostkowe (165) zakończone powodzeniem;
symulacja `main.py` na sztucznych danych w obu trybach (gałąź: wysyłka
tylko na kanał testowy, historia bez zmian; `main`: kanał główny,
historia zapisana). Na gałęzi `v20-kanał-testowy`: uruchomienie o 12:14
nie znalazło nowych artykułów (log potwierdził tryb testowy i brak
zapisu); uruchomienie o 22:38 wysłało 7 artykułów spośród 92 wyłącznie
na `#prasówka-test` z nagłówkiem testowym, a gałąź nie dostała commita
z danymi.

**Ograniczenia:** tryb testowy rozpoznaje tylko nazwę gałęzi; ręczne
uruchomienie na `main` zawsze idzie na kanał główny. Test na gałęzi nie
sprawdza zapisu historii i archiwum (z założenia) – te części potwierdza
dopiero pierwsza prasówka po scaleniu.

## v19 --- 20.10.2026

**Niezawodny poranny start: cztery próby z harmonogramu i strażnik
„jedna prasówka dziennie”.**

Diagnoza harmonogramu z v14 (19–20.10.2026): pierwsze zaplanowane
uruchomienie 19.10 przyszło o 11:54 zamiast o 6:17, a 20.10 nie przyszło
wcale. Dwie tymczasowe sondy (cron co 20 minut, jedna w UTC, druga z
polem `timezone: Europe/Warsaw`) przez dobę uruchomiły się po około 4
razy zamiast około 70, zawsze obie w odstępie 1–2 minut. Wniosek: pole
`timezone` działa; GitHub uruchamia harmonogramy w tym repozytorium
nieregularnie, pomijając lub opóźniając większość startów (dokumentacja
GitHuba dopuszcza opóźnienia i pominięcia przy dużym obciążeniu).

W `.github/workflows/daily-digest.yml` harmonogram ma teraz cztery
próby: `17 6-9 * * 1-6` (6:17, 7:17, 8:17 i 9:17 czasu polskiego, od
poniedziałku do soboty). Nowy moduł `src/run_guard.py` zapisuje po
każdym zakończonym uruchomieniu znacznik `data/last_digest.json` (data,
sposób uruchomienia, liczba wysłanych artykułów) – także wtedy, gdy nie
było czego wysłać, ale nie po nieudanej wysyłce. Zaplanowane
uruchomienie kończy się bez wysyłki, jeśli dzisiejsza prasówka już się
odbyła; uruchomienie ręczne nigdy nie jest blokowane i również „zalicza
dzień”. `src/main.py` sprawdza strażnika na początku i zapisuje znacznik
na końcu. Usunięto obie sondy (`schedule-probe-utc.yml`,
`schedule-probe-tz.yml`).

Zmianę zweryfikowano: testy jednostkowe (158) zakończone powodzeniem.
Ręczne uruchomienie na gałęzi `v19-harmonogram` (20.10.2026, 11:16):
2 artykuły spośród 82, streszczenia 2 z 2 (`gpt-oss-120b`), prasówka
dotarła na Discord, a workflow zapisał znacznik
`{"date": "2026-10-20", "trigger": "workflow_dispatch", "articles": 2}`.

**Ograniczenia:** blokadę zaplanowanego uruchomienia da się sprawdzić
wyłącznie na `main` (harmonogram nie działa na innych gałęziach) –
zostanie potwierdzona w kolejnych dniach i opisana w tym wpisie. Jeśli
wszystkie cztery próby przepadną, prasówki trzeba uruchomić ręcznie.
Jeśli pierwsza próba nie znajdzie artykułów, kolejne tego dnia też nic
nie wyślą. Miesięczne top 10 (v17) ma ten sam problem z harmonogramem i
wymaga analogicznego zabezpieczenia przed 1.11.2026.

## v18 --- 19.10.2026

**Streszczenia AI po polsku z obowiązkowym słowniczkiem zgodnym z
glosariuszem CyberSec Mozaika.**

Nowy moduł `src/ai_summaries.py`: każdy artykuł w prasówce dostaje
streszczenie po polsku (do 2 zdań), także artykuły z polskich serwisów.
Model: `openai/gpt-oss-120b` w Groq (darmowy plan), a gdy zawiedzie –
`qwen/qwen3.8-27b` w Groq (ten sam klucz, osobny limit); gdy oba
zawiodą, prasówka idzie bez streszczeń. Artykuły trafiają do AI paczkami
po 5; przy przekroczeniu limitu (429) kod czeka i ponawia. Materiałem
jest pełny tekst z kanału, jeśli kanał go podaje (Niebezpiecznik, Z3S),
a w pozostałych przypadkach opis z RSS (do 1500 znaków); stron
artykułów nie pobieramy. Pełny tekst służy tylko do streszczeń, nie
wpływa na selekcję. Treść z kanałów jest dla AI danymi, nie poleceniami;
streszczenia są czyszczone (jedna linia, bez linków, formatowania i „@”).
Klucz `GROQ_API_KEY` trafia tylko do kroku uruchamiającego prasówkę; bez
niego prasówka działa jak dotąd. Limit czasu zadania: 20 minut.

Słowniczek: nowy plik `data/glosariusz_mirror.csv` – samodzielny mirror
glosariusza CyberSec Mozaika (matka v83, 726 haseł); prasówka nie
korzysta z samej matki. Mirror generuje ręcznie uruchamiany skrypt
`tools/eksport_mirrora.py`, który przechowuje też decyzje prasówki
(forma w tekście, objaśnienie w nawiasie, uwaga dla AI, formy zakazane).
Zasada (decyzja z 19.10.2026): termin angielski pierwszy, gdy tak mówi
branża, a polski odpowiednik w nawiasie – jak w matce od v32; wyjątek:
„podwyższenie (eskalacja) uprawnień”. Moduł `src/glossary.py` wymusza
słowniczek w trzech miejscach: (1) polecenie dla AI („SŁOWNICZEK JEST
OBOWIĄZKOWY”) z 21 stałymi konwencjami i maks. 40 hasłami występującymi
w streszczanych artykułach; (2) kontrola form zakazanych (np.
„eskalacja uprawnień”, „eksploit”, „łatka”, „aktor zagrożeń”) –
streszczenie z błędem wraca raz do AI z uwagą, a jeśli nadal jest
błędne, zostaje odrzucone; (3) objaśnienia w nawiasach dopisuje kod, nie
AI, tylko przy pierwszym wystąpieniu terminu w całej prasówce, w zgodzie
z przypadkiem (formy z Morfeusza 2, np. „poprawce (łatce)”,
„podwyższenie (eskalację) uprawnień”).

W `src/discord_output.py` streszczenie stoi pod tytułem jako cytat
(nigdy nie oddziela się od tytułu przy dzieleniu wiadomości), a na końcu
prasówki jest dopisek, że streszczenia przygotowało AI. Nagłówek sekcji
nie zostaje już sam na końcu wiadomości. `src/deduplication.py` i
`src/main.py` przekazują pełną treść z kanału.

Zmianę zweryfikowano: testy jednostkowe (151) zakończone powodzeniem.
Pierwsze uruchomienie na gałęzi `v18-streszczenia-ai` nie wybrało
żadnego artykułu (brak nowych powyżej progu), więc AI nie zostało
wywołane. Drugie uruchomienie (19.10.2026, 23:09): 6 artykułów spośród
85, streszczenia 6 z 6 przygotował `gpt-oss-120b` za pierwszym
podejściem (bez naruszeń słowniczka); prasówka dotarła na Discord (2
wiadomości). Na tej podstawie poprawiono trzy rzeczy przed scaleniem:
w poleceniu dla AI terminy angielskie bez nawiasów (model przepisał
dosłownie „exploit (kit)”) i prośba o odmianę terminów; brak
zagnieżdżonych objaśnień („(RCE (zdalne wykonanie kodu))”); nagłówek
sekcji przenoszony do kolejnej wiadomości.

**Ograniczenia:** streszczenia z krótkich zajawek (BleepingComputer)
mają często 1 zdanie; przeglądy tygodniowe dają ogólnikowe streszczenia.
Kod objaśnia przy pierwszym użyciu każdy angielski termin z mirrora
(np. „API (interfejs programowania aplikacji)”), co może zagęścić
nawiasy. Jakość i poprawki po teście ocenimy w kolejnych prasówkach.
Mirror trzeba odświeżyć po każdej zmianie nazw w matce. Awaria całego
Groq oznacza prasówkę bez streszczeń (zapasowy dostawca odłożony).

## v17 --- 19.10.2026

**Miesięczne zestawienie 10 najważniejszych wydarzeń na osobnym kanale
Discorda.**

Dodano moduł `src/monthly_top.py` i workflow
`.github/workflows/monthly-top.yml`. Pierwszego dnia miesiąca o 8:17
czasu polskiego (`Europe/Warsaw`) archiwum poprzedniego miesiąca jest
grupowane w wydarzenia tym samym mechanizmem co w v16, ale w skali
całego miesiąca; łączone są także kolejne artykuły z tego samego serwisu
(np. aktualizacje), pod warunkiem wspólnej nazwy lub numeru CVE.
Wydarzenia są szeregowane według liczby artykułów, następnie liczby
serwisów i najwyższej punktacji, a 10 pierwszych trafia na kanał
`#top-miesiąca` przez sekret `DISCORD_MONTHLY_WEBHOOK_URL`. Każda
pozycja podaje liczbę artykułów i serwisów (z polską odmianą) oraz dzień
pierwszego wystąpienia; niepełny miesiąc jest oznaczany w nagłówku.
Miesiąc można podać ręcznie (`RRRR-MM`); wartość jest sprawdzana wzorcem
przed odczytem plików. Workflow ma wyłącznie uprawnienie odczytu
repozytorium.

W `src/event_grouping.py` nazwy muszą różnić się co najwyżej końcówką do
3 liter (nazwa „Medyc” nie łączy się już z przymiotnikiem „medycznej”),
a próg rzadkości słowa może rosnąć wraz z wielkością wydarzenia
(potrzebne w skali miesiąca, gdzie nazwa występuje we wszystkich
artykułach o wydarzeniu). Dodano testy (107 łącznie), m.in. dla łączenia
aktualizacji, rankingu, odmiany, niepełnego miesiąca i nieprawidłowego
miesiąca.

Zmianę zweryfikowano: testy jednostkowe (107) zakończone powodzeniem;
symulacja na archiwum z prawdziwymi tytułami wykazała dwa błędne
połączenia (dwa różne artykuły Sekuraka o wspólnych pospolitych słowach
oraz „Medyc”/„medycznej”), które usunięto przed wdrożeniem. Po scaleniu
ręczne uruchomienie workflow na gałęzi `main` (19.10.2026) zakończyło
się powodzeniem: na kanał `#top-miesiąca` dotarło zestawienie „📅 Top 10
· październik 2026” z oznaczeniem niepełnego miesiąca (archiwum od
19.10) i jedną pozycją (OpenCode Console Breach…, 1 artykuł, 1 serwis).

**Ograniczenia:** ręczne uruchomienie workflow jest możliwe dopiero po
scaleniu do `main`, bo GitHub pokazuje przycisk uruchamiania tylko dla
workflow istniejących na gałęzi domyślnej. Harmonogram korzysta z pola `timezone`, którego działanie jest
wyjaśniane (zob. v14). Ranking opiera się na liczbie artykułów, więc
wydarzenia opisywane przez wiele serwisów mają przewagę nad
pojedynczymi, choć ważnymi analizami.

## v16 --- 19.10.2026

**Wykrywanie tego samego wydarzenia opisanego przez różne serwisy i
sekcja „Ciąg dalszy”.**

Dodano moduł `src/event_grouping.py`. Artykuły z różnych serwisów o tym
samym wydarzeniu są łączone w jedną pozycję prasówki z dopiskiem
„także:” i linkami do pozostałych źródeł. O połączeniu decydują: wspólny
numer CVE, co najmniej dwa wspólne rzadkie słowa tytułu albo jedna
wspólna nazwa, która nie występuje w innych tytułach dnia (wyraz z
wielką literą w środku, jak „BeyondTrust”, albo pisany wielką literą w
środku tytułu zdaniowego, jak „Fakturownia.pl”). Słowa porównywane są po
pięcioliterowych rdzeniach, a ogólne słownictwo newsów i bezpieczeństwa
jest pomijane. Artykuły z tego samego serwisu nie są łączone. Grupę
reprezentuje artykuł z najwyższą punktacją, przy remisie ze źródła
polskiego; gdy jego serwis wyczerpał limit, grupę reprezentuje inny
artykuł z grupy. Artykuły o wydarzeniach dostarczonych w ciągu ostatnich
3 dni (według archiwum z v15) trafiają do osobnej sekcji „🔁 Ciąg
dalszy”.

Linki wszystkich artykułów z grupy są zapisywane w `published_links`, a
archiwum przechowuje źródła powiązane i znacznik ciągu dalszego. W logu
dodano liczbę połączonych powtórzeń i artykułów z ciągu dalszego. Zmiany
objęły `src/main.py`, `src/article_selection.py`,
`src/article_archive.py` i `src/discord_output.py`; dodano testy oparte
na prawdziwych parach tytułów (94 łącznie). Zmiana trafiła na gałąź
`main` bezpośrednio, bez pull requesta, wskutek wgrania plików na
niewłaściwą gałąź.

Zmianę zweryfikowano: testy jednostkowe (94) zakończone powodzeniem; na
7 prawdziwych parach „to samo wydarzenie” wykryto 6, na 13 parach „różne
wydarzenia” nie było błędnych połączeń; symulacja na 68 prawdziwych
tytułach połączyła m.in. Cisco, BeyondTrust, Palo Alto, ataki na sklepy
we Francji i Fakturownię oraz oznaczyła kontynuację z archiwum.
Uruchomienia na żywo (na `main` i na gałęzi `v17-top-miesiaca`)
zakończyły się powodzeniem; nie wystąpiły w nich jeszcze artykuły do
połączenia.

**Ograniczenia:** reguły przedkładają precyzję nad kompletność: część
powtórzeń zostanie pominięta, np. gdy nazwa stoi na początku obu
tytułów, a jeden z nich jest pisany wielkimi literami w każdym słowie
(para o Drupalu). Porównywane są wyłącznie tytuły. Grupowanie nie
działało jeszcze na prawdziwej porannej prasówce z wieloma artykułami.

## v15 --- 18.10.2026

**Miesięczne archiwum dostarczonych artykułów i odporniejszy zapis
danych.**

Dodano moduł `src/article_archive.py`, który zapisuje każdy artykuł
dostarczony na Discord w miesięcznym pliku `data/archive/RRRR-MM.json`:
datę prasówki (czas polski), tytuł, link, źródło, kategorie i punkty.
Ten sam link nie jest zapisywany dwukrotnie, a polskie znaki są
zapisywane czytelnie. Archiwum jest podstawą planowanego miesięcznego
zestawienia 10 najważniejszych artykułów i późniejszej integracji z
Mozaiką. Funkcja `run()` w `src/main.py` archiwizuje wybrane artykuły
zaraz po udanej wysyłce. Błąd archiwum jest zapisywany w logu, historia
artykułów zostaje mimo to zapisana, a uruchomienie kończy się błędem,
więc dostarczone linki nie są wysyłane ponownie.

W workflow krok zapisu danych dodaje teraz cały folder `data` przed
sprawdzeniem zmian, dzięki czemu nowe pliki archiwum są zapisywane w
repozytorium (wcześniej sprawdzano tylko `data/seen_articles.json`, a
nowe pliki zostałyby utracone). Krok ten wykonuje się także wtedy, gdy
krok prasówki zakończy się błędem (`if: ${{ !cancelled() }}`), więc
linki dostarczone przed awarią są zawsze zapisywane. Dodano 9 testów
archiwum. Zaktualizowano README (PL i EN), w tym listę planowanych
funkcji o wykrywanie powtórzonych wydarzeń i miesięczne zestawienie top
10.

Zmianę zweryfikowano: testy jednostkowe (78) zakończone powodzeniem;
symulacja pełnego uruchomienia utworzyła plik archiwum z 20
dostarczonymi artykułami, a symulacja z celowo uszkodzonym plikiem
archiwum potwierdziła zapis historii i zakończenie uruchomienia błędem.
Ręczne uruchomienie na gałęzi `v15-archiwum` zakończyło się powodzeniem,
ale nie wybrało żadnego artykułu (76 dostępnych, 1 promocja, 75 poniżej
progu), więc potwierdziło jedynie poprawne działanie kroku zapisu przy
braku zmian.

**Potwierdzenie (19.10.2026):** pierwsze uruchomienie dostarczające
artykuł (ręczne, na gałęzi `v17-top-miesiaca`) utworzyło plik
`data/archive/2026-10.json` z poprawnym wpisem, a krok zapisu
zatwierdził go w repozytorium razem z historią. **Ograniczenia:**
archiwum obejmuje artykuły od dnia wdrożenia, więc za październik 2026
jest niepełne. Data w archiwum to data prasówki, a nie data publikacji
artykułu.

## v14 --- 18.10.2026

**Automatyczny harmonogram prasówki: 6:17 czasu polskiego, od
poniedziałku do soboty.**

W pliku `.github/workflows/daily-digest.yml` dodano wyzwalacz `schedule`
z wyrażeniem cron `17 6 * * 1-6` i strefą czasową `Europe/Warsaw`.
Prasówka uruchamia się automatycznie od poniedziałku do soboty (bez
niedziel), a dzięki polu `timezone` godzina pozostaje stała także po
zmianie czasu. Start o 6:17, a nie o pełnej godzinie, ogranicza ryzyko
opóźnień w okresach największego obciążenia GitHub Actions. Zachowano
możliwość ręcznego uruchamiania (`workflow_dispatch`). Dodano grupę
współbieżności `daily-digest` (`cancel-in-progress: false`):
uruchomienie ręczne i zaplanowane nie mogą działać równocześnie, więc te
same artykuły nie zostaną wysłane dwukrotnie przed zapisaniem ich w
`published_links`. Kod Pythona nie uległ zmianie. Zaktualizowano README
(PL i EN).

Zmianę zweryfikowano: GitHub zaakceptował nowy plik workflow, a ręczne
uruchomienie na gałęzi `v14-harmonogram` zakończyło się powodzeniem:
wszystkie 6 kanałów pobrano bez błędów (150 wpisów), 71 artykułów
opublikowanych wcześniej pominięto, a spośród 79 dostępnych do selekcji
wybrano 3, odrzucając 1 jako promocję i 75 jako poniżej progu trafności.
Prasówka dotarła na Discord.

**Ograniczenia:** harmonogram działa wyłącznie z gałęzi `main`, więc
pierwsze automatyczne uruchomienie (planowane na 19.10.2026) przyszło
o 11:54 zamiast o 6:17, a 20.10 nie przyszło wcale – diagnoza i
poprawka: v19. GitHub nie gwarantuje
dokładnej godziny startu zaplanowanych uruchomień; w okresach dużego
obciążenia mogą one zostać opóźnione lub pominięte.

## v13 --- 17.10.2026

**Poprawa jakości selekcji: polskie słowa kluczowe, próg trafności,
limity źródeł i filtr promocji.**

Przebudowano moduł `src/article_selection.py`. Słowa kluczowe są
zapisywane jako rdzenie wyrazów dopasowywane od początku słowa (np.
`wyciek` obejmuje „wycieku” i „wyciekiem”), a znak `$` oznacza
dopasowanie całego wyrazu (np. `luk$` nie obejmuje słowa „lukratywny”).
Dodano polskie słowa kluczowe dla kategorii najważniejszych wiadomości
(m.in. wyciek, kradzież danych, zhakowany/zhackowany, włamanie, haker,
krytyczna podatność) i podatności (m.in. podatność, luka, łatka,
poprawki bezpieczeństwa, zdalne wykonanie kodu) oraz rozszerzono słowa
związane z Polską. Polskie rdzenie sprawdzono z pełnymi paradygmatami
odmiany wygenerowanymi przez analizator morfologiczny Morfeusz 2;
uzupełniono formy z oboczności (np. „luce”, „łatce”, „poprawek”,
„hakerzy”, „włamali”). Słowa „cyberatak” i „incydent” są uwzględniane
tylko w tytułach.

Do prasówki trafiają wyłącznie artykuły z wynikiem co najmniej 2, czyli
z kategorii najważniejszych wiadomości lub podatności; samo powiązanie z
Polską (+1) podnosi pozycję, ale nie wystarcza do wyboru, a prasówka nie
jest już uzupełniana do 20 pozycji. Każde źródło może dostarczyć
najwyżej 4 artykuły, a Niebezpiecznik najwyżej 2. Tytuły promocyjne
(webinary, bezpłatne szkolenia, e-booki, rabaty, treści sponsorowane,
wykłady, zapisy) są wykluczane. Tytuły w kontekście wydarzeń, raportów
lub poradników (m.in. konferencje, eksperci, „wzrost”, „odporność”,
poradniki, kary regulacyjne) tracą 2 punkty, więc wchodzą do prasówki
tylko przy silnych sygnałach bezpieczeństwa. „Weekendowa lektura” i inne
przeglądy tygodniowe nie są wykluczane. W logu `src/main.py` dodano
liczbę artykułów odrzuconych jako promocja i poniżej progu trafności.
Zaktualizowano testy (24 nowe, oparte na prawdziwych tytułach z
wcześniejszych prasówek) oraz README (PL i EN).

Zmianę zweryfikowano: testy jednostkowe (69) zakończone powodzeniem;
symulacja na 58 tytułach z wcześniejszych prasówek wybrała 14 artykułów,
odrzucając m.in. wypełniacze bez związku z bezpieczeństwem, zapowiedź
wykładu i bezpłatnego szkolenia oraz relacje z konferencji. Pierwsze
uruchomienie workflow na gałęzi `v13-selekcja` wybrało 20 artykułów
spośród 105, w tym 13 ze źródeł polskich (wcześniej 2 z 20), bez
przekroczenia limitów źródeł. Drugie uruchomienie, po dodaniu kontekstów
„odporność” i „fined”, wybrało 8 artykułów spośród 85: 1 odrzucono jako
promocję, a 76 znalazło się poniżej progu trafności. `published_links`
zawiera 88 linków. Rozwiązano ograniczenia opisane w v12 dotyczące
przewagi źródeł anglojęzycznych, polskich incydentów w „Pozostałych”,
zbyt szerokiego słowa „polski”, braku filtra promocji i uzupełniania
prasówki do 20 pozycji.

**Ograniczenia:** te same wydarzenia opisane przez różne serwisy nadal
pojawiają się wielokrotnie (np. Fakturownia w Niebezpieczniku i Zaufanej
Trzeciej Stronie); wykrywanie powtórzonych wydarzeń zaplanowano jako
osobną zmianę. Ocena opiera się na słowach kluczowych i nie rozumie
treści: artykuł o incydencie bez słów kluczowych w tytule lub opisie
zostanie pominięty, a kara za kontekst może obniżyć wartościową relację
z konferencji. Przeglądy tygodniowe są oceniane jako jeden artykuł.
Ostrzeżenie z v12 o możliwej ponownej wysyłce po częściowo nieudanej
wysyłce pozostaje aktualne.

## v12 --- 15.10.2026

**Dostarczanie prasówki na Discorda (bez AI) i zapis opublikowanych
linków.**

Dodano moduł `src/discord_output.py`, który grupuje wybrane artykuły
według najważniejszej kategorii (kolejność ważności wynika ze słownika
`CATEGORIES` w `src/article_selection.py`, więc nowe kategorie są
obsługiwane automatycznie), formatuje je jako numerowane, klikalne
tytuły z domeną źródła i bez podglądów stron, dzieli prasówkę na
wiadomości mieszczące się w limicie długości Discorda i wysyła je na
webhook. Liczebniki są odmieniane zgodnie z polską gramatyką. Wzmianki
typu `@everyone` z tytułów zewnętrznych artykułów są wyłączone. Gdy
sekcja przechodzi do kolejnej wiadomości, jej nagłówek jest powtarzany z
dopiskiem „(cd.)”; limit wiadomości ustawiono na 1900 znaków jako
margines bezpieczeństwa.

Funkcja `run()` w `src/main.py` buduje prasówkę z wybranych artykułów i
wysyła ją na adres ze zmiennej środowiskowej `DISCORD_WEBHOOK_URL`.
Linki trafiają do `published_links` dopiero po udanej wysyłce. Brak
zmiennej pomija wysyłkę bez błędu, a błąd wysyłki kończy uruchomienie
błędem, dzięki czemu workflow jest oznaczany jako nieudany. Workflow
przekazuje sekret repozytorium `DISCORD_WEBHOOK_URL` wyłącznie do kroku
uruchamiającego prasówkę. Usunięto ograniczenie opisane w v11: licznik
„Artykuły widziane wcześniej” zastąpiono licznikiem „Artykuły
opublikowane wcześniej (pominięte)”.

Dodano funkcję `clean_title()` w `src/rss_helpers.py`, dekodującą encje
HTML w tytułach (np. `&#8230;`, `&#x1f4cc;`), które niektóre kanały, w
tym Niebezpiecznik, kodują podwójnie. Dodano 15 testów jednostkowych
(`src/test_discord_output.py` oraz testy `clean_title()`); testy nie
łączą się z Discordem. Zaktualizowano README (PL i EN), w tym
uzupełniono w README_PL ucięte zakończenie listy planowanych funkcji.

Zmianę zweryfikowano: testy jednostkowe (45) zakończone powodzeniem;
trzy ręczne uruchomienia workflow na gałęzi `v12-discord-from-main`
dostarczyły na prywatny kanał Discorda prasówki po 20 artykułów. Kolejne
uruchomienia pomijały artykuły opublikowane wcześniej: do selekcji
dostępnych było 150, 130 i 110 artykułów, a `published_links` zawiera 60
linków. Potwierdzono powtarzanie nagłówka „(cd.)” w kolejnych
wiadomościach.

**Ograniczenia:** selekcja opiera się na angielskich słowach kluczowych,
więc w pierwszym uruchomieniu 18 z 20 artykułów pochodziło ze źródeł
anglojęzycznych, a polskie artykuły o incydentach (np. wycieki danych)
trafiały do „Pozostałych”. Słowo „polski” bywa zbyt szerokim sygnałem, a
treści promocyjne (webinary, podsumowania tygodnia) nie są filtrowane.
Prasówka jest zawsze uzupełniana do 20 pozycji, także artykułami o
niskiej trafności. Te same wydarzenia opisane przez różne serwisy
pojawiają się wielokrotnie, ponieważ deduplikacja działa po linkach.
Jeśli wysyłka nie powiedzie się po dostarczeniu części wiadomości, linki
nie zostaną oznaczone jako opublikowane i mogą zostać wysłane ponownie.

## v11 --- 15.10.2026

**Wydzielenie głównego przepływu do funkcji `run()` i potwierdzenie
pełnego przebiegu etapu 3.**

W pliku `src/main.py` kod wykonywany dotąd na poziomie modułu
(pobieranie RSS, kategoryzacja, selekcja TOP 20, aktualizacja historii)
przeniesiono do funkcji `run()`, wywoływanej wyłącznie w bloku
`if __name__ == "__main__":`. Logika przetwarzania nie uległa zmianie:
poza zmianą wcięć diff obejmuje trzy dodane linie. Import `main.py`
przez inny moduł nie pobiera już feedów ani nie nadpisuje
`data/seen_articles.json`, co pozwala dołączać kolejne moduły (np.
dostarczanie na Discorda lub integrację z glosariuszem) bez efektów
ubocznych.

Zmianę zweryfikowano: testy jednostkowe (30) zakończone powodzeniem;
ręczne uruchomienie workflow na gałęzi `refactor-main` zakończone
sukcesem: 6 feedów bez błędów, 150 wpisów, 150 unikalnych artykułów,
0 nieprawidłowych wpisów, 150 artykułów dostępnych do selekcji, 20
wybranych do digestu. Historia wzrosła do 250 linków w `seen_links`;
`published_links` pozostaje puste. Potwierdzono, że podsumowanie RSS i
statystyki selekcji są wypisywane w logu. Ich wcześniejszy brak
najprawdopodobniej wynikał z tego, że wyszukiwarka logów GitHub Actions
przeszukuje tylko rozwinięte kroki, a nie z błędu programu.

W README (PL i EN) usunięto zastrzeżenie, że działanie selekcji wymaga
potwierdzenia, a sekcję ostatnich zweryfikowanych wyników zastąpiono
wynikami tego uruchomienia, z odesłaniem do changelogu. W nagłówku
changelogu zaznaczono, że od v11 wpisy są dodawane na bieżąco, razem ze
zmianą, a nie odtwarzane z historii Git.

**Ograniczenie:** licznik „Artykuły widziane wcześniej” liczy w
rzeczywistości artykuły wcześniej opublikowane (`published_links`), a
nie wcześniej wykryte (`seen_links`); przy pustej liście publikacji
pokazuje 0. Do poprawy przy wdrażaniu publikowania.

## v10 --- 11.10.2026

**Rozdzielenie historii wykrytych i opublikowanych artykułów oraz
filtrowanie artykułów wcześniej opublikowanych.**

Rozszerzono strukturę `data/seen_articles.json` o `published_links`,
oddzielając ją od `seen_links`. Dodano ładowanie i zapisywanie
opublikowanych linków, testy nowej struktury oraz funkcję
`filter_unpublished_articles()`. Filtrowanie zintegrowano z przepływem
RSS, a komunikaty historii uporządkowano tak, by rozróżniały linki
wcześniej wykryte od linków oznaczonych jako opublikowane.
Zaktualizowano również dokumentację angielską i polską, aby
odzwierciedlała bieżącą implementację.

Zmiana przygotowuje przepływ do oddzielenia pobierania artykułu od jego
publikacji. **Ograniczenie:** w przeanalizowanej historii nie
potwierdzono integracji z Discordem ani kompletnego procesu, który po
udanej publikacji automatycznie dopisuje link do `published_links`. Sam
filtr nie oznacza, że publikowanie zostało wdrożone.

## v9 --- 11.10.2026

**Wybór TOP 20 artykułów według priorytetu.**

Dodano funkcję wyboru artykułów z najwyższą punktacją, z domyślnym
limitem 20 pozycji. Funkcję zaimportowano do głównego przepływu i
zintegrowano z przetwarzaniem RSS. Dodano testy wyboru najlepszych
artykułów oraz przypadków granicznych. Mechanizm wykorzystuje kategorie
i punktację modułu selekcji wprowadzonego wcześniej.

To etap wyboru kandydatów do dalszego wykorzystania, a nie mechanizm
publikacji. **Ograniczenie:** nie potwierdzono generowania streszczeń
przez AI ani wysyłania wybranych artykułów do Discorda.

## v8 --- 10.10.2026

**Regułowa kategoryzacja artykułów i punktacja priorytetów.**

Dodano moduł `src/article_selection.py`, który rozpoznaje tematy na
podstawie reguł i słów kluczowych, w tym informacje krytyczne z obszaru
cyberbezpieczeństwa, podatności oraz tematykę związaną z Polską.
Zastosowano punktację: +3 dla kategorii krytycznej, +2 dla podatności i
+1 dla tematów polskich. Dodano testy modułu, podłączono go do głównego
skryptu i wprowadzono logowanie kategorii oraz wyników.

Jest to selekcja oparta na jawnych regułach, a nie klasyfikacja
wykonywana przez model AI. W kolejnym etapie dodano wybór TOP 20. Wpis
nie oznacza wdrożenia streszczania ani publikowania.

## v7 --- 10.10.2026

**Trwała historia linków między uruchomieniami GitHub Actions.**

Dodano plik `data/seen_articles.json` i moduł `src/article_history.py`
do odczytu oraz zapisu historii artykułów w JSON. Wprowadzono testy
historii, obsługę brakującego pliku, kontrolę struktury danych i
zachowywanie kolejności unikalnych linków. Główny przepływ RSS zaczął
ładować wcześniej zapisane linki, pomijać wcześniej widziane artykuły i
raportować ich liczbę osobno od duplikatów znalezionych w bieżącym
uruchomieniu.

Po przetworzeniu nowe linki są zapisywane w historii. Workflow otrzymał
uprawnienie `contents: write` i krok utrwalający zmieniony plik historii
w repozytorium. Dodano także diagnostykę odczytu historii.

Rozwiązanie pozwala pamiętać linki między uruchomieniami workflow. Nie
przechowuje pełnych treści artykułów ani nie gwarantuje, że artykuł
pozostanie dostępny w źródłowym kanale RSS.

## v6 --- 10.10.2026

**Walidacja wpisów RSS, opisy artykułów i dokładniejsze podsumowanie
przetwarzania.**

Rozszerzono walidację artykułów: odrzucane są wpisy bez prawidłowego
tytułu lub linku, a adresy są sprawdzane pod kątem obsługiwanego
schematu HTTP/HTTPS i hosta. Dodano liczniki elementów pobranych,
nieprawidłowych wpisów i duplikatów oraz zbiorcze podsumowanie wyników.
Doprecyzowano liczenie tak, aby wpisy odrzucone podczas walidacji nie
były zaliczane jako duplikaty.

Wyodrębniono `is_valid_url()` i `is_duplicate_link()` do
`src/rss_helpers.py` oraz dodano testy jednostkowe. Parser zaczął
pobierać opisy z RSS `description` i Atom `summary`, a rekordy artykułów
rozszerzono o pole opisu. Poprawiono też błędy wcięć w kodzie
przetwarzającym RSS i składnię testów.

Zmiany poprawiły diagnostykę i testowalność. Nie gwarantują jednak
kompletności ani poprawności danych dostarczanych przez zewnętrzne
kanały.

## v5 --- 10.10.2026

**Wydzielenie deduplikacji do osobnego modułu i uruchamianie testów w
CI.**

Logikę deduplikacji przeniesiono z głównego skryptu do
`src/deduplication.py`, udostępniając funkcję `add_article()`. Główny
przepływ RSS korzysta z wydzielonego modułu, a testy sprawdzają
rozpoznawanie duplikatów i dodawanie nowych artykułów. Workflow GitHub
Actions rozszerzono o uruchamianie testów jednostkowych.

Refaktoryzacja ułatwiła niezależne testowanie logiki i jej dalszy
rozwój. Sama zasada deduplikacji po linku powstała we wcześniejszym
etapie.

## v4 --- 09.10.2026

**Pierwsza deduplikacja artykułów i agregowanie informacji o źródłach.**

Dodano mechanizm, który rozpoznaje ten sam artykuł na podstawie linku i
zapobiega dodaniu kolejnego rekordu dla powtarzającego się adresu.
Rekordy rozszerzono o informacje o źródłach, dzięki czemu ten sam link
znaleziony w różnych kanałach może zachować informację o wielu źródłach.
Rozpoczęto wydzielanie tej logiki do osobnego modułu.

Deduplikacja opiera się na linku. Nie oznacza wykrywania treści
identycznych artykułów, które zostały opublikowane pod różnymi adresami
URL.

## v3 --- 08.10.2026

**Obsługa sześciu źródeł oraz formatów RSS i Atom.**

Pobieranie kanału wydzielono do funkcji `fetch_feed(url)`, a
konfigurację rozszerzono do sześciu źródeł: Niebezpiecznik, Sekurak,
Zaufana Trzecia Strona, CyberDefence24, BleepingComputer i The Hacker
News. Parser obsługuje zarówno elementy RSS `item`, jak i wpisy Atom
`entry`, w tym tytuły z przestrzenią nazw oraz linki Atom pobierane z
atrybutu `href`.

Poprawiono obsługę białych znaków przed deklaracją XML. Żądania HTTP
otrzymały nagłówek `User-Agent` i limit czasu 20 sekund. Błąd pobierania
lub parsowania jednego kanału jest obsługiwany oddzielnie, aby program
mógł kontynuować pracę z pozostałymi źródłami. Artykuły są gromadzone na
wspólnej liście; usunięto tymczasowy limit pięciu wpisów na kanał.
Rekord artykułu otrzymał również pole źródła.

Etap zapewnia pobieranie i przetwarzanie wpisów z wielu kanałów. Nie
obejmuje jeszcze generowania streszczeń ani publikowania wyników.

## v2 --- 08.10.2026

**Uruchamianie skryptu i testów przez GitHub Actions.**

Utworzono początkowy workflow `Daily CyberSec Digest`, dodano checkout
repozytorium i uruchamianie skryptu Pythona. Poprawiono strukturę YAML,
w tym położenie `jobs:` na głównym poziomie konfiguracji, aby workflow
miał poprawną strukturę. Dodano początkowy test i podstawowe elementy
konfiguracji repozytorium.

Workflow jest skonfigurowany do ręcznego uruchamiania przez
`workflow_dispatch`. **Ograniczenie:** w przeanalizowanej konfiguracji
nie znaleziono harmonogramu, który uruchamiałby zadanie codziennie
automatycznie.

## v1 --- 08.10.2026

**Początkowy szkielet projektu.**

Utworzono repozytorium projektu, podstawowe pliki i początkowy skrypt
Pythona do pobierania oraz parsowania kanału RSS. Rozpoczęto testowanie
odczytu odpowiedzi XML i dostosowywanie parsera do rzeczywistej
struktury kanałów. Tymczasowe komunikaty diagnostyczne i eksperymentalne
zmiany służące inspekcji pojedynczych źródeł nie zostały opisane jako
osobne funkcje, jeśli później je usunięto.

Był to fundament pod dalsze etapy: obsługę wielu źródeł, walidację,
deduplikację, historię artykułów i selekcję według priorytetu.

------------------------------------------------------------------------

## Stan projektu wynikający z przeanalizowanej historii

-   **Potwierdzone funkcje:** pobieranie i parsowanie RSS/Atom z wielu
    źródeł, walidacja wpisów, deduplikacja po linku, przechowywanie
    źródeł i opisów, trwała historia linków, regułowa kategoryzacja i
    punktacja, wybór do 20 artykułów oraz filtrowanie linków oznaczonych
    jako opublikowane.
-   **Niepotwierdzone jako wdrożone:** streszczanie artykułów przez AI,
    publikowanie na Discordzie oraz automatyczny codzienny harmonogram.
-   `seen_links` i `published_links` pełnią różne role. Obecność filtra
    publikowanych linków nie dowodzi, że zewnętrzna publikacja jest już
    wykonywana ani że `published_links` jest aktualizowane po jej
    sukcesie.

------------------------------------------------------------------------

# Changelog (English)

History of **CyberSec-NewsDigest-AI** --- an automated cybersecurity
news digest that retrieves and processes articles from RSS/Atom feeds.

Newest versions appear first. Versions v1--v10 are documentation labels
for major development stages reconstructed from Git history; they are
not official release tags. Their dates reflect commit author dates in
Git, not local file download times or independently confirmed release
dates. Related commits are grouped into one entry. Purely cosmetic
changes, temporary diagnostics, and experiments later removed have been
omitted.

From v11 onwards, entries are added together with each change, before
it is merged into the `main` branch. One version corresponds to one
logical change; automatic article-history updates made by the workflow
do not receive separate versions. From v24 onwards, small tweaks (e.g.
changing one explanation) do not get their own number: they are
described in the nearest version as a separate paragraph.

Format inspired by [Keep a Changelog](https://keepachangelog.com/).
Sources for v1--v10: Git history (113 commits), commit descriptions,
and reviewed diffs.

------------------------------------------------------------------------

## v29 --- 2026-10-25

**Stricter language check of summaries, protection against the rate
limit, roundups and a more precise 🔥.**

Reason: reading the digests of 23–24 October 2026. Four summaries in
English; calques ("rekordy pacjentów", "AI‑zarządzanego frameworka",
"do intruzji", "eksploatując", "Kompromisy wystąpiły", "rootowy kod");
grammar errors ("Publikuje się natychmiastowa łatka", "nazwanego
łatki", "iPhoneie"); "RCE (RCE)" after the v27 autofix; summaries
restating the title; two articles without a summary because a batch got
429 from both models; roundups (ThreatsDay, In Other News, Weekendowa
lektura) summarized by one topic, and Weekendowa lektura with 🔥; 🔥
on Arista for older CVE ids further down the page; PHP three times
(different titles, same CVE ids).

Changes:

- **Style list `data/styl_unikaj.csv`** (new, edited by JW): calque and
  suggestion, `*` = any ending. The list goes into the prompt and the
  check; a calque goes back for correction but never causes a summary to
  be cut or dropped (a "soft" problem).
- **Language check** (`src/summary_quality.py`): an English summary goes
  back for correction and is dropped if still English (the title alone
  is better than English text); a summary restating the title (at most
  two new words) goes back for correction; "Nie podano…" remarks and a
  bare "w tygodniu" (without dates) are reported like filler and
  relative time words.
- **Proofreading round** (`src/ai_summaries.py`): after all summaries,
  one request to the second model (separate limits): "fix only grammar,
  punctuation, typos and calques, do not change facts". A correction is
  accepted only when it keeps the numbers and CVE ids and the length
  (60–140%) and adds no problems; otherwise the earlier version stays.
  Log: "KOREKTA: …".
- **Rate limit**: requests to one model are spaced out (at least 20 s),
  and a batch that no model handled is retried at the end after 60 s.
- **Autofix**: "zdalne wykonanie kodu (RCE)" gives "RCE" (no "RCE
  (RCE)"), a word repeated in parentheses right after itself is removed,
  "iPhoneie" → "iPhonie".
- **Roundups**: ThreatsDay, Weekly Recap and In Other News are left out
  like promotional content (their stories are in the digest separately;
  the log counter "Odrzucone jako promocja" includes them). "Weekendowa
  lektura" stays (decision of v12), but as a roundup: a fixed
  description instead of an AI summary, no 🔥 and no merging by CVE ids.
- **More precise 🔥 and merging by CVE** (`src/kev.py`,
  `src/event_grouping.py`): only CVE ids from the title and the first
  600 characters of the text count; such a shared id merges articles
  into one event (also from one site).

New and changed files: `data/styl_unikaj.csv` (new),
`src/summary_quality.py`, `src/ai_summaries.py`, `src/glossary.py`,
`src/article_selection.py`, `src/kev.py`, `src/event_grouping.py`,
`src/test_ai_summaries.py`, `src/test_summary_quality.py`,
`src/test_glossary.py`, `src/test_article_selection.py`,
`src/test_kev.py`, `src/test_event_grouping.py`, README (PL/EN).

The change was verified: unit tests (268) passed, including examples
from the digests of 23–24 October 2026. A branch test is pending.
Merging stories by company names in titles (Quest Diagnostics, Capcom)
is left for the next version.

## v28 --- 2026-10-23

**🔥 for vulnerabilities from the CISA KEV catalog.**

CISA's Known Exploited Vulnerabilities catalog lists vulnerabilities
with confirmed exploitation in attacks; 245 entries were added in 2025
(about 4–5 a week). For a SOC analyst this is a "patch first" signal.

- **The marker is set by code, not by the AI** (new `src/kev.py`): the
  catalog (JSON) is downloaded once per run from CISA, or from CISA's
  GitHub mirror when that fails. CVE ids are searched in the title, feed
  text and article page text, also of articles merged into the same
  event. An article with a CVE id from the catalog gets 🔥 before its
  title, and a note "🔥 luka z katalogu CISA KEV – potwierdzone
  wykorzystywanie w atakach" appears below the digest. Without access to
  the catalog the digest is sent without markers (log: "CISA KEV: …").
- **The archive** saves the article's CVE ids (`cves`) and those from the
  catalog (`kev`).
- **The weekly and monthly tops** download the catalog again and check
  the saved CVE ids (and ids in the title and summary), because CISA
  often adds a vulnerability a few days after the first articles. 🔥 and
  the note appear there too.

New and changed files: `src/kev.py` (new), `src/test_kev.py` (new),
`src/main.py`, `src/discord_output.py`, `src/article_archive.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/test_monthly_top.py` and
`src/test_weekly_top.py` (tests do not download the catalog), README
(PL/EN).

The change was verified: unit tests (250) passed. Test on the `v28-kev`
branch on 2026-10-23 (01:34): catalog downloaded from www.cisa.gov (1754
entries), 2 of 20 articles marked (Arista VeloCloud Orchestrator
CVE-2026-114625, BeyondTrust Remote Support CVE-2026-102764), 🔥 note
below the digest; AI summaries 20 of 20 (one correction after a 429 from
both models was saved by the code repair). To watch: remarks in the form
"Nie podano informacji…" / "Nie podano zaleceń" are not detected yet,
and a roundup such as "ThreatsDay" is summarized by one of its many
topics.

## v27 --- 2026-10-22

**Inflection of terms and explanations, and full article text from
pages.**

Reason: the v26 test (2026-10-22) showed "ostrzegają przed exploit (kod
wykorzystujący podatność)": the term not inflected and the explanation
in the nominative. Some feeds (BleepingComputer, The Hacker News, The
Record) give only a one- or two-sentence teaser, so the AI had little
material.

Changes:

- **Explanations in parentheses in the same case as the term**
  (`src/glossary.py`): exploit, botnet and infostealer are inflected
  like Polish nouns, and the explanation follows them: "przed exploitem
  (kodem wykorzystującym podatność)", "członkowie botnetu (sieci
  zainfekowanych urządzeń)", "ochrona przed infostealerami (programami
  kradnącymi dane)". Morfeusz 2 does not know these words, so their
  forms follow Polish model nouns generated with Morfeusz 2 (exploit
  like "kotlet" – exploicie, botnet like "budżet" – botnecie,
  infostealer like "komputer" – infostealerze); the explanations were
  generated with Morfeusz 2 as well. The form "exploita"/"infostealera"
  may be genitive or accusative: the genitive is chosen after a
  preposition (do, od, bez, z…), after negation ("nie wykryto
  exploita"), after "użyć/używać", "szukać", "potrzebować" and after a
  verbal noun ("wykorzystanie exploita"); otherwise the accusative (as
  decided on 2026-10-19 for ambiguous forms). Ransomware is
  indeclinable.
- **Check of uninflected terms** (`src/summary_quality.py`): exploit,
  botnet, infostealer, backdoor, keylogger, rootkit, loader, dropper,
  trojan, phishing in the base form after a preposition or phrase that
  needs another case ("przed exploit", "przy użyciu botnet", "przed
  nowym infostealer") go back to the AI for correction. The prompt
  requires inflection with examples, and the glossary correction request
  says to inflect the required form like the used one ("eksploitem" →
  "exploitem").
- **Full text from the article page** (new `src/article_pages.py`):
  when the feed material is shorter than 600 characters, the article
  page is fetched once (15 s timeout, up to 2 MB, HTML only), and its
  paragraphs (`<p>`) are collected, preferably from inside `<article>`,
  without scripts, menus, footer, sidebars, short paragraphs and typical
  notes (newsletter, cookies, "czytaj też", ads). The page text is data
  like the feed text and is used only as material for the AI and the
  fact check; it is not saved to history or the archive. A page error
  (e.g. 403 from bot protection) leaves the article with its feed
  material. Log: "Pełna treść ze stron: N z M…" and "PEŁNA TREŚĆ: …" on
  errors.

Changed and new files: `src/glossary.py`, `src/summary_quality.py`,
`src/ai_summaries.py`, `src/test_ai_summaries.py`, `src/main.py`,
`src/article_pages.py` (new),
`src/test_article_pages.py` (new), `src/test_glossary.py`,
`src/test_summary_quality.py`, `src/discord_output.py`,
`src/test_discord_output.py`, README (PL/EN).

First test on the `v27-odmiana-strony` branch on 2026-10-22: full text
fetched from 10 of 11 pages (one: connection timeout), including
BleepingComputer, The Hacker News, SecurityWeek, Kapitan Hack, CERT
Polska and Krebs; AI summaries 15 of 15, inflection correct ("przed
exploitem (kodem wykorzystującym podatność)"). Summaries became concrete
(CVE ids, patched versions, numbers from the Interpol operation), but
also too long: one sentence joined with semicolons, two cut at the
450-character limit, plus added recommendations and a remark on what
the report does not say.

Fixes after the test:

- The check (`src/summary_quality.py`) reports summaries longer than 400
  characters, semicolons joining sentences and remarks about missing
  information ("nie podaje informacji o…", "brak informacji o…").
- Prompt: at most 350 characters, short sentences without semicolons, at
  most 3 CVE ids or versions; recommendations only when the article
  lists them; no remarks about what the article does not say.
- The glossary correction request no longer asks to "inflect" acronyms
  (RCE).
- Completion of v26: the files with the "także:" fix
  (`src/discord_output.py`, `src/test_discord_output.py`) did not reach
  the v26 merge, although the v26 changelog describes the fix; the v27
  test still showed "thehackernews.com, thehackernews.com…". The files
  are added in v27.

Second branch test on 2026-10-22: summaries shorter, in sentences with
full stops and not cut, but 8 of 16 articles were left **without a
summary**: the new length and semicolon check reported more summaries,
and a summary that still had a problem after the correction round (or
whose correction failed) was dropped entirely. Also "patchują" in the
Arista summary and "Raport nie podaje sprawcy" in the Pegasus summary.

Fixes after the second test:

- **Repair by code instead of dropping** (`src/ai_summaries.py`,
  `src/summary_quality.py`): when the AI-corrected summary still has a
  problem or the correction request failed (e.g. rate limit), code turns
  semicolons into full stops, removes sentences with problems and cuts
  the text to whole sentences within 400 characters. Only a summary with
  no correct sentence left is dropped. Log: "KONTROLA: streszczenie N
  naprawione przez kod…".
- The check of remarks about missing information also covers
  "raport/artykuł nie podaje…".
- Glossary, a small change: for "łatka" (H166) the anglicisms "patchować"
  ("patchują", "spatchowany") are forbidden too;
  `tools/eksport_mirrora.py` (OVERRIDES H166), `data/glosariusz_mirror.csv`
  (only row H166).

The full log of the second test showed the cause: most correction
requests were for "poprawki" → "łatka", "zdalne wykonanie kodu" → "RCE"
and semicolons, and one correction round got error 429 (rate limit) from
Groq, so five summaries were dropped at once ("brak poprawki"). One was
dropped for the date "21", which was not in the material.

Further fixes:

- **Corrections without an AI request** (`src/glossary.py`, function
  `autofix`, called in `clean_summary`): "poprawka" in every form →
  "łatka" in the same form (poprawce → łatce), "zdalne wykonanie
  (dowolnego) kodu" and "remote code execution" → "RCE" (indeclinable),
  "eksploit…" → "exploit…", semicolon → sentence end. Fewer correction
  requests mean less risk of the rate limit.
- **Second chance when a correction fails**: when the correction request
  to one model fails (e.g. 429), the other Groq model (separate limits)
  is asked, and only then does the code repair run.
- Cutting at the character limit no longer leaves an unfinished
  sentence: the safety limit in `clean_summary` is 1000 characters, and
  the 400-character length is kept by the check and the code repair
  (whole sentences).

The change was verified: unit tests (240) passed. Third branch test on
2026-10-22: full text fetched from 12 of 12 pages, AI summaries **16 of
16**, only one correction request (the remark "Raport nie podaje…",
corrected by the AI), no rate-limit error and no code repair. Summaries
have 1–3 sentences with full stops, no semicolons and no cuts, with CVE
ids, versions and numbers from the article pages; inflection correct
("chroniące przed exploitem (kodem wykorzystującym podatność)"),
"także:" lists each site once. An error to watch: in one summary the
year "2024" from the title ended up in the patch date ("21 października
2024"); the fact check does not catch it, because the number is in the
material.

## v26 --- 2026-10-22

**Five new sources, an article age filter and better merging of the
same event.**

New sources (chosen on 2026-10-22 by publishing frequency and standing
in the industry): **CERT Polska** and **Kapitan Hack** (Polish),
**SecurityWeek** (about 6–7 articles a day, the best coverage of vendor
patches), **The Record** (about 4 a day, journalism: nation-state
attacks, police, policy) and **Krebs on Security** (about 1 a week, own
investigations). Rejected: Help Net Security (many vendor pieces), Dark
Reading (much opinion), Security Affairs and aggregators (reprints).
There are now 11 sources (6 Polish, 5 English).

Code changes:

- **Age filter** (`src/rss_helpers.py`): entries older than 3 days
  (`pubDate` in RSS or `published`/`updated` in Atom) are skipped,
  because feeds of the new sources also contain older articles (Krebs:
  about two months). 3 days cover the Sunday break. Entries without a
  date or with an unreadable date pass. The log shows their number
  ("Pominięte jako starsze niż 3 dni").
- **Source limits** (`src/article_selection.py`): SecurityWeek and The
  Record 3 articles each, so frequent English sources do not push Polish
  ones out of the daily twenty; others unchanged (4, Niebezpiecznik 2).
- **Event merging** (`src/event_grouping.py`): a shared name with
  letters and digits (e.g. PHP2Shell, Plex2Shell, Log4j) merges articles
  like a shared CVE id. Until now the name of a big event appeared in
  many titles of the day, so it was not "rare" and did not merge
  articles (test of 2026-10-22: three separate PHP2Shell items). A
  shared CVE or such a name also merges two articles from one source
  (The Hacker News wrote about PHP2Shell twice). Group names (APT28,
  UNC…, Storm-…) and generic technical names (Win32, x64…) do not merge
  articles, because they appear in different stories. The same rule
  works in the weekly and monthly tops and in the "Ciąg dalszy" section.

Changed and new files: `src/main.py` (source list, age filter, log),
`src/rss_helpers.py`, `src/article_selection.py`,
`src/event_grouping.py`, `src/test_event_grouping.py`,
`src/test_article_age.py` (new), README (PL/EN).

The change was verified: unit tests passed, including titles from
the test of 2026-10-22 (four PHP2Shell articles merge into one item,
Plex2Shell stays separate, two APT28 articles are not merged). Test on
the `v26-zrodla` branch on 2026-10-22: all 11 feeds fetched without
errors (CERT Polska 100 entries, Kapitan Hack 10, SecurityWeek 10, The
Record 5, Krebs 10); 173 entries skipped as older than 3 days; a digest
with 15 articles (about 10 before) from 11 sources, 7 of them Polish; 6
articles merged with others (PHP2Shell: 5 articles from 3 sites in one
item); AI summaries 15 of 15.

Fix after the test: the "także:" note listed the same site several
times ("thehackernews.com, thehackernews.com, securityweek.com,
securityweek.com"). Now each other site is given once (with its first
article), and the site of the main article is not repeated
(`src/discord_output.py`, `src/test_discord_output.py`; tests: 227).

## v25 --- 2026-10-22

**Sharper AI summaries: facts instead of filler, fact and time checks,
correct capitalization.**

Reason: the digest now goes to several people, including mentors, and
summaries from 19–22 October repeated the same errors: filler phrases
("co stanowi poważne zagrożenie…"), "Łatki zostaną udostępnione jutro"
(patches will be released tomorrow) later shown in the weekly top, "98
zero-day" without a noun, "exploit tych luk mogą prowadzić" starting
with a lowercase letter after a glossary correction, "emergency łatki"
and uninflected "podatności (luka)".

Changes:

- **New prompt** (`src/ai_summaries.py`): 2–3 sentences; the first says
  what happened and whom it affects (company, product and version,
  group, CVE), the next ones the scale, impact and what to do, if the
  article says so; no filler and no relative time words; numbers and
  names exactly as in the article; numbers with a noun ("98 luk
  zero-day"); no English words except proper names and glossary terms;
  1 sentence when the material is only a title or a teaser.
- **Quality check** (new `src/summary_quality.py`), in the same
  correction round as the glossary: filler phrases (a phrase list),
  relative time words ("jutro", "dziś", "wczoraj", "w przyszłym
  tygodniu"…, and a weekday without a date, e.g. "w środę"), CVE ids and numbers above 12 that are not in the article
  title or text (the current year and its neighbours are not checked;
  "26 739" and "1,83" are compared with "26,739" and "1.83M"). A summary
  with a problem is sent back once with a description of the problem
  and dropped if it is still wrong (no summary is better than a wrong
  number). The log shows each check as "KONTROLA: …".
- **Capital letter at the start of sentences** fixed by code (except
  after abbreviations: np., m.in., ok., tys., Inc. etc.).
- **Glossary, a small change without its own version:** the AI no
  longer adds "(luka)" after "podatność" (H164); "(luka)" in
  parentheses is forbidden, and "luka" may be used on its own. For RCE
  (H090) the English form "remote code execution" is forbidden too.
  Changes: `tools/eksport_mirrora.py` (OVERRIDES H164 and H090),
  `data/glosariusz_mirror.csv` (only rows H164 and H090).

New and changed files: `src/summary_quality.py`,
`src/test_summary_quality.py`, `src/ai_summaries.py`,
`src/test_ai_summaries.py`, `src/test_glossary.py`,
`tools/eksport_mirrora.py`, `data/glosariusz_mirror.csv`, README (PL/EN).

The change was verified: unit tests (218) passed; the check run on 33
summaries from the October archive caught 7 of them ("jutro", "W
minionym tygodniu", "stanowi poważne zagrożenie dla", 4 × "podatności
(luka)"), and the capitalization fix corrected "exploit tych luk
mogą…". Test on the `v25-streszczenia` branch on 2026-10-22: a digest
with 10 articles on the test channel, AI summaries 10 of 10; the check
reported 4 summaries ("poprawka" instead of "łatka", "zdalnego
wykonania kodu" instead of "RCE"), all corrected in the second round;
the fact check rejected no summary. Summaries give dates, numbers and
names from the articles. After the test, a weekday without a date
("przed wydaniem łatki w środę") and the form "remote code execution"
were added as forbidden.

## v24 --- 2026-10-22

**External alarm clock (cron-job.org) as the main trigger of the digest
and tops; MFA without parentheses.**

Reason: GitHub's schedule is practically unusable in this repository.
Probes on 19–20 October gave about 4 starts out of 70 expected, and on
20–21 October none of the four morning attempts started; digests had to
be run manually.

Solution: cron-job.org calls the GitHub API
(`POST /repos/…/actions/workflows/<file>/dispatches`, body
`{"ref":"main","inputs":{"budzik":"true"}}`) with a fine-grained PAT
(this repository only, Actions: Read and write, valid for one year;
stored only in cron-job.org). Three jobs in the Europe/Warsaw time zone:

- Daily Digest -- Monday to Saturday, 06:17 (`daily-digest.yml`),
- Weekly Top 5 -- Monday, 08:17 (`weekly-top.yml`),
- Monthly Top 10 -- 1st day of the month, 08:17 (`monthly-top.yml`).

GitHub's schedule stays as a backup. So that the alarm clock and the
backup never send the same thing twice, all three workflows have a new
`budzik` input (a checkbox, off by default) and pass a `TRIGGER`
variable (`budzik` or GitHub's event name). The guards
(`src/run_guard.py`, `src/top_guard.py`) treat `budzik` like a scheduled
run: if the day, week or month has already been handled, the run ends
without sending. A manual run (`budzik` unchecked) is still never
blocked. The marker `data/last_digest.json` records `"trigger":
"budzik"`, so it shows what sent the digest.

Also (a small change without its own version): **MFA without
parentheses.** The acronym is widely known ("practically all of us deal
with it"), so code no longer adds "(uwierzytelnianie wieloskładnikowe)"
to it. Explanations in parentheses now cover 6 terms: ransomware,
infostealer, exploit, botnet, podwyższenie (eskalacja) uprawnień and
poświadczenia (dane logowania). The form "MFA" and the ban on the
expanded Polish form in the text remain.

Changed files: `.github/workflows/daily-digest.yml`, `weekly-top.yml`,
`monthly-top.yml` (`budzik` input, `TRIGGER` variable, comments),
`src/run_guard.py`, `src/top_guard.py`, `src/test_run_guard.py`,
`src/test_top_guard.py`, `tools/eksport_mirrora.py` (OVERRIDES H232),
`data/glosariusz_mirror.csv` (only row H232), `src/test_glossary.py`
(explanation tests moved from MFA to botnet; acronym matching tested on
a sample entry), README (PL/EN).

The change was verified: unit tests (203) passed; a test run of the
Weekly Top 5 job in cron-job.org on 2026-10-21 returned 204 and started
the workflow on `main` (successful, nothing sent, because the archive
does not cover the week of 12–18 October). Test on the `v24-budzik`
branch on 2026-10-22: a run without `budzik` delivered a digest (2
articles) to the test channel, and a run with `budzik` checked ended
without sending, with the message "Dzisiejsza prasówka już poszła – ten
zaplanowany start kończy się bez wysyłki." (today's digest has already
been sent). Confirmed on 2026-10-23: the alarm clock started the digest
at 06:17 (`workflow_dispatch` on `main`, successful), the marker
`data/last_digest.json` recorded `"trigger": "budzik"` and 20 articles;
GitHub's schedule started no attempt that morning, so there was nothing
to skip (the skipping itself is confirmed by the branch test). It was
also the first real digest with v28: 2 articles with 🔥 (Arista
VeloCloud Orchestrator, BeyondTrust Remote Support), summaries 20 of 20.

## v23 --- 2026-10-21

**One-time backfill of AI summaries in the archive for articles archived
before v22.**

Reason: the archive started saving summaries only in v22, so 11 articles
from 2026-10-19/20 had no summaries and the weekly and monthly tops showed
titles only for them. An oversight from v17/v18 (tops built from an
archive without summaries).

New module `src/backfill_summaries.py` and a manual workflow
`.github/workflows/backfill-summaries.yml` ("Backfill AI summaries"): for
a chosen archive month it finds records without a summary, looks the
articles up in the current RSS feeds (the same material as the digest:
full text or description), writes summaries with the same AI module and
mandatory glossary, and saves them in the archive. Articles no longer in
the feeds are summarized from the title only (the AI then writes 1
sentence and adds nothing); the log marks them "tylko tytuł". A preview
runs first (`save = false`, result only in the log), then the save
(`save = true`). Records that have a summary are not changed; a run from
a branch saves nothing; nothing goes to Discord. The workflow shares the
concurrency group `daily-digest` with the digest, because both write the
archive.

The change was verified: unit tests (194) passed, including filling only
missing summaries, preview without saving, no saving from a branch, and
material from RSS or from the title.

Preview on `main` (2026-10-21, 00:22): 11 articles without a summary, 9
found in the RSS feeds, 2 no longer (BleepingComputer: F5/NGINX and
Microsoft/Exchange); 10 summaries, but one of them described the missing
material ("Brak dostępnych informacji w treści artykułu.") and for one
the AI returned nothing. Fix before saving: `src/backfill_summaries.py`
gives the AI the title itself as the text when there is no material (the
AI renders it as one Polish sentence), and `src/ai_summaries.py` drops
answers that describe missing material instead of summarizing (starting
with "Brak informacji…" or mentioning the "article text") – this also
applies to the daily digest. Tests: 196.

Housekeeping: in the v23 PR the files `backfill_summaries.py` and
`test_backfill_summaries.py` landed in the repository root instead of
`src`; the correct versions were then added directly on `main` (two
commits without a PR), and the root copies were removed in the fix.

Second preview (2026-10-21, 00:32): 11 of 11 summaries; 8 correct, 3
wrong: for a title-only article (Microsoft/Exchange) the AI added an
unsupported second sentence ("Microsoft zaleca zastosowanie
poprawek…"), for OpenCode "distillation attacks" became "attacks on AI
distillation processes" (they are attacks that use distillation, i.e.
copying a model), and for Plex2Shell the PoC was attributed to the
attackers instead of researchers; two summaries used "poprawka" instead
of the agreed "łatka". Second fix: for title-only articles only the
first sentence of the summary is saved (`src/backfill_summaries.py`),
and "poprawka" was added to the forbidden forms of entry H166
(`tools/eksport_mirrora.py`, `data/glosariusz_mirror.csv`), so the
glossary check enforces "łatka" – also in the daily digest.
Interpretation errors (OpenCode, Plex2Shell) are corrected manually in
the archive after saving. Tests: 198.

Save on `main` (2026-10-21, 00:42, commit "Backfill AI summaries in
archive"): 11 of 11 summaries in the archive; the title-only
Microsoft/Exchange article has one sentence, "łatki" instead of
"poprawki", and the OpenCode and Plex2Shell errors from the second
preview did not recur. Manual correction of 2 summaries in
`data/archive/2026-10.json` (editing, no change of facts): F5
("out-of-band łatki" → "pozacykliczne łatki") and the "government office"
scam (unsupported "co umożliwiło szybkie podjęcie działań obronnych"
removed); two other proposed corrections (OpenCode Console, THN weekly
recap) were rejected. The preview of the weekly top for
2026-10-19/25 shows summaries for all items. The backfill workflow stays
in the repository as a tool for the future (e.g. after an AI outage).

**Limitations:** the workflow can be run only after merging (GitHub shows
the run button only for workflows on `main`), hence the preview before
saving. Title-only summaries are poorer. The tool is one-time; after the
backfill the workflow can be removed.

## v22 --- 2026-10-20

**Weekly top 5, one-time sending of weekly and monthly tops, and AI
summaries in the tops.**

New module `src/weekly_top.py`: on Mondays the top 5 events of the
previous week (Monday–Sunday) go to a new Discord channel `#top-tygodnia`
(secret `DISCORD_WEEKLY_WEBHOOK_URL`). Grouping and ranking are the same
as in the monthly top (articles, sources, score); a week spanning two
months reads both archive files. New workflow
`.github/workflows/weekly-top.yml`: attempts at 08:17, 09:17, 10:17 and
11:17 Polish time; a manual run accepts any date in the chosen week.

Safeguard against the unreliable schedule (as in v19): the monthly top
10 now has four attempts on the first day of the month (08:17–11:17)
instead of one. The new module `src/top_guard.py` records in
`data/last_top.json` which week and month have been sent; later
scheduled attempts end without sending. Manual runs are never blocked.
Not recorded: test runs from branches, a missing webhook (so a later
attempt can still send) and a preview of a period that has not ended (so
it does not block the full report). Both top workflows have write
permission (marker only) and share the concurrency group `top-reports`;
all three workflows fetch other changes before pushing (`git pull
--rebase`), because on Mondays the digest and the weekly top may save at
the same time.

Summaries in the tops: the archive (`src/article_archive.py`) saves the
AI summary of each delivered article, and the tops show it under the
title as a quote (the summary of the first article in the event that has
one). A long top repeats its header with "(cd.)" in every following
message – before, the second message started at item 9 in the middle of
the list, which Discord numbered wrongly. Shared delivery for both tops:
the `deliver` function in `src/monthly_top.py`. Tests use temporary
markers and do not depend on the branch or trigger.

The change was verified: unit tests (189) passed, also in the branch and
scheduled-run environments; a preview of the weekly top for 2026-10-19/25
on the real archive (OpenCode merged from two sources). Manual monthly
top 10 runs on the `v22-top-tygodnia` branch (2026-10-20, 23:29 and
23:52, month 2026-10): delivered only to `#prasówka-test`, "(cd.)" header
in the second message, no marker commit on the branch. During upload 4
files first landed in the repository root instead of `src`; they were
removed before merging.

**Limitations:** the weekly top cannot be run from a branch before
merging (GitHub shows the run button only for workflows on `main`) – its
first live run after merging (2026-10-21, 00:03, preview of the week
2026-10-19/25) reached `#top-tygodnia` and wrote no marker. Articles
archived before this change had no summaries (11 of 11), so the preview
showed titles only – backfill: v23. English titles are still not
translated (planned for the next version).

## v21 --- 2026-10-20

**Glossary mirror from CyberSec Mozaika v84 and explanations in
parentheses for 7 chosen terms only.**

`data/glosariusz_mirror.csv` was generated from the CyberSec Mozaika
mother workbook v84 (727 entries): new H723 wiper, H724 komunikat
bezpieczeństwa, H725 obejście uwierzytelniania and H726 DLL sideloading,
replacing the temporary rows from the "Hasła do dopisania" sheet
(DOP-9…11).

Reason for the second change: in the v20 tests code explained each of
about 270 English mirror terms, so there were too many parentheses and
some were wrong ("NATO (translacja adresów sieciowych)" – the acronym NAT
matched inside NATO; "DLL sideloading (instalacja spoza sklepu)" – the
shorter entry matched inside the longer one). Decision of 2026-10-20:
parentheses only for 7 terms – ransomware (program żądający okupu),
infostealer (program kradnący dane), exploit (kod wykorzystujący
podatność), botnet (sieć zainfekowanych urządzeń), MFA (uwierzytelnianie
wieloskładnikowe), podwyższenie (eskalacja) uprawnień and poświadczenia
(dane logowania). "Łatka" (instead of "poprawka") and "opłacani przez
państwo" – without parentheses. All other entries still enforce the text
form and the forbidden-form check, just without parentheses.

Code changes: `tools/eksport_mirrora.py` no longer adds explanations
automatically (only from the digest's decision list), and ignores spaces
and hyphens when detecting English-first names ("DLL sideloading" = "DLL
side-loading"). `src/glossary.py`: acronyms match only as whole words
(optionally with an ending after a hyphen, e.g. "IAB-ów"), longer terms
are checked before shorter ones; inflection rules for "poprawka" and
"opłacani przez państwo" removed. Tests updated (`src/test_glossary.py`,
`src/test_discord_output.py`); a test ensures exactly the 7 chosen
entries have parentheses.

The change was verified: unit tests (170) passed. A manual run on the
`v21-mirror-v84` branch (2026-10-20, 23:06): 8 of 92 articles, digest
only on `#prasówka-test`; parentheses added by code only for ransomware,
exploit and poświadczenia (inflected: "poświadczeń (danych logowania)"),
no wrong explanations.

**Limitations:** in one summary the AI wrote "poprawce" instead of
"łatce" – "poprawka" is not on the forbidden list, so the check does not
catch it (to consider in the summary quality version). The Mozaika
mother workbook has "poprawka, łatka" at H166 and "oprogramowanie
wymuszające okup" in the notes of H015 – under the unification rule the
digest's forms can be moved to the mother workbook in its next version.

## v20 --- 2026-10-20

**Test channel for runs from branches: a test never reaches the main
channel and saves nothing.**

Reason: on 2026-10-20 a test on the `v19-harmonogram` branch sent 2
articles to the main channel and recorded them as published only on that
branch; 10 minutes later a late scheduled run on `main` sent the same 2
articles again, because `main` did not know about them.

New module `src/test_mode.py`: a run on any branch other than `main`
(variable `GITHUB_REF_NAME`) is a test run – the digest goes to a separate
Discord channel `#prasówka-test` (secret `DISCORD_TEST_WEBHOOK_URL`), the
first message has the banner "🧪 TEST · gałąź … · bez zapisu w historii
i archiwum", and `src/main.py` saves no published links, archive,
history or daily marker. The branch therefore keeps the data of `main`,
and `main` never resends articles tested on a branch. Without the test
secret a branch run sends nothing and never reaches the main channel.
The same applies to the monthly top 10 (`src/monthly_top.py`). Both
workflows pass `DISCORD_TEST_WEBHOOK_URL` only to the sending step. Runs
from `main` (manual and scheduled) work as before.

A new test `src/test_scripts_compile.py` checks the syntax of every file
in `src`, including those no other test imports: the first version of
the change in `main.py` had a syntax error (`elif` after a `try/except`
block) that the unit tests missed; that run stopped before fetching
anything (nothing was sent or saved).

The change was verified: unit tests (165) passed; a simulation of
`main.py` on fake data in both modes (branch: sent only to the test
channel, history unchanged; `main`: main channel, history saved). On the
`v20-kanał-testowy` branch: the 12:14 run found no new articles (the log
confirmed test mode and no saving); the 22:38 run sent 7 of 92 articles
only to `#prasówka-test` with the test banner, and the branch got no data
commit.

**Limitations:** test mode depends only on the branch name; a manual run
on `main` always goes to the main channel. A branch test does not check
saving history and archive (by design) – those parts are confirmed by the
first digest after merging.

## v19 --- 2026-10-20

**Reliable morning start: four scheduled attempts and a "one digest per
day" guard.**

Schedule diagnosis from v14 (2026-10-19/20): the first scheduled run on
2026-10-19 came at 11:54 instead of 06:17, and on 2026-10-20 it did not
come at all. Two temporary probes (cron every 20 minutes, one in UTC, one
with `timezone: Europe/Warsaw`) ran about 4 times each in 24 hours
instead of about 70, always both within 1–2 minutes. Conclusion: the
`timezone` field works; GitHub runs schedules in this repository
irregularly, skipping or delaying most starts (GitHub's documentation
allows delays and skipped runs under heavy load).

In `.github/workflows/daily-digest.yml` the schedule now has four
attempts: `17 6-9 * * 1-6` (06:17, 07:17, 08:17 and 09:17 Polish time,
Monday to Saturday). The new module `src/run_guard.py` writes the marker
`data/last_digest.json` (date, trigger, number of articles sent) after
every completed run – also when there was nothing to send, but not after
a failed delivery. A scheduled run ends without sending if today's digest
has already run; manual runs are never blocked and also count as today's
digest. `src/main.py` checks the guard at the start and writes the
marker at the end. Both probes (`schedule-probe-utc.yml`,
`schedule-probe-tz.yml`) were removed.

The change was verified: unit tests (158) passed. A manual run on the
`v19-harmonogram` branch (2026-10-20, 11:16): 2 of 82 articles, 2 of 2
summaries (`gpt-oss-120b`), the digest reached Discord, and the workflow
wrote the marker
`{"date": "2026-10-20", "trigger": "workflow_dispatch", "articles": 2}`.

**Limitations:** skipping a scheduled run can only be checked on `main`
(schedules do not run on other branches) – it will be confirmed in the
coming days and recorded in this entry. If all four attempts are lost,
the digest has to be run manually. If the first attempt finds no
articles, later attempts that day send nothing either. The monthly top 10
(v17) has the same schedule problem and needs a similar safeguard before
2026-11-01.

## v18 --- 2026-10-19

**AI summaries in Polish with a mandatory glossary consistent with the
CyberSec Mozaika glossary.**

New module `src/ai_summaries.py`: every article in the digest gets a
summary in Polish (up to 2 sentences), including articles from Polish
sites. Model: `openai/gpt-oss-120b` on Groq (free tier), falling back to
`qwen/qwen3.8-27b` on Groq (same key, separate rate limit); if both fail,
the digest is sent without summaries. Articles are sent to the AI in
batches of 5; when rate limited (429) the code waits and retries. The
material is the full text from the feed when the feed provides it
(Niebezpiecznik, Z3S), otherwise the RSS description (up to 1,500
characters); article pages are not fetched. Full text is used only for
summaries and does not affect selection. Feed text is treated as data,
not instructions; summaries are cleaned (one line, no links, formatting
or "@"). The `GROQ_API_KEY` secret is passed only to the digest step;
without it the digest works as before. Job time limit: 20 minutes.

Glossary: new file `data/glosariusz_mirror.csv` – a standalone mirror of
the CyberSec Mozaika glossary (mother workbook v83, 726 entries); the
digest never reads the mother workbook. The mirror is generated by the
manually run script `tools/eksport_mirrora.py`, which also holds the
digest's own decisions (text form, explanation in parentheses, AI rule,
forbidden forms). Rule (decision of 2026-10-19): the English term first
where the industry uses it, with the Polish equivalent in parentheses –
as in the mother workbook since v32; exception: "podwyższenie
(eskalacja) uprawnień". The module `src/glossary.py` enforces the
glossary in three places: (1) the prompt ("SŁOWNICZEK JEST
OBOWIĄZKOWY") with 21 fixed conventions and up to 40 entries found in the
summarized articles; (2) a check for forbidden forms (e.g. "eskalacja
uprawnień", "eksploit", "łatka", "aktor zagrożeń") – a summary that
breaks the glossary is sent back once with a note and dropped if still
wrong; (3) explanations in parentheses are added by code, not the AI,
only at the first occurrence of a term in the whole digest and in the
grammatical case of the explained word (forms from Morfeusz 2, e.g.
"poprawce (łatce)", "podwyższenie (eskalację) uprawnień").

In `src/discord_output.py` the summary is quoted under its title (never
separated from it when the digest is split into messages), and a note at
the end of the digest says the summaries were prepared by AI. A section
header is no longer left alone at the end of a message.
`src/deduplication.py` and `src/main.py` pass on the full feed text.

The change was verified: unit tests (151) passed. The first run on the
`v18-streszczenia-ai` branch selected no articles (nothing new above the
threshold), so the AI was not called. The second run (2026-10-19, 23:09):
6 of 85 articles, 6 of 6 summaries written by `gpt-oss-120b` on the first
attempt (no glossary violations); the digest reached Discord
(2 messages). Based on it, three fixes were made before merging: English
terms without parentheses in the prompt (the model copied "exploit (kit)"
literally) and a request to inflect terms; no nested explanations
("(RCE (zdalne wykonanie kodu))"); a section header is moved to the next
message.

**Limitations:** summaries of short teasers (BleepingComputer) often
have 1 sentence; weekly recaps give generic summaries. Code explains
every English mirror term at first use (e.g. "API (interfejs
programowania aplikacji)"), which may add many parentheses. Quality and
the post-test fixes will be assessed in the next digests. The mirror must
be refreshed after every rename in the mother workbook. An outage of the
whole Groq service means a digest without summaries (backup provider
postponed).

## v17 --- 2026-10-19

**Monthly top 10 events delivered to a separate Discord channel.**

Added `src/monthly_top.py` and the `.github/workflows/monthly-top.yml`
workflow. On the first day of each month at 08:17 Polish time
(`Europe/Warsaw`), the previous month's archive is grouped into events
with the same mechanism as in v16, but across the whole month; follow-up
articles from the same source (e.g. updates) are also merged when they
share a name or a CVE identifier. Events are ranked by number of
articles, then number of sources and highest score, and the top 10 are
sent to the `#top-miesiąca` channel via the
`DISCORD_MONTHLY_WEBHOOK_URL` secret. Each item shows the number of
articles and sources (with Polish plural forms) and the first day the
event appeared; an incomplete month is marked in the header. The month
can be given manually (`YYYY-MM`) and is validated against a pattern
before any file is read. The workflow has read-only repository
permissions.

In `src/event_grouping.py`, names may now differ only by an inflectional
ending of up to 3 letters (the name "Medyc" no longer matches the
adjective "medycznej"), and the rarity limit of a word can grow with the
size of an event (needed at monthly scale, where the name appears in
every article about the event). Tests were added (107 in total),
covering follow-up merging, ranking, plural forms, incomplete months and
invalid months.

The change was verified: unit tests (107) passed; a simulation on an
archive of real titles revealed two false merges (two different Sekurak
articles sharing common words, and "Medyc"/"medycznej"), which were
fixed before deployment. After merging, a manual run of the workflow on
the `main` branch (2026-10-19) succeeded: the "📅 Top 10 · październik
2026" summary reached the `#top-miesiąca` channel, marked as an
incomplete month (archive from 19.10) and containing one item (OpenCode
Console Breach…, 1 article, 1 source).

**Limitations:** the workflow can be run manually only after merging
into `main`, because GitHub shows the run button only for workflows that
exist on the default branch. The schedule uses
the `timezone` field, whose behaviour is being investigated (see v14).
Ranking by number of articles favours events covered by many sites over
single but important analyses.

## v16 --- 2026-10-19

**Detection of the same event reported by different sources, and a "Ciąg
dalszy" (follow-up) section.**

Added `src/event_grouping.py`. Articles from different sources about the
same event are merged into one digest item, with "także:" (also:) and
links to the other sources. A merge requires a shared CVE identifier, at
least two shared rare title words, or one shared name that appears in no
other title of the day (a word with an inner capital letter, such as
"BeyondTrust", or a capitalized word in the middle of a sentence-case
title, such as "Fakturownia.pl"). Words are compared by five-letter
stems, and generic news and security vocabulary is ignored. Articles
from the same source are never merged. A group is represented by its
highest-scoring article, preferring Polish sources on ties; if that
article's source has reached its limit, another group member represents
the event. Articles about events delivered within the last 3 days
(according to the v15 archive) are shown in a separate "🔁 Ciąg dalszy"
section.

Links of all grouped articles are recorded in `published_links`, and the
archive stores related sources and the follow-up flag. The log now
reports merged duplicates and follow-up articles. Changes cover
`src/main.py`, `src/article_selection.py`, `src/article_archive.py` and
`src/discord_output.py`; tests based on real title pairs were added (94
in total). The change was committed directly to `main`, without a pull
request, after the files were uploaded to the wrong branch.

The change was verified: unit tests (94) passed; 6 of 7 real "same
event" pairs were detected, with no false merges among 13 "different
events" pairs; a simulation on 68 real titles merged, among others,
Cisco, BeyondTrust, Palo Alto, the French store attacks and Fakturownia,
and marked a follow-up from the archive. Live runs (on `main` and on the
`v17-top-miesiaca` branch) succeeded; they did not yet contain articles
to merge.

**Limitations:** the rules favour precision over completeness, so some
duplicates are missed, e.g. when a name starts both titles and one of
them is in Title Case (the Drupal pair). Only titles are compared.
Grouping has not yet run on a real morning digest with many articles.

## v15 --- 2026-10-18

**Monthly archive of delivered articles and more robust data
persistence.**

Added the `src/article_archive.py` module, which stores each article
delivered to Discord in a monthly file `data/archive/YYYY-MM.json`:
digest date (Polish time), title, link, source, categories and score.
The same link is never stored twice, and Polish characters are written
readably. The archive is the basis for the planned monthly top 10 digest
and later integration with Mozaika. `run()` in `src/main.py` archives
the selected articles right after a successful delivery. An archive
error is logged, the article history is still saved, and the run ends
with an error, so delivered links are not sent again.

In the workflow, the persist step now stages the whole `data` folder
before checking for changes, so new archive files are committed
(previously only `data/seen_articles.json` was checked and new files
would have been lost). The step also runs when the digest step fails
(`if: ${{ !cancelled() }}`), so links delivered before a failure are
always recorded. Added 9 archive tests. Updated the README (PL and EN),
including planned features for repeated-event detection and the monthly
top 10.

The change was verified: unit tests (78) passed; a full-run simulation
created an archive file with 20 delivered articles, and a simulation
with a deliberately corrupted archive file confirmed that the history is
saved and the run ends with an error. A manual run on the `v15-archiwum`
branch succeeded but selected no articles (76 eligible, 1 promotional,
75 below threshold), so it only confirmed that the persist step behaves
correctly when nothing changes.

**Confirmation (2026-10-19):** the first run delivering an article
(manual, on the `v17-top-miesiaca` branch) created
`data/archive/2026-10.json` with a correct entry, and the persist step
committed it together with the history. **Limitations:** the archive
covers articles from the deployment date onwards, so October 2026 is
incomplete. The archived date is the digest date, not the article's
publication date.

## v14 --- 2026-10-18

**Automatic digest schedule: 06:17 Polish time, Monday to Saturday.**

A `schedule` trigger with the cron expression `17 6 * * 1-6` and the
`Europe/Warsaw` timezone was added to
`.github/workflows/daily-digest.yml`. The digest runs automatically
Monday to Saturday (not on Sundays), and the `timezone` field keeps the
hour fixed across daylight saving changes. Starting at 06:17 rather than
on the hour reduces the risk of delays during peak GitHub Actions load.
Manual runs (`workflow_dispatch`) remain available. A `daily-digest`
concurrency group (`cancel-in-progress: false`) was added so manual and
scheduled runs never overlap and the same articles are not sent twice
before being recorded in `published_links`. No Python code was changed.
The README (PL and EN) was updated.

The change was verified: GitHub accepted the new workflow file, and a
manual run on the `v14-harmonogram` branch succeeded: all 6 feeds were
retrieved without errors (150 entries), 71 previously published articles
were skipped, and of 79 eligible articles 3 were selected, with 1
excluded as promotional and 75 below the relevance threshold. The digest
was delivered to Discord.

**Limitations:** schedules run only from the `main` branch, so the first
scheduled run (planned for 2026-10-19) came at 11:54 instead of 06:17,
and on 2026-10-20 it did not come at all – diagnosis and fix: v19. GitHub does not guarantee exact start times
for scheduled runs; under heavy load they may be delayed or skipped.

## v13 --- 2026-10-17

**Selection quality: Polish keywords, relevance threshold, source
limits, and promotional filter.**

`src/article_selection.py` was reworked. Keywords are written as word
stems matched from the start of a word (e.g. `wyciek` covers "wycieku"
and "wyciekiem"), and `$` marks a whole-word match (e.g. `luk$` does not
match "lukratywny"). Polish keywords were added for critical news (e.g.
data leak, data theft, hacked, break-in, hacker, critical vulnerability)
and vulnerabilities (e.g. vulnerability, flaw, patch, security fixes,
remote code execution), and Poland-related keywords were extended.
Polish stems were checked against complete inflection paradigms
generated by the Morfeusz 2 morphological analyzer, and forms with stem
alternations were added (e.g. "luce", "łatce", "poprawek", "hakerzy",
"włamali"). "Cyberatak" (cyberattack) and "incydent" (incident) are
counted only in titles.

Only articles scoring at least 2, i.e. critical news or vulnerabilities,
enter the digest; a Poland-related match (+1) raises an article's
position but is not enough on its own, and the digest is no longer
filled up to 20 items. Each source may contribute at most 4 articles,
and Niebezpiecznik at most 2. Promotional titles (webinars, free
trainings, e-books, discounts, sponsored content, lectures, sign-ups)
are excluded. Titles in an event, report, or advice context (e.g.
conferences, experts, "growth", "resilience", how-to guides, regulatory
fines) lose 2 points, so they are selected only with strong security
signals. "Weekendowa lektura" and other weekly roundups are not
excluded. `src/main.py` now logs the numbers of promotional and
below-threshold articles. Tests (24 new, based on real titles from
earlier digests) and the README (PL and EN) were updated.

The change was verified: unit tests (69) passed; a simulation on 58
titles from earlier digests selected 14 articles, rejecting, among
others, fillers unrelated to security, a lecture announcement, a free
training offer, and conference reports. The first workflow run on the
`v13-selekcja` branch selected 20 articles from 105, including 13 from
Polish sources (previously 2 of 20), without exceeding source limits.
The second run, after adding the "resilience" and "fined" contexts,
selected 8 articles from 85: 1 was excluded as promotional and 76 were
below the relevance threshold. `published_links` contains 88 links. The
v12 limitations regarding the dominance of English-language sources,
Polish incidents placed under "Pozostałe", the overly broad word
"polski", the missing promotional filter, and filling the digest up to
20 items were resolved.

**Limitations:** the same event reported by different sites still
appears more than once (e.g. Fakturownia in Niebezpiecznik and Zaufana
Trzecia Strona); detection of repeated events is planned as a separate
change. Scoring relies on keywords and does not understand content: an
incident article without keywords in its title or description will be
skipped, and the context penalty may lower a valuable conference report.
Weekly roundups are scored as a single article. The v12 warning about
possible resending after a partially failed delivery still applies.

## v12 --- 2026-10-15

**Digest delivery to Discord (without AI) and recording of published
links.**

Added the `src/discord_output.py` module, which groups selected articles
by their most important category (importance follows the order of the
`CATEGORIES` dictionary in `src/article_selection.py`, so new categories
are handled automatically), formats them as numbered, clickable titles
with source domains and without page previews, splits the digest into
messages within Discord's length limit, and sends them to a webhook.
Polish plural forms are applied correctly. Mentions such as `@everyone`
from external article titles are disabled. When a section continues in
the next message, its header is repeated with a "(cd.)" suffix; the
message limit was set to 1900 characters as a safety margin.

`run()` in `src/main.py` builds the digest from the selected articles
and sends it to the address in the `DISCORD_WEBHOOK_URL` environment
variable. Links are added to `published_links` only after a successful
delivery. A missing variable skips delivery without an error, and a
delivery failure ends the run with an error, so the workflow is marked
as failed. The workflow passes the `DISCORD_WEBHOOK_URL` repository
secret only to the step that runs the digest. The limitation described
in v11 was resolved: the "Artykuły widziane wcześniej" counter was
replaced with "Artykuły opublikowane wcześniej (pominięte)" (previously
published, skipped).

Added `clean_title()` to `src/rss_helpers.py`, which decodes HTML
entities in titles (e.g. `&#8230;`, `&#x1f4cc;`) that some feeds,
including Niebezpiecznik, encode twice. Added 15 unit tests
(`src/test_discord_output.py` and tests for `clean_title()`); the tests
do not contact Discord. Updated the README (PL and EN), including the
truncated end of the planned features list in README_PL.

The change was verified: unit tests (45) passed; three manual workflow
runs on the `v12-discord-from-main` branch delivered 20-article digests
to a private Discord channel. Each subsequent run skipped previously
published articles: 150, 130 and 110 articles were eligible for
selection, and `published_links` contains 60 links. Repetition of the
"(cd.)" header in continued messages was confirmed.

**Limitations:** selection relies on English keywords, so in the first
run 18 of 20 articles came from English-language sources, and Polish
articles about incidents (e.g. data leaks) were placed under "Pozostałe"
(other). The word "polski" can be too broad a signal, and promotional
content (webinars, weekly recaps) is not filtered. The digest is always
filled up to 20 items, including articles of low relevance. The same
event reported by different sites appears more than once, because
deduplication works on links. If delivery fails after some messages have
been sent, the links are not marked as published and may be sent again.

## v11 --- 2026-10-15

**Main flow moved into a `run()` function; full stage 3 run confirmed.**

In `src/main.py`, code previously executed at module level (RSS
retrieval, categorization, TOP 20 selection, history update) was moved
into a `run()` function, called only under
`if __name__ == "__main__":`. Processing logic is unchanged: apart from
indentation, the diff consists of three added lines. Importing
`main.py` from another module no longer downloads feeds or overwrites
`data/seen_articles.json`, which allows further modules (e.g. Discord
delivery or glossary integration) to be added without side effects.

The change was verified: unit tests (30) passed; a manual workflow run
on the `refactor-main` branch succeeded: 6 feeds without errors, 150
entries, 150 unique articles, 0 invalid entries, 150 articles eligible
for selection, 20 selected for the digest. History grew to 250 links in
`seen_links`; `published_links` remains empty. The RSS summary and
selection statistics were confirmed to be printed in the log. Their
earlier absence most likely resulted from the GitHub Actions log search
covering only expanded steps, not from a program error.

The README (PL and EN) no longer states that selection still requires
confirmation, and its latest verified results section now shows the
results of this run, with a reference to the changelog. The changelog
header now notes that, from v11 onwards, entries are added together with
each change rather than reconstructed from Git history.

**Limitation:** the "Artykuły widziane wcześniej" (previously seen
articles) counter actually counts previously published articles
(`published_links`), not previously detected ones (`seen_links`); with
an empty publication list it shows 0. To be fixed when publishing is
implemented.

## v10 --- 2026-10-11

**Separate the history of discovered articles from published articles,
and filter out links already marked as published.**

The `data/seen_articles.json` structure was extended with
`published_links`, separate from `seen_links`. Loading and saving
published links, tests for the updated structure, and the
`filter_unpublished_articles()` function were added. Filtering was
integrated into the RSS workflow, and history messages were clarified to
distinguish previously discovered links from links marked as published.
The English and Polish documentation was also updated to reflect the
current implementation.

This change prepares the workflow to distinguish article collection from
publication. **Limitation:** the reviewed history does not confirm a
Discord integration or a complete process that automatically adds a link
to `published_links` after successful publication. The filter alone does
not mean publishing has been implemented.

## v9 --- 2026-10-11

**Select the top 20 articles by priority.**

A function was added to select the highest-scoring articles, with a
default limit of 20. It was imported into the main workflow and
integrated with RSS processing. Tests were added for top-article
selection and edge cases. The selection uses the categories and scoring
rules introduced in the earlier selection module.

This stage selects candidates for further use; it does not publish them.
**Limitation:** AI-generated summaries and delivery of selected articles
to Discord are not confirmed as implemented.

## v8 --- 2026-10-10

**Rule-based article categorization and priority scoring.**

The `src/article_selection.py` module was added to classify topics using
explicit rules and keywords, including critical cybersecurity
information, vulnerabilities, and Poland-related topics. The scoring
rules assign +3 for the critical category, +2 for vulnerabilities, and
+1 for Poland-related topics. Tests were added, the module was connected
to the main script, and category and score logging was introduced.

This is rule-based selection, not classification performed by an AI
model. Top-20 selection was added in the following stage. This entry
does not imply that summarization or publishing was implemented.

## v7 --- 2026-10-10

**Persist article-link history between GitHub Actions runs.**

The `data/seen_articles.json` file and `src/article_history.py` module
were added to read and write article history as JSON. Tests for history
handling, support for a missing file, data-structure checks, and
preservation of the order of unique links were introduced. The main RSS
workflow began loading previously saved links, skipping previously seen
articles, and reporting their count separately from duplicates found
during the current run.

New links are saved after processing. The workflow received
`contents: write` permission and a step to persist the updated history
file in the repository. A diagnostic message for history loading was
also added.

This allows the project to remember links between workflow runs. It does
not store full article contents or guarantee that an article will remain
available in its source feed.

## v6 --- 2026-10-10

**Validate RSS entries, retain article descriptions, and improve
processing summaries.**

Article validation was extended: entries without a valid title or link
are rejected, and URLs are checked for a supported HTTP/HTTPS scheme and
host. Counters were added for collected items, invalid entries, and
duplicates, along with an aggregate processing summary. Duplicate
counting was refined so that entries rejected during validation are not
counted as duplicates.

The `is_valid_url()` and `is_duplicate_link()` functions were extracted
into `src/rss_helpers.py`, and unit tests were added. The parser began
reading descriptions from RSS `description` and Atom `summary`, and
article records were extended with a description field. Indentation
errors in RSS processing and a syntax error in the tests were also
fixed.

These changes improved diagnostics and testability. They do not
guarantee that external feeds provide complete or correct data.

## v5 --- 2026-10-10

**Extract deduplication into a separate module and run tests in CI.**

Deduplication logic was moved from the main script into
`src/deduplication.py`, exposing the `add_article()` function. The main
RSS workflow uses the separate module, and tests cover duplicate
detection and adding new articles. GitHub Actions was extended to run
unit tests.

The refactor made the logic easier to test independently and maintain.
Deduplication by link itself had been introduced in an earlier stage.

## v4 --- 2026-10-09

**Initial article deduplication and aggregation of source information.**

A mechanism was added to identify the same article by link and prevent a
second record from being added for a repeated URL. Article records were
extended with source information, allowing a link found in multiple
feeds to retain information about more than one source. The logic was
then prepared for extraction into a separate module.

Deduplication is based on the link. It does not identify identical
article content published under different URLs.

## v3 --- 2026-10-08

**Support six sources and both RSS and Atom formats.**

Feed retrieval was extracted into `fetch_feed(url)`, and the
configuration was expanded to six sources: Niebezpiecznik, Sekurak,
Zaufana Trzecia Strona, CyberDefence24, BleepingComputer, and The Hacker
News. The parser supports RSS `item` elements and Atom `entry` elements,
including namespace-qualified titles and Atom links read from the `href`
attribute.

Handling of whitespace before an XML declaration was improved. HTTP
requests gained a `User-Agent` header and a 20-second timeout. Errors
while retrieving or parsing one feed are handled separately so the
program can continue with the remaining sources. Articles are collected
into a shared list, and a temporary limit of five entries per feed was
removed. Article records also gained a source field.

This stage enables retrieval and processing of entries from multiple
feeds. It does not include summary generation or publishing.

## v2 --- 2026-10-08

**Run the script and tests through GitHub Actions.**

The initial `Daily CyberSec Digest` workflow was created, with
repository checkout and execution of the Python script. The YAML
structure was corrected, including moving `jobs:` to the top level of
the configuration. An initial test and basic repository configuration
files were added.

The workflow is configured for manual execution through
`workflow_dispatch`. **Limitation:** the reviewed configuration does not
contain a schedule for automatic daily runs.

## v1 --- 2026-10-08

**Initial project scaffold.**

The project repository and basic files were created, along with an
initial Python script for retrieving and parsing an RSS feed. Early
testing examined XML responses and adapted the parser to the actual
structure of feed entries. Temporary diagnostics and experiments used to
inspect individual sources are not listed as separate features when they
were later removed.

This provided the foundation for later stages: multiple sources,
validation, deduplication, article history, and priority-based
selection.

------------------------------------------------------------------------

## Project status based on the reviewed history

-   **Confirmed features:** retrieval and parsing of RSS/Atom from
    multiple sources, entry validation, deduplication by link, source
    and description metadata, persistent link history, rule-based
    categorization and scoring, selection of up to 20 articles, and
    filtering of links marked as published.
-   **Not confirmed as implemented:** AI-generated article summaries,
    publishing to Discord, and an automatic daily schedule.
-   `seen_links` and `published_links` have different roles. The
    presence of a published-link filter does not prove that external
    publishing is implemented or that `published_links` is updated after
    a successful publication.
