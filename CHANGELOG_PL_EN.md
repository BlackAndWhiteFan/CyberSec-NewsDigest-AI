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

## v40 · Dwa nawiasy --- 07.11.2026

**Objaśnienia w nawiasach tylko przy dwóch terminach (mirror v92).**

Powód: pierwsza decyzja autora z przęsła P8 · Rozbieżności mostu
(List 18, 2.11.2026). Od pliku-matki v92 objaśnienia H182 i H207 pochodzą
z bloku językowego pliku-matki, a nie z wyjątków w kodzie mostu
(Listy 21–22). Objaśnienie w nawiasie zostaje tylko tam, gdzie
polski termin bywa niejasny: „podwyższenie (eskalacja) uprawnień” (H182)
i „poświadczenia (dane logowania)” (H207). Exploit, botnet, ransomware i
infostealer (H153, H004, H015, H019) są dla czytelnika prasówki
zrozumiałe bez objaśnienia; wiper (H723) objaśnienia nie miał.

Zmiany:

- **Mirror v92** `data/glosariusz_mirror.csv` z eksportera mostu
  (krok K5 runbooka: nowy mirror do Prasówki), zamiast dwóch osobnych
  mirrorów (List 22): pusta kolumna `nawias` przy H004, H015, H019 i
  H153, nagłówek `plik-matka v92 · 2026-11-03`.
- **Kod objaśnień** (`src/glossary.py`): usunięte objaśnienia odmieniane
  dla exploita, botnetu i infostealera, objaśnienie ransomware zależne
  od przypadka i reguła pomijania „ransomware” po osobach i grupach
  (v33). Tabele form exploita, botnetu i infostealera zostają jako
  zestaw testowy dla form odmienionych planowanych w pliku-matce
  (List 16, pkt 3a). Mechanizm objaśnień działa dalej z danych mirrora,
  więc przywrócenie objaśnienia w pliku-matce nie wymaga zmian w kodzie
  (poza odmianą zależną od przypadka).
- **Testy:** przykłady objaśnień przeniesione na H182 i H207; nowy test,
  że exploit, botnet, ransomware, infostealer i wiper zostają bez
  nawiasu. Razem 441 testów.

Zmienione pliki: `data/glosariusz_mirror.csv`, `src/glossary.py`,
`src/test_glossary.py`, `src/test_quality_v33.py`,
`src/test_discord_output.py`, README (PL/EN).

------------------------------------------------------------------------

## v39 --- 02.11.2026

**Straż dwóch ostatnich linii danych dla mostu i pole `proofread`.**

Powód: analiza grafu „Linie styku” w Kartonie Mostu (List 13). Raport
mostu (`bridge_report.py` w repo `cybersec-most`) czyta z Prasówki cztery
pliki, a test kontraktu z v38 pilnował tylko dwóch: archiwum i mirrora.
Zestawienia (`data/tops/`, dla przęsła P4 · Żywe przykłady) i lista kalk
(`data/styl_unikaj.csv`, dla przęsła P3 · Kalki) nie miały strażnika. Do
tego most chce przy wyborze żywych przykładów preferować zdania, które
przeszły korektę językową (List 14).

Pierwsze zestawienie zapisane przez v38 (`data/tops/2026-W44.json`,
2.11.2026) posłużyło jako prawdziwy materiał do testu.

Zmiany:

- **Test kontraktu zestawień** (`src/test_v39.py`): każdy plik w
  `data/tops/` – lista z kolejnymi pozycjami od 1, wszystkie pola,
  `kind` (`week`/`month`) zgodny z formatem okresu, okres zgodny z nazwą
  pliku, typy liczb i list.
- **Test formatu listy kalk:** nagłówek dokładnie `forma;zamiast`,
  separator `;`, komentarze `#`, gwiazdka tylko na końcu słowa – tak, jak
  plik czyta raport mostu.
- **Pole `proofread`** (`src/ai_summaries.py`, `src/article_archive.py`):
  nazwa modelu, który sprawdzał streszczenie w korekcie językowej, albo
  pusty tekst, gdy korekty nie było (np. Gemini i Mistral niedostępne).
  Rekordy sprzed v39 nie mają tego pola – most odróżnia oba przypadki.

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/article_archive.py`,
`src/test_v39.py` (nowy), README (PL/EN).

Testy jednostkowe: 443, zakończone powodzeniem.

------------------------------------------------------------------------

## v38 --- 01.11.2026

**Dane dla mostu do CyberSec Mozaika: hasła w archiwum, zapis zestawień,
test kontraktu; mirror v90; eksporter w repo mostu.**

Powód: ustalenia z Prasówką–Mozaiką (Listy 1–11 w `cybersec-most`) i
próbny raport mostu z 1.11.2026. Raport (`bridge_report.py` w prywatnym
repo `cybersec-most`) czyta dane Prasówki, nie jej kod. Brakowało mu
dwóch rzeczy: informacji, które hasła wystąpiły w artykule (streszczenia
są odmienione, więc szukanie form po stronie mostu byłoby zawodne), i
zestawień, które dotąd istniały tylko na Discordzie.

Zmiany:

- **Pole `terms` w archiwum** (`src/article_archive.py`, `src/glossary.py`):
  ID haseł z mirrora (H###) znalezionych w tytule i streszczeniu, tym
  samym dopasowaniem co słowniczek w prompcie.
- **Zapis zestawień** (`src/monthly_top.py`, `src/weekly_top.py`):
  wysłane top 5 i top 10 trafiają do `data/tops/RRRR-Www.json` i
  `RRRR-MM.json` (pozycja, tytuł, link, streszczenie, model historii,
  liczba artykułów i serwisów, KEV, CVE, linki). Plik powstaje razem ze
  znacznikiem, więc nie przy testach z gałęzi. Log: „ZAPIS ZESTAWIENIA”.
- **Test kontraktu danych** (`src/test_v38.py`): pola rekordu archiwum,
  pola notatek języka według typu, wartości `fixed_by`, 6 kolumn i
  nagłówek mirrora.
- **Test miejsca plików:** w `src/` tylko kod, w katalogu głównym bez
  plików `.py`/`.csv`/`.json`. 1.11 mirror v90 trafił do `src/`,
  Prasówka czytała dalej v84, a wszystkie testy przechodziły.
- **Eksporter mirrora usunięty** (`tools/eksport_mirrora.py`): mieszka
  teraz w `cybersec-most` razem z `OVERRIDES`, bo czyta prywatny
  plik-matkę.
- **Log na bieżąco:** `PYTHONUNBUFFERED=1` w workflow prasówki i
  zestawień (31.10 krok wyglądał na zawieszony, bo log pojawiał się
  dopiero na końcu).
- **Licencja słowniczka** w obu README (CC BY-NC-ND 4.0, © Jan Wolski).

Drobna poprawka z 1.11 (osobno, przed v38): mirror odświeżony do
pliku-matki v90 – 740 haseł (14 nowych haseł UKC, H727–H740), 6 kolumn
używanych w runtime, nagłówek z wersją i datą ISO oraz atrybucją CC.

Nowe i zmienione pliki: `src/article_archive.py`, `src/glossary.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/ai_summaries.py`,
`src/test_v38.py` (nowy), `tools/eksport_mirrora.py` (usunięty),
`.github/workflows/daily-digest.yml`, `weekly-top.yml`,
`monthly-top.yml`, README (PL/EN).

Testy jednostkowe: 436, zakończone powodzeniem.

------------------------------------------------------------------------

## v37c --- 31.10.2026

**Powód odmowy API w logu; Ministral jako model Mistrala; odczyt
odpowiedzi Ministrala.**

Powód: w testach zestawienia tygodniowego z 31.10.2026 Mistral odpowiadał
„HTTP Error 403: Forbidden” – także dla `mistral-large-2512` z listy
limitów darmowego poziomu, przy włączonej zgodzie na trenowanie i bez
ograniczeń dostępu w organizacji. Log pokazywał tylko kod, bez powodu.

Zmiany:

- **Powód odmowy w logu** (`src/ai_summaries.py`): przy błędach HTTP 4xx
  (poza 404 i 429) log dostaje pierwsze 200 znaków odpowiedzi API, np.
  „KOREKTA: Mistral … niedostępny … | odpowiedź API: {…}”. Klucz nigdy nie
  trafia do logu.
- **Domyślny model Mistral** (`src/mistral.py`): `ministral-14b-2512`.
  Nowy log pokazał powód 403: `mistral-large-2512` jest na liście limitów,
  ale nie w darmowym planie („This model is not available in your
  subscription tier”); `mistral-medium-latest` ma 20 000 tokenów na
  minutę, mniej niż jedno zapytanie z historiami (429). Ministral (937 500
  tokenów na minutę) napisał pierwsze prawdziwe historie wydarzeń, np.
  PHP2Shell od honeypota do Mirai, Arista „trzecia taka luka w cztery
  miesiące” z późniejszego artykułu. Zmienna `MISTRAL_MODEL` dalej go
  podmienia.
- **Pusta odpowiedź to porażka** (`src/ai_summaries.py`): test z
  `ministral-14b-2512` – model odpowiedział, ale nie dało się z odpowiedzi
  odczytać ani jednej historii, a kod uznał ją za sukces i nie spróbował
  kolejnego modelu („ZESTAWIENIE AI: pominięte”). Teraz taka porcja
  przechodzi do następnego modelu, log pokazuje początek odpowiedzi, a
  odczyt przyjmuje identyfikatory jako tekst („1”), klucz „wydarzenia” oraz
  pole „historia” zamiast „tekst” (tak odpowiada `ministral-14b-2512`).

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/mistral.py`,
`src/test_v37c.py` (nowy), README (PL/EN).

Testy jednostkowe: 427, zakończone powodzeniem.

------------------------------------------------------------------------

## v37b --- 31.10.2026

**Zestawienia na tym samym łańcuchu co prasówka.**

Powód: przed pierwszym miesięcznym top 10 (1.11.2026) – konsekwencja
projektowa po v37a. Korekta streszczeń w zestawieniach przeszła na nowy
łańcuch już w v37a (`proofread_top` używa `proofread_summaries`), ale
workflow zestawień nie dostawały sekretu Mistrala, a historie wydarzeń
(`summarize_events`) szły starą drogą: jedno zapytanie, Gemini w jednej
rundzie, potem Groq.

Zmiany:

- **Historie wydarzeń w porcjach i rundach** (`src/ai_summaries.py`):
  Gemini główny, Mistral, Gemini lite, a od drugiej rundy Groq jako ostatni
  piszący. Mistral przed lite, inaczej niż w korekcie: w teście z gałęzi
  `gemini-3.5-flash-lite` napisał każdą historię jak streszczenie jednego
  artykułu (PHP2Shell: 17 artykułów, nic po 22.10) – lite wystarcza do
  korekty, nie do składania historii z wielu artykułów – i tak pisze streszczenia dzienne, a każda historia przechodzi
  kontrolę względem materiału wydarzenia. Log: „ZESTAWIENIE AI: 1–5 –
  model …”.
- **Workflow tygodniowy i miesięczny** dostają `MISTRAL_API_KEY`,
  `GEMINI_LITE_MODEL` i `MISTRAL_MODEL`.
- Korekta zestawień działa także z samym kluczem Mistrala.

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/test_v37b.py`
(nowy), `.github/workflows/weekly-top.yml`,
`.github/workflows/monthly-top.yml`, README (PL/EN).

Testy jednostkowe: 420, zakończone powodzeniem.

------------------------------------------------------------------------

## v37a --- 31.10.2026

**Korekta językowa codziennie: porcje, Gemini lite, Mistral; bez pustych
„dwóch innych luk”.**

Powód: prasówki z 30 i 31.10.2026 wyszły bez korekty (JW: „wolałbym
jednak powtarzalność korekty językowej”). Logi: oba modele Gemini
niedostępne w obu rundach – przekroczenie czasu i 503, ani jednego 429,
czyli przeciążenie po stronie Google, a nie wyczerpany limit. Bez
korekty przeszły m.in. „grupa wyciekła dane”, „10 august 2023”, „nie
zostały załatwione”. Do tego „oraz dwie inne luki” w 5 streszczeniach –
pusta wzmianka, którą podsuwała sama prośba o ograniczenie numerów CVE.

Zmiany:

- **Korekta w porcjach po 5 streszczeń** (`src/ai_summaries.py`): krótka
  odpowiedź mieści się w 30 s także przy obciążeniu, a utracona porcja
  nie zabiera korekty pozostałym.
- **Lżejsze modele Gemini** (`src/gemini.py`): `gemini-3.8-flash-lite`,
  `gemini-3.5-flash-lite` po modelach głównych; osobna pula mocy.
  Zmienna repozytorium `GEMINI_LITE_MODEL` podmienia nazwy.
- **Mistral jako ostatni zapas** (`src/mistral.py`, nowy): darmowy plan
  bez karty, sekret `MISTRAL_API_KEY`, model `mistral-large-latest`
  (zmienna `MISTRAL_MODEL`). Wchodzi od drugiej rundy – Gemini ma
  pierwszeństwo. Bez Groq, jak od v35.
- **Trzy rundy z rosnącą przerwą** (30 s, 60 s); model, który zawiódł, jest
  pomijany do końca rundy, żeby nie czekać na niego przy każdej porcji.
  Log: „KOREKTA: streszczenia 1–5 – model …”, „KOREKTA: runda 2 za 30 s”,
  „KOREKTA: bez korekty N z M streszczeń”.
- **Bez „oraz dwie inne luki”** (prompt, `src/summary_quality.py`):
  nadmiarowe luki model nazywa typem z artykułu albo pomija; pusta
  wzmianka wraca do poprawki jako problem miękki.

Most do CyberSec Mozaika przesunięty na v38.

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/gemini.py`,
`src/mistral.py` (nowy), `src/summary_quality.py`,
`src/test_proofreading.py`, `src/test_v37a.py` (nowy),
`.github/workflows/daily-digest.yml`, README (PL/EN).

Testy jednostkowe: 415, zakończone powodzeniem.

------------------------------------------------------------------------

## v36 --- 29.10.2026

**Miękkie problemy nigdy nie tną streszczenia; bez urwanych fragmentów;
mniej telegrafu; „z/ze” poprawnie; bez dopisanego phishingu.**

Powód: prasówka z 29.10.2026 (JW: „nieco kulawo, choć trochę lepiej …
rwane”). Korekta Gemini zadziałała (12 z 15, `gemini-3.5-flash` w
ponownej próbie z v35). Problemy:

- Oracle E-Business Suite: „Luka umożliwia … RCE po jej załataniu.” –
  szkic miał tylko kalkę „eksploatację” (problem miękki), poprawka AI
  dostała problem twardy, a kod przyciął poprawioną wersję, wycinając
  pierwsze zdanie z nazwą produktu;
- „ze włączoną funkcją” – błąd autopoprawki z v35 („ze” przed każdym
  „w” ze spółgłoską);
- tekst „rwany”: prompt v34 („krótkie, proste zdania, jedno zdanie –
  jeden fakt”) i podział zdań powyżej 25 słów dały ciąg krótkich zdań
  bez spójników, czasem równoważnik („W tym cztery krytyczne błędy…”);
- dopisany skutek: „co może umożliwić kampanie phishingowe” (Burger
  King; 27.10 „zwiększa ryzyko phishingu” przy Kopenhadze).

Zmiany:

- **Szkic z samymi miękkimi problemami zostaje** (`src/ai_summaries.py`),
  gdy poprawka AI nie jest czysta – kod nie tnie poprawionej wersji.
- **Bez pierwszego zdania – bez streszczenia**: jeśli naprawa przez kod
  usunęłaby pierwsze zdanie (podmiot: produkt, firma, grupa), artykuł
  idzie z samym tytułem. Log: „KONTROLA: streszczenie N odrzucone (kod
  usunąłby pierwsze zdanie)”.
- **„Ze” przed „w” tylko z głoską syczącą** (`src/glossary.py`): „ze
  wsparciem”, „ze wszystkimi”, „ze względu”; „z włączoną”, „z wnukiem”
  bez zmian.
- **Płynniej** (prompt, `src/summary_quality.py`): zdania do ok. 25 słów,
  powiązane fakty łączone spójnikami („bo”, „więc”, „ale”, „a”); każde
  zdanie z orzeczeniem; prośba o podział dopiero powyżej 30 słów (było
  25).
- **Phishing i socjotechnika tylko z artykułu**: wzmianka bez pokrycia w
  materiale wraca do poprawki (na archiwum: 2 dopowiedzenia złapane, 2
  prawdziwe wzmianki przechodzą).

Most do CyberSec Mozaika przesunięty na v37.

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/summary_quality.py`,
`src/glossary.py`, `src/test_v36.py` (nowy), README (PL/EN).

Testy jednostkowe: 404, zakończone powodzeniem.

------------------------------------------------------------------------

## v35 --- 28.10.2026

**Jedna luka – jedna pozycja; korekta tylko przez Gemini; zalecenia tylko
konkretne.**

Powód: prasówki z 27 i 28.10.2026 po v34 (ocena JW: „czytało się trochę
trudno, kuleje polski, watę też pcha … trochę wstyd, czytają to moi
mentorzy”). Problemy zebrane w obserwacji i sprawdzone w archiwum:

- ta sama luka kilka razy: Brotli CVE-2026-111497 w trzech pozycjach
  (27.10), Apple CVE-2026-86950 w dwóch (28.10) – drugi dzień z rzędu;
- korekta językowa przez Groq (Gemini niedostępny trzeci raz w trzech
  dniach) pogorszyła tekst: „starsze iPhone’y i iPad’y” → „starsze
  iPhone’ów i iPad’ów”, „Exploity PoC pojawiły się” → „Exploitów PoC
  pojawiły się”, „uni‑związany” → „niezależny” (zmiana sensu);
- zalecenia w trybie rozkazującym w 6 z 13 streszczeń, często puste
  („Zainstaluj najnowsze wersje systemów, aby usunąć te luki”,
  „Postępuj zgodnie z zaleceniami GMO”, „Zaleca się aktualizację wtyczki
  po jej wydaniu”) – skutek uboczny promptu v34 („3. zdanie: co
  zrobić”);
- uwagi o artykule („Artykuł opisuje…”, „Brak dostępnych łatek w
  artykule”); „w wtyczce”, „z wsparciem”, „łaty”;
- „twofactorgauthenticator” zamiast „twofactor_gauthenticator”;
- „Bezpłatne e-dzienniki z lukami w przepisach” w „Podatnościach”,
  felieton „This is Fine: What NetScaler Zero-Days Tell Us…” w
  „Najważniejszych”.

Zmiany:

- **Łączenie po numerach CVE po pobraniu stron** (`src/event_grouping.py`,
  `merge_by_cves`, `src/main.py`): łączenie wydarzeń działało przed
  pobraniem stron artykułów, a wiele kanałów daje tylko zajawkę bez
  numeru CVE. Po pobraniu stron i znacznikach KEV wybrane artykuły ze
  wspólnym numerem CVE łączą się w jedną pozycję (prowadzi ta z wyższą
  punktacją, przy remisie polska); drugie przejście po streszczeniach
  bierze też numery CVE ze streszczeń (SecurityWeek podał CVE Apple
  dalej niż w pierwszych 600 znakach strony). Log: „SCALENIE PO CVE (ze
  stron / ze streszczeń): N”. Lektura nigdy nie jest łączona.
- **Numery CVE z niełamliwym łącznikiem** (`src/kev.py`,
  `src/summary_quality.py`, `src/ai_summaries.py`): AI często pisze
  „CVE‑2026‑86950” ze znakiem U+2011; kod szukał tylko zwykłego „-”, więc
  takich numerów nie widziały łączenie, KEV ani kontrola faktów (10 ze
  110 streszczeń października). Rozpoznawane są wszystkie warianty, a
  czyszczenie streszczenia zamienia je na „-”.
- **Korekta językowa tylko przez Gemini** (`src/ai_summaries.py`): przy
  chwilowym błędzie (503, przekroczony czas) jeszcze jedna runda po 30 s;
  gdy Gemini jest niedostępny, streszczenia zostają bez korekty – bez
  przejścia na Groq. Historie wydarzeń w zestawieniach (pisanie, nie
  korekta) nadal mają Groq jako zapas.
- **Zalecenia tylko konkretne** (prompt): trzecie zdanie opcjonalne,
  tylko z konkretem (wersja z poprawką, obejście, co wyłączyć), opisowo
  („Poprawka jest w wersji 6.2606.4246.”), nie trybem rozkazującym. W
  kontroli: zalecenie bez konkretu („najnowsze wersje”, „udostępnione
  łatki”, „zgodnie z zaleceniami”, „po jej wydaniu”) to ogólnik; tryb
  rozkazujący na początku zdania – uwaga miękka (prośba o opis, bez
  skracania).
- **Uwagi o artykule** jako ogólnik: „artykuł opisuje / omawia /
  przedstawia…”, „w artykule”; „brak dostępnych łatek” jak „brak łatki”.
- **Autopoprawki** (`src/glossary.py`): „w”/„z” → „we”/„ze” przed
  wyrazem pisanym małą literą, który zaczyna się zbitką spółgłosek
  („we wtyczce”, „we wszystkich”, „we francuskich”, „ze wsparciem”, „ze
  szkoły”); dwuznaki sz, rz, cz, dz liczą się jako jedna głoska („z
  szybkiego” zostaje); nazwy i skróty bez zmian („z SQL”, „w
  Wrocławiu”). „Łata / łaty / łatę…” → „łatka / łatki / łatkę…”.
- **Podkreślnik w nazwach** zostaje („twofactor_gauthenticator”);
  usuwany jest tylko „_”, który mógłby rozpocząć lub zakończyć
  formatowanie Markdown.
- **Selekcja** (`src/article_selection.py`): kara kontekstu dla „luk w
  przepisach / prawie / ustawie”, „luki prawnej” oraz felietonów („tell
  us”, „new normal”, „lessons from”). Felieton z wieloma słowami
  kluczowymi (NetScaler: zero-day) po karze nadal przekracza próg – spada
  w rankingu, ale może wejść, gdy są wolne miejsca.

Test na gałęzi `v35-jakosc` 28.10.2026: zielony, „SCALENIE PO CVE (ze
stron): 0” i „(ze streszczeń): 0” (mało artykułów po porannej prasówce);
korekta pominięta – `gemini-3.8-flash` dwa razy przekroczył czas (2 × 90
s), `gemini-3.5-flash` dwa razy zwrócił 503; Groq nie ruszał tekstu.
Uruchomienie trwało ponad 5 minut. Poprawka: limit czasu zapytania do
Gemini 30 s zamiast 90 s (`src/gemini.py`) – działający Gemini odpowiada
w kilka sekund; najgorszy przypadek czekania spada z ok. 6,5 do ok. 2
minut. Wniosek dla eksperymentu z modelem piszącym: Gemini w darmowym
planie bywa rano niedostępny (cztery dni z rzędu), więc model piszący
musi mieć zapas.

Sprawdzone na archiwum: łączenie po CVE we wszystkich dniach października
łączy tylko pozycje o tym samym wydarzeniu (PHP2Shell, Brotli, Apple);
nowe ogólniki na 107 streszczeniach oznaczają wyłącznie watę i formułki;
autopoprawka przyimków zmieniła tylko błędne formy („z szybkiego” po
poprawce zostaje); kara kontekstu trafia 3 tytuły ze 110, wszystkie
słusznie. Stare testy korekty (przejście na Groq) zastąpione testami
nowej zasady.

Nowe i zmienione pliki: `src/event_grouping.py`, `src/main.py`,
`src/kev.py`, `src/summary_quality.py`, `src/ai_summaries.py`,
`src/glossary.py`, `src/article_selection.py`, `src/gemini.py`, `src/test_v35.py` (nowy),
`src/test_ai_summaries.py`, `src/test_proofreading.py`,
`src/test_language_notes.py`, README (PL/EN).

Testy jednostkowe: 398, zakończone powodzeniem.

------------------------------------------------------------------------

## v34 --- 26.10.2026

**Streszczenia z sensem i łatwe w czytaniu: co się stało, dlaczego to
ważne, co zrobić; streszczenia całych wydarzeń w zestawieniach.**

Powód: ocena top 5 z 26.10.2026 (JW): streszczenia bez waty, ale
telegraficzne – stos numerów CVE i wersji, długie łańcuchy imiesłowów,
bez odpowiedzi na pytania praktyka SOC „czy to jest wykorzystywane?”,
„czy łatać dziś?”. W zestawieniu wydarzenie dostawało streszczenie
jednego artykułu z jednego dnia: PHP2Shell (17 artykułów, 7 serwisów)
to jedno zdanie z numerami CVE i oceną CVSS, bez historii tygodnia
(próby ataków 4 dni przed ujawnieniem, awarie stron, kolejna luka bez
łatki). Cel JW: jakościowo, a jednocześnie strawnie. Decyzja JW z
26.10.2026: most do Mozaiki będzie wersją v35.

Zmiany w prasówce dziennej:

- **Układ streszczenia** (prompt w `src/ai_summaries.py`): 1. zdanie –
  co się stało i kogo dotyczy, zwykłymi słowami, z nazwą produktu lub
  firmy (numer CVE najwyżej jeden, nie na początku); 2. zdanie –
  dlaczego to ważne dla obrońcy: wykorzystywanie w atakach, publiczny
  exploit, skala, łatka albo jej brak; 3. zdanie, gdy artykuł to podaje
  – co zrobić konkretnie. Najwyżej 420 znaków (kontrola: 480), 2 numery
  CVE i 3 wersje.
- **CISA KEV dla AI**: znacznik 🔥 ustawiany przez kod trafia też do
  AI jako pole „kev”, więc „wykorzystywana w atakach” opiera się na
  katalogu, a nie na domysłach; fakt jest dopisany do materiału kontroli.
- **Kontekst ciągu dalszego** (`src/event_grouping.py`): artykuł
  oznaczony jako ciąg dalszy po tytule dostaje wcześniejsze doniesienie
  z archiwum (data i streszczenie) jako pole „kontekst”; AI pisze, co
  nowego, z krótkim nawiązaniem („Kilka dni po ujawnieniu PHP2Shell
  (22.10) …”). Kontekst należy do materiału kontroli faktów.
- **Bezpieczniki** (`src/summary_quality.py`): „aktywnie
  wykorzystywana”, „wykorzystywana w atakach” i „brak łatki / nie
  wydano łatki / niezałatana” tylko wtedy, gdy materiał to mówi (jak
  „zero-day” w v33) – drugie zdanie nie może dramatyzować. Domysły o
  eskalacji („sytuacja może eskalować”, „ataki mogą się nasilić”) to
  ogólnik.
- **Wykrywacz zdań bez konkretu** (`src/summary_quality.py`, pytanie
  JW: jak upewnić się, że AI nie dopcha waty do historii): zdanie bez
  żadnego konkretu (cyfry, numeru CVE, skrótu, nazwy, liczebnika
  słownego) za to ze słownictwem oceniającym („pokazuje”, „wyzwania”,
  „poważne zagrożenie”, „ryzyko”, „współpracuje z ekspertami”) wraca do
  poprawki, a jeśli zostanie – kod je usuwa. Pierwsza wersja (samo „bez
  konkretu”) oznaczyła 35 ze 140 zdań archiwum, z czego połowa była
  dobra („Luka umożliwia wykonanie dowolnego kodu bez
  uwierzytelnienia”), więc odpadła; obecna oznacza 8 ze 140 – wszystkie
  to wata („Firma współpracuje z organami ścigania i ekspertami ds.
  cyberbezpieczeństwa”, „Problemy te pokazały, że … mogą stać się
  wektorem zagrożenia”). Zdanie złapane już przez listę ogólników nie
  jest zgłaszane drugi raz.
- **Czytelność** (miękko, jak lista stylu – nigdy nie skraca
  streszczenia): zdanie dłuższe niż 25 słów i więcej niż 2 numery CVE
  wracają do poprawki z prośbą o podział. Na 60 streszczeniach z
  22–26.10 dotyczy to 14 (np. zdanie PHP z czterema wersjami, 28 słów).

Zmiany w zestawieniach:

- **Streszczenie całego wydarzenia** (`src/ai_summaries.py`,
  `src/monthly_top.py`): jedno zapytanie na zestawienie (Gemini,
  zapasowo Groq) pisze dla każdego wydarzenia z co najmniej dwoma
  pozycjami materiału krótką historię w 3–4 bardzo krótkich zdaniach
  (doprecyzowanie JW z 26.10.2026): co się wysypało i kogo dotyczy, jak
  to szło (najważniejszy zwrot z datą), co dzieje się teraz i czy sprawa
  eskaluje (ataki trwają, nowe botnety, kolejne luki, łatka – tylko na
  podstawie konkretnego zwrotu z materiału), jak to łatać; element bez
  pokrycia w materiale jest pomijany. Historia ma zostać w pamięci
  („człowiek najlepiej uczy się przez historie, które przemawiają do
  wyobraźni”, JW): AI wybiera z materiału jeden konkretny, obrazowy
  szczegół („ataki zaczęły się 4 dni przed ujawnieniem”), bez metafor –
  to samo w prompcie prasówki dziennej zamiast „duża skala”. Historia
  ma się nadawać do opowiedzenia przy kawie ludziom z SOC („case study
  condensate”, JW): w „jak to szło” AI podaje, jeśli materiał to mówi,
  jak atakujący weszli – wektor i technika (SQL injection, skradzione
  klucze, phishing, łańcuch kilku luk). Bez morału i „lekcji” – wnioski
  wyciąga czytelnik; „Ta historia pokazuje, że…” i „lekcja z tego…” to
  ogólniki. Materiał: polskie
  streszczenia artykułów wydarzenia w kolejności dat (z serwisem) i
  tytuły artykułów powiązanych. Nowe streszczenie jest użyte tylko
  wtedy, gdy przejdzie kontrolę faktów, słowniczka i jakości względem
  tego materiału; inaczej zostaje dotychczasowe. Log: „ZESTAWIENIE AI:
  wydarzenie N – przed / po” i „streszczenia wydarzeń N z M”. Potem,
  jak w v33, korekta językowa.

Materiał dla PHP2Shell (top 5 za 19–25.10) to 8 streszczeń od 21.10
do 24.10 i tytuły powiązane („PHP Warns of Another Unpatched RCE Risk…”,
„PHP2Shell Exploit Attempts Hit Millions…”, „Mirai Botnet Operators
Join PHP2Shell Attacks”).

Test prasówki na gałęzi `v34-sens` 26.10.2026 (12:09): 3 artykuły, wszystkie
analizy z lektury. Kontrola złapała zdanie z 26 słowami i adres IP
spoza artykułu. Usterki sprawdzone u źródła: Signal – „nie ma jeszcze
dostępnej łatki”, choć RingRTC 2.72.0 i nowsze aplikacje Signal mają
poprawkę (bezpiecznik przepuścił, bo strona mówi o „unpatched
versions”); Plex2Shell – jedno techniczne zdanie zamiast sedna (łańcuch
czterech luk, RCE bez logowania, CVSS 9.8) i bez historii, bo
ostrzeżenie CISA z 22.10 było starsze niż 3 dni; PaperCut – angielskie
„AI‑orchestrated toolkit”.

Poprawki po teście:

- **Kontekst z 14 dni** (`src/event_grouping.py`, `src/main.py`):
  każdy artykuł dostaje najnowsze wcześniejsze doniesienie o tym samym
  wydarzeniu z archiwum z 14 dni (wspólny numer CVE albo reguła tego
  samego wydarzenia; bez rekordów całej lektury), nie tylko ciąg dalszy
  z 3 dni. Sekcja „Ciąg dalszy” bez zmian (3 dni). Log: „KONTEKST:
  wcześniejsze doniesienie z archiwum dla N z M artykułów”.
- **„Brak łatki” przy wersji z poprawką** (`src/summary_quality.py`):
  „unpatched” / „niezałatane” w źródle nie wystarcza, gdy źródło podaje
  wersję z poprawką („before 2.72.0”, „fixed in”); streszczenie, które
  podaje wersję z poprawką i jednocześnie „brak łatki”, to sprzeczność.
- Lista stylu: „AI-orchestrat*”, „AI-powered”, „AI-driven”,
  „toolkit*”.

Test top 5 na gałęzi (26.10.2026, 12:24): oba modele Gemini
niedostępne (timeout, 503), historie napisał Groq gpt-oss-120b;
„streszczenia wydarzeń 5 z 5”. Lepiej niż dotąd – pojawiły się elementy
historii („exploity 4 dni przed publicznym ujawnieniem”, „kryptominery i
backdoor w postaci proxy”). Słabości: w 3 z 5 historii uwagi o
materiale zamiast faktów („Materiał nie podaje żadnych ataków ani
łatek”, „CISA … nie podaje łatek”, „nie ma informacji o dalszych
atakach ani o dostępnych łatach” przy wycieku kluczy API); błędy słów
i sensu, których kontrola nie łapie („mógł wyczerpać klucze API”,
„aktywnie wykorzystywaną zero‑day”, „Od końca października dostępne są
łatki”, „łatki w pełni blokują RCE” bez kolejnej luki z 24.10); puste
zdanie przy Ariście i pominięty szczegół „trzecia taka luka w cztery
miesiące”. Poprawka (ta sama rodzina co „Nie podano…” z v29 i „nie są
znane” z v33): uwagi „materiał nie…”, „nie podaje…”, „nie ma
informacji…” to ogólniki (na 80 streszczeniach archiwum: 2, obie to
takie uwagi); prompt historii: element bez pokrycia pominąć bez słowa,
łatki tylko przy lukach – przy wycieku, co wyciekło i co zrobić. Błędy
słów i sensu nie dostają reguł: to argument za eksperymentem z modelem
piszącym (Gemini pisze streszczenia dzienne, Groq jako zapas; więcej
materiału) po okresie obserwacji.

Pytanie JW (26.10.2026): czy nie wpadamy w pętlę „test → reguła →
test”? Wniosek: po części tak – kolejne reguły z pojedynczych przykładów
na małych próbkach (tu 3 artykuły z lektury) grożą przeuczeniem i
przeładowaniem promptu. Dlatego reguła o bezosobowym początku („Wykryto…”,
3 z 80 streszczeń) została wycofana, a v34 zamyka się na poprawkach
prawdziwych błędów (fałszywy fakt, za krótki kontekst). Decyzja JW: po
scaleniu 1–2 dni obserwacji zwykłych prasówek bez nowych zmian; dalsze
poprawki tylko na podstawie powtarzających się problemów, nie
pojedynczych zdań.

Nowe i zmienione pliki: `src/ai_summaries.py`, `src/summary_quality.py`,
`src/event_grouping.py`, `src/monthly_top.py`, `src/main.py`,
`src/test_summaries_v34.py` (nowy), `src/test_summary_quality.py`
(limit długości), `data/styl_unikaj.csv`, README (PL/EN).

Testy jednostkowe: 377, zakończone powodzeniem.

Dokończenie v34 (27.10.2026): prasówka z 27.10 nie miała linii
„KONTEKST” w logu. Pięć plików kodu z drugiej paczki (`ai_summaries.py`,
`summary_quality.py`, `event_grouping.py`, `main.py`,
`test_summaries_v34.py`) trafiło przy wgrywaniu do katalogu głównego
repozytorium zamiast do `src`, więc weszło do scalenia v34, ale nie
działało: workflow uruchamia `src/main.py`. Na `main` brakowało więc
kontekstu z 14 dni, blokady fałszywego „brak łatki” i wyłapywania uwag
o materiale. Pliki przeniesione do `src`, kopie z katalogu głównego
usunięte. To trzeci taki przypadek (v22, v26), więc nowy test
`src/test_repo_layout.py` zatrzymuje workflow, gdy w katalogu głównym
pojawi się plik `.py`. Testy jednostkowe: 379.

------------------------------------------------------------------------

## v33 --- 26.10.2026

**Jakość streszczeń i zestawień po prasówce i pierwszym automatycznym
top 5 z 26.10.2026.** Decyzja JW z 26.10.2026: ta wersja zamyka się
na poprawkach jakości, a raport dla CyberSec Mozaika z dziennika języka
(v32) będzie wersją v34, gdy dziennik zbierze dane.

Powód: pierwsza prasówka po v32 (26.10.2026, budzik, 10 artykułów)
wyglądała „kulawo” (JW): formułka „Zaleca się natychmiastową
aktualizację / natychmiastowe zastosowanie łatki” w 4 z 10 streszczeń;
„podatność zero-day” przy luce w Brotli, załatanej 21.10 (pierwszy
potwierdzony przypadek etykiety dopisanej przez AI); „Liczba i rodzaj
naruszonych danych nie są znane”; wydanie PHP 8.5.12 z lektury na górze
„Najważniejszych”, choć PHP2Shell był w prasówkach 22–24.10.

Zmiany:

- **Formułka bez konkretu jako ogólnik** (`src/summary_quality.py`):
  zdanie „Zaleca się (natychmiastową) aktualizację / zastosowanie łatki
  / aktualizację wszystkich wymienionych komponentów.” wraca do
  poprawki, a jeśli zostanie – kod je usuwa. Zalecenie z konkretem
  („… i ograniczenie dostępu do interfejsów zarządzania”, „do wersji
  8.5.12”) zostaje. Prompt: zalecenie tylko konkretne, bez formułki na
  końcu.
- **„zero-day” i „natychmiast…” tylko wtedy, gdy są w materiale**:
  sprawdzanie jak przy liczbach spoza artykułu (w materiale liczą się
  zero-day, 0-day, immediately, urgent, imperative, natychmiast,
  niezwłocznie, pilnie, jak najszybciej itp.). Gdy poprawka AI nie
  pomoże, kod usuwa samo określenie („podatność zero-day CVE-…” →
  „podatność CVE-…”), więc zdanie z faktami zostaje. Korekta językowa
  nie może takich określeń dodać.
- Ogólnik „nie jest / nie są (jeszcze) znane”.
- **„Ciąg dalszy” po CVE ze strony linku z lektury** (`src/main.py`):
  dla artykułów „via Zaufana Trzecia Strona” liczą się też numery CVE
  z pierwszych 2000 znaków pobranej strony (komentarz ZTS jest krótki,
  a post PHP Foundation wymienia CVE-2026-109618 i CVE-2026-109619 po
  pierwszych 600 znakach). Dla zwykłych artykułów bez zmian.

Sprawdzone na streszczeniach z 26.10.2026: reguły łapią trzy formułki
(PHP, Armory Castle, Atlassian) i „nie są znane” (Quest Diagnostics);
zalecenie HPE z konkretem zostaje.

Test na gałęzi `v33-jakosc` 26.10.2026 (7:26): 3 artykuły z 78 (resztę
zabrała poranna prasówka), wszystkie z lektury; żadne streszczenie nie
kończy się formułką, kontrola zgłosiła tylko liczbę „2023” spoza
artykułu (poprawioną przez AI). Usterki: „Negocjatorzy ransomware
(program żądający okupu)” – objaśnienie wygląda, jakby negocjatorzy byli
programem; kalki „AI-hackingowego” i „buildów szyfrujących”.

Poprawki po teście:

- **Objaśnienie ransomware** (`src/glossary.py`): pomijane, gdy
  ransomware określa osoby lub grupy („negocjatorzy / grupy / gang /
  operatorzy / członkowie ransomware”); objaśnienie trafia wtedy do
  dalszego wystąpienia albo do kolejnego streszczenia. „Atak ransomware
  (program żądający okupu)” zostaje jak dotąd. Po czasowniku lub
  przyimku z dopełniaczem objaśnienie jest w dopełniaczu: „użyła
  ransomware (programu żądającego okupu)” – ten sam mechanizm co dla
  exploita i infostealera (v27), formy zgodne z odmianą wygenerowaną
  wcześniej Morfeuszem 2.
- Lista stylu `data/styl_unikaj.csv`: „AI-hacking*” (→ do włamań z
  użyciem AI) i „buildy / buildów / buildami / buildach” (→ wersje,
  kompilacje); bez gołego „build”, żeby nie łapać nazw produktów
  („Build Tools”).

**Poprawki po pierwszym automatycznym top 5** (26.10.2026, 8:17,
`#top-tygodnia`, tydzień 19–25.10). Zestawienie poszło o czasie, ale:
PHP2Shell był dwa razy (pozycja 4 to zapowiedź z 21.10 „… patches
coming tomorrow” ze streszczeniem „Łatki zostaną udostępnione jutro”, a
cztery inne artykuły o PHP2Shell były osobnymi wydarzeniami); pozycja 5
łączyła Fortinet (Sekurak) z FortiSIEM (The Hacker News); w starych
streszczeniach z archiwum zostały „RCE (RCE)”, „exploit tych luk mogą
prowadzić” (mała litera, błędna składnia) i „zero‑day podatność”.
Zestawienia nie łączyły po numerach CVE ani po tytułach artykułów
powiązanych i pokazywały streszczenia z archiwum bez żadnej kontroli.

- **Reguła jednej nazwy** (`src/event_grouping.py`): formy jednej nazwy
  muszą różnić się tylko końcówką („Capcom” / „Capcomu”), więc
  „Fortinet” i „FortiSIEM” (wspólny tylko początek „forti”) się nie
  łączą; nazwy platform (Python) nie łączą także w tej regule (błędne
  połączenie MCP Python SDK z Pillow). Słowa typu produktu (center,
  manager, software, platform, suite…) nie są nazwą firmy (dane z
  26.10: „Siemens Software Center” z „Atlassian … Data Center”).
  Obserwowane od v31 błędne połączenia Fortinet/FortiSIEM i MCP Python
  SDK/Pillow są usunięte.
- **Łączenie w zestawieniach** (`src/monthly_top.py`): wspólny numer
  CVE (zapisany w archiwum albo w tytule lub streszczeniu) albo nazwa
  wydarzenia z cyframi w dowolnym tytule rekordu i wydarzenia, także w
  tytułach artykułów powiązanych; drugi przebieg scala wydarzenia
  rozdzielone przez kolejność. Rekord całej lektury nie łączy po CVE.
- **Lider wydarzenia**: najwyższa punktacja, potem polskie źródło,
  potem najwięcej artykułów powiązanych (PHP2Shell pod tytułem Kapitana
  Hacka zamiast angielskiej zapowiedzi).
- **Streszczenia w zestawieniach**: kod stosuje autopoprawki („RCE
  (RCE)” → „RCE”), wielkie litery i usuwa zdania z problemami („jutro”,
  ogólniki); streszczenie po angielsku albo powtarzające tytuł zastępuje
  streszczenie kolejnego artykułu wydarzenia. Potem jedna korekta
  językowa całego zestawienia (Gemini, zapasowo Groq; jedno zapytanie
  na tydzień lub miesiąc). Workflow `weekly-top.yml` i
  `monthly-top.yml` dostają sekrety `GROQ_API_KEY`, `GEMINI_API_KEY` i
  zmienną `GEMINI_MODEL`; bez nich zestawienie idzie bez korekty.
- **Przeglądy pomijane w zestawieniach**: ThreatsDay i lektura jako
  jedna pozycja, zarchiwizowane przed filtrem z v29.
- **Numery CVE linków z lektury** (`src/kev.py`): dla artykułów „via
  Zaufana Trzecia Strona” liczy się 2000 pierwszych znaków strony linku
  (zamiast 600), więc archiwum zapisuje CVE takiej publikacji (dla 🔥 i
  łączenia w zestawieniach); „Ciąg dalszy” używa tej samej granicy.

Symulacja na archiwum: top 5 za 19–25.10 to PHP2Shell (17 artykułów,
7 serwisów, tytuł Kapitana Hacka, streszczenie bez „RCE (RCE)”), Arista
VCO, Node2Shell, Plex2Shell, OpenCode; bez duplikatu PHP, bez
Fortinet/FortiSIEM i bez ThreatsDay. Grupowanie całego października: bez
utraty trafnych połączeń. Zostaje do korekty AI: „Exploit tych luk mogą
prowadzić” (Plex) – kod poprawia tylko wielką literę.

Nowe i zmienione pliki: `src/summary_quality.py`, `src/ai_summaries.py`,
`src/main.py`, `src/glossary.py`, `src/event_grouping.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/kev.py`,
`src/test_quality_v33.py` (nowy), `src/test_tops_v33.py` (nowy),
`src/discord_output.py`, `.github/workflows/weekly-top.yml`,
`.github/workflows/monthly-top.yml`, `data/styl_unikaj.csv`, README
(PL/EN).

Drugi test na gałęzi (26.10.2026, 10:50) – prasówka i top 5 uruchomione
z gałęzi na kanał testowy. Top 5 zgodny z symulacją, a korekta Gemini
poprawiła „Exploity tych luk mogą prowadzić” i „podatność zero-day”.
Prasówka: lista stylu złapała „rekordów”, „Breaches”, „AI‑napędzany”,
„eksploatacji”, „AI‑zarządzany” i „buildów”. Nowe usterki: pusty
nagłówek „🔁 CIĄG DALSZY (cd.)” nad samą stopką; „46 własnych wersji,
kompilacji szyfrujących” (AI wpisało obie podpowiedzi z listy stylu);
„4,1 mln danych” (dane są niepoliczalne); „firm negocjujących
ransomware (program żądający okupu)”.

- **Podział na wiadomości** (`src/discord_output.py`): pusta linia, po
  której nie ma już numerowanej pozycji, kończy sekcję, więc stopka nie
  dostaje nagłówka „(cd.)”; sekcja zestawienia (pusta linia pod
  nagłówkiem) dalej się kontynuuje.
- **Podpowiedzi z listy stylu jako alternatywy**
  (`src/summary_quality.py`, `src/ai_summaries.py`): „wersji,
  kompilacji” trafia do AI jako „wersji albo kompilacji (wybierz jedno
  słowo, nie wpisuj obu)”; plik listy bez zmian w tej sprawie.
- Lista stylu: „mln / tys. / mld danych” → „wpisów” (dane są
  niepoliczalne).
- Objaśnienie ransomware pomijane także po „negocjujących” (rdzeń
  „negocj”).

Do obserwacji (sens, nie forma – kod tego nie wykryje): streszczenie
VeraCrypt opisuje mechanizm, ale pomija sedno (utrata znacznika Mark of
the Web); w PHP2Shell zdanie bez podmiotu („podatności … potwierdzono
ich wykorzystywanie”), którego korekta nie poprawiła.

Dziennik porządków w zestawieniach (`src/ai_summaries.py`,
`src/monthly_top.py`, `src/weekly_top.py`): każda zmiana streszczenia
zrobiona przez kod trafia do logu workflow jako „PORZĄDEK: wydarzenie
N – …” (autopoprawka, usunięte zdanie z powodem, streszczenie pominięte
jako angielskie albo powtarzające tytuł) i podsumowanie „streszczenia
zmienione przez kod: N z M”. Wcześniej porządkowanie było ciche, a log
zestawienia pokazywał tylko korektę („KOREKTA: …”). Symulacja na top 5
z 19–25.10: „RCE (RCE)” → „RCE” (PHP2Shell) i pominięte streszczenie po
angielsku (Node2Shell) – 2 z 5.

Testy jednostkowe: 346, zakończone powodzeniem.

------------------------------------------------------------------------

## v32 --- 25.10.2026

**Dziennik języka: poprawki językowe streszczeń zapisywane w archiwum.**

Powód: do v31 poprawki językowe istniały tylko w logu uruchomienia
(„KONTROLA: …”, „KOREKTA: przed/po”). Log znika po 90 dniach i nie da
się go policzyć, więc nie było danych do raportów dla CyberSec Mozaika.
Decyzja JW z 25.10.2026: najpierw załatać tę lukę (v32), a raporty dla
Mozaiki zrobić w v33.

Zmiany:

- **Notatki językowe przy artykule** (nowy `src/language_notes.py`):
  każdy dostarczony artykuł ma w archiwum pole `language` z listą
  poprawek jego streszczenia. Rodzaje: `glossary` (forma zakazana
  zamiast wymaganej, z numerem hasła H), `style` (kalka z listy
  `data/styl_unikaj.csv`), `inflection` (termin w formie podstawowej po
  przyimku, np. „przed exploit”, z numerem hasła), `autofix` (zamiana
  przez kod bez zapytania do AI, z numerem hasła, gdy reguła wynika ze
  słowniczka) i `proofreading` (streszczenie przed i po korekcie oraz
  model, który ją zrobił).
- **Wynik poprawki** (`fixed_by`) przy formach ze szkicu AI: `ai`
  (poprawiło AI), `code` (kod usunął zdanie), `remains` (forma została w
  streszczeniu – możliwe tylko przy kalkach, które nigdy nie skracają
  streszczenia) albo `dropped` (streszczenie odrzucone; notatki zostają
  przy artykule).
- `src/glossary.py`: reguły autopoprawek mają przypisaną formę ze
  słowniczka (łatka, RCE, exploit) albo nazwę reguły; nowe funkcje
  `entry_by_form` i `violation_entries` (forma zakazana razem z hasłem).
  `src/summary_quality.py`: kalki i nieodmienione terminy dostępne jako
  dane (`style_hits`, `uninflected_hits`).
- Log: „JĘZYK: uwagi językowe do archiwum – słowniczek N, styl N,
  odmiana N, autopoprawki N, korekta N”.
- Notatki opisują tylko to, co napisało AI: niczego nie zmieniają w
  streszczeniu i nie zapisują nic do glosariusza. Uruchomienia testowe
  niczego nie zapisują, jak dotąd.

Sprawdzone na prawdziwych błędach z logów 22–25.10.2026: „rekordy
pacjentów” i „AI‑zarządzanego” (styl), „patchują” (słowniczek, H166),
„przed exploit” (odmiana, H153), „eksploatując”, „intruzji”,
„Kompromisy”, „rootowy” (styl) – wszystkie zapisane.

Test na gałęzi `v32-jezyk` 25.10.2026: streszczenia AI 9 z 9, korekta
poprawiła 7; log „JĘZYK: … słowniczek 0, styl 2, odmiana 0,
autopoprawki 2, korekta 7” zgodny z liniami KONTROLA i KOREKTA. „Ciąg
dalszy” miał 6 z 9 pozycji. Pięć było trafnych (PHP, Arista VCO,
BeyondTrust/Armory Castle, Brotli/Node.js, Quest Diagnostics), ale
analiza Unit 42 o FortiManagerze trafiła tam przez CVE-2024-47575 z
całej lektury 699, dostarczonej 24.10 jako jedna pozycja. Do tego w
streszczeniach: „eliminują ryzyko ataków” (ogólnik), „75 unikalnych
podatności” i „wpływających na wersje” (kalki).

Poprawki po teście:

- **„Ciąg dalszy” po CVE pomija rekordy całej lektury** (`src/main.py`):
  ich numery CVE pochodzą z dziesiątek różnych linków, więc nowa analiza
  jednego z nich nie jest kontynuacją wydarzenia.
- Ogólnik „eliminuje ryzyko / zagrożenie” (`src/summary_quality.py`).
- Lista stylu `data/styl_unikaj.csv`: „unikaln*” (→ różny albo bez
  przymiotnika) i „wpływając* na wersj*” (→ dotyczący wersji).

Nowe i zmienione pliki: `src/language_notes.py` (nowy),
`src/test_language_notes.py` (nowy), `src/ai_summaries.py`,
`src/glossary.py`, `src/summary_quality.py`, `src/article_archive.py`,
`src/main.py`, `src/test_roundup_parts.py`, `data/styl_unikaj.csv`,
README (PL/EN).

Testy jednostkowe: 307, zakończone powodzeniem.

------------------------------------------------------------------------

## v31 --- 25.10.2026

**Rozbiór „Weekendowej lektury” na linki, łączenie tematów po nazwach
firm, alarm przy błędzie workflow.**

- **„Weekendowa lektura” rozbierana na części** (nowy
  `src/roundup_parts.py`, `src/main.py`): zgodnie z pierwotnym zamysłem
  JW (25.10.2026) przegląd ZTS nie jest jedną pozycją, tylko źródłem
  linków. Każdy element listy lub akapit z linkiem do innego serwisu
  staje się kandydatem do prasówki (tytuł: tekst linku albo początek
  komentarza; opis: komentarz ZTS) i przechodzi tę samą punktację,
  próg, odrzucanie opublikowanych linków i łączenie wydarzeń. W
  prasówce najwyżej 3 takie linki (`LEKTURA_LIMIT` w
  `src/article_selection.py`), podpisane „via Zaufana Trzecia Strona”;
  archiwum zapisuje pole `via`. Log wypisuje znalezione pozycje
  („WEEKENDOWA LEKTURA: N pozycji”, „LEKTURA: …”). Gdy w treści nie ma
  takich linków (zmiana układu), lektura zostaje jedną pozycją ze
  stałym opisem jak w v29.
- **Łączenie po nazwach firm i produktów** (`src/event_grouping.py`,
  `src/monthly_top.py`): w tytułach pisanych wielkimi literami (Title
  Case) każde słowo jest wielką literą, więc dotychczasowa reguła nazw
  nic nie widziała (Quest Diagnostics i Capcom dwa razy w prasówkach z
  23–24.10). Nowe reguły: wspólna para wyrazów z wielkiej litery,
  niegenerycznych i rzadkich w puli („Quest Diagnostics”); pojedyncze
  wspólne słowo tylko wtedy, gdy teksty artykułów (opisy, polskie
  streszczenia) pokazują, że to nazwa – zawsze wielką literą, nigdy
  małą („Capcom”); nazwy platform występujące w różnych historiach
  (Microsoft, Windows, Chrome, Python, WordPress…) nigdy nie łączą
  same. Działa w prasówce, „Ciągu dalszym” i zestawieniach.
- **Alarm przy błędzie** (`.github/workflows/daily-digest.yml`,
  `weekly-top.yml`, `monthly-top.yml`): gdy workflow zakończy się
  błędem, na kanał testowy przychodzi komunikat „⚠️ … workflow
  zakończył się błędem” z linkiem do logu – właściciel dowiaduje się o
  awarii przed czytelnikami.
- Drobna zmiana: uwagi „… nie została podana / ujawniona / wskazana”
  zgłaszane jak ogólniki („Liczba poszkodowanych nie została podana”,
  test v30).

Sprawdzono na archiwum października (70 artykułów): zestawienie łączy
teraz Quest Diagnostics, Capcom i Arista VCO, bez nowych błędnych
połączeń (dwa połączenia z wcześniejszych reguł – Fortinet/FortiSIEM i
MCP Python SDK/Pillow – zostają do obserwacji).

Nowe i zmienione pliki: `src/roundup_parts.py` (nowy),
`src/test_roundup_parts.py` (nowy), `src/main.py`,
`src/article_selection.py`, `src/discord_output.py`,
`src/article_archive.py`, `src/event_grouping.py`,
`src/test_event_grouping.py`, `src/monthly_top.py`,
`src/summary_quality.py`, trzy workflowy, README (PL/EN).

Test na gałęzi `v31-lektura` 25.10.2026: Weekendowa Lektura odcinek
699 rozebrana na 53 pozycje z polskimi tytułami ZTS; do prasówki weszły
3 (m.in. Krebs o negocjatorze współpracującym z ShinyHunters); link do
subskrypcji, YouTube i Discord odpadły przez próg trafności. Wady:
weszła publicystyka („Najbezpieczniejsza przeglądarka 2026? …”, +3 za
„zero-day”), a odpadły analizy zagrożeń bez słów kluczowych w tytule
(Unit 42, ESET, Mandiant, Microsoft, Securelist); pozycja o PHP z
lektury trafiła do „Najważniejszych”, choć PHP2Shell był już w
prasówce (komentarz ZTS nie ma numeru CVE, tytuł – nazwy).

Poprawki przed scaleniem (decyzja JW: od razu, przed v32):

- **Pytajnik w tytule linku z lektury** = publicystyka: kara jak za
  kontekst wydarzeń/poradników (`has_context_title`); tylko dla
  lektury, bo w zwykłych kanałach pytajnik bywa w newsach
  („Fakturownia zhakowana?”).
- **Premia +2 dla linków z lektury do publikacji badawczych**
  (`ANALYSIS_SOURCES`: Unit 42, Securelist, ESET WeLiveSecurity,
  Google/Mandiant Threat Intelligence, Microsoft Security Blog, Sophos,
  Sekoia, Zscaler, Symantec, Check Point Research, Talos, CrowdStrike,
  Proofpoint, Elastic Security Labs, Huntress, GreyNoise, Hunt.io,
  CERT Polska), więc analizy bez słów kluczowych w tytule przechodzą
  próg.
- **Pomijane linki bez treści artykułu**: z3s.pl (skrót ZTS), YouTube,
  Discord, X/Twitter, Facebook, LinkedIn, Instagram, TikTok, Telegram
  (dopasowanie domeny lub subdomeny, nie końcówki – „x.com” to nie
  „netflix.com”).
- **„Ciąg dalszy” po numerach CVE ze streszczeń** (`src/main.py`):
  po streszczeniach artykuł, którego streszczenie ma numer CVE z
  rekordu archiwum z ostatnich 3 dni, trafia do „Ciągu dalszego”.

Symulacja na tytułach lektury 699: na górze rankingu Nginx, PHP, Unit 42
o FortiManagerze, Mandiant o Armory Castle; „Najbezpieczniejsza
przeglądarka” spada poniżej progu. Testy jednostkowe: 290, zakończone
powodzeniem.

Dokumentacja przed scaleniem: README (PL/EN) napisane od nowa na stan
v31. Usunięte nieaktualne stany (budzik „oczekuje na potwierdzenie”,
grupowanie „jeszcze nie wystąpiło na żywo”, wyniki v13 z 69 testami,
„planowane przetwarzanie AI”); tabela 16 etapów z wersjami; opis
podzielony na sekcje (źródła i selekcja, wydarzenia i znaczniki,
streszczenia AI, wysyłka i zestawienia, wyzwalacze); aktualne
ograniczenia i plan rozwoju (most do Mozaiki, v32). Polskie README
dostało brakujące sekcje: architekturę, strukturę repozytorium,
konfigurację i sekrety, testy. Sekcja „Stan projektu wynikający z
przeanalizowanej historii” na końcu changelogu jest oznaczona jako
zapis historyczny po v10.

## v30 --- 25.10.2026

**„Polacy nie gęsi”: korekta językowa Gemini, podpowiedzi
LanguageTool, prostsze zdania.**

Powód: w teście v29 (25.10.2026) korekta (gpt-oss-120b) poprawiła 5 z
6 streszczeń, ale zostały błędy rekcji i uzgodnienia, które gubią sens:
„CISA dodało do listy KEV dwóch podatności” (powinno być: „CISA dodała
… dwie podatności”) i „Exploit CVE-2026-110447 umożliwia backdoor”.
Modele Groq piszą po polsku zbyt słabo, by to wyłapać. Uzupełnienie
v29: drugi test na gałęzi `v29-jezyk` dał „KOREKTA: poprawione językowo
5 z 6 streszczeń” po przejściu korekty na gpt-oss-120b.

Decyzja JW z 25.10.2026: korekta przez Google Gemini w ramach
darmowego limitu (projekt „PolacyNieGesi4Digest”, bez płatności;
sekret `GEMINI_API_KEY`). Przyjęto do wiadomości zapis warunków Gemini
API o planie płatnym dla aplikacji udostępnianych użytkownikom w EOG –
z API korzysta tylko automat na GitHubie, a w EOG nawet darmowe użycie
podlega zasadom planu płatnego (treści nie są używane do trenowania);
przy problemie korekta wraca do Groq.

Zmiany:

- **Korekta przez Gemini** (nowy `src/gemini.py`): modele
  `gemini-3.8-flash`, zapasowo `gemini-3.5-flash` (odczytane z AI
  Studio; zmienna repozytorium `GEMINI_MODEL` może je podmienić). Klucz
  w nagłówku `x-goog-api-key`, nigdy w adresie ani w logu. Kolejność:
  Gemini → gpt-oss-120b → qwen3.8-27b; po wyczerpaniu darmowego limitu
  (błąd 429) korekta przechodzi na Groq, a prasówka działa dalej. Jedno
  zapytanie dziennie.
- **Podpowiedzi LanguageTool** (nowy `src/languagetool.py`): wszystkie
  streszczenia sprawdzane jednym zapytaniem do publicznego API
  LanguageTool (pl-PL, bez klucza); uwagi z kategorii gramatyka,
  interpunkcja, mylone słowa i semantyka trafiają do korekty jako
  „uwagi” przy konkretnym streszczeniu (literówki są pomijane, bo to
  zwykle nazwy techniczne). Kod nie stosuje ich sam.
- **Prompt streszczeń**: krótkie, proste zdania (do ok. 20 słów, jedno
  zdanie – jeden fakt), uzgadnianie czasownika z podmiotem („CISA
  dodała”, „Microsoft wydał”), biernik po „dodać/wydać/załatać”, numer
  CVE to luka, a nie exploit.
- **Prompt korekty**: rekcja i uzgodnienie na przykładzie z testu,
  przeformułowanie niejasnego zdania przy zachowaniu faktów, możliwość
  podziału długiego zdania.
- **Log „przed → po”** dla każdego poprawionego streszczenia oraz
  nazwa modelu, który zrobił korektę.

Nowe i zmienione pliki: `src/gemini.py` (nowy), `src/languagetool.py`
(nowy), `src/test_proofreading.py` (nowy), `src/ai_summaries.py`,
`.github/workflows/daily-digest.yml` (sekret `GEMINI_API_KEY`,
zmienna `GEMINI_MODEL`), README (PL/EN).

Zmianę zweryfikowano: testy jednostkowe (277) zakończone powodzeniem.
Test na gałęzi `v30-Polacy` 25.10.2026: korektę zrobił
`gemini-3.8-flash` (klucz i nazwa modelu działają), poprawione 6 z 6
streszczeń, żadna poprawka nie odrzucona. Przykłady z logu „przed →
po”: „Exploit CVE-2026-110447 umożliwia instalację backdoora” → „Luka
CVE-2026-110447 pozwala zainstalować backdoora”; „łatki dla 72
podatności…, w tym osiem krytycznych luk” → „ośmiu krytycznych luk”;
„Atlassian wydało” → „Atlassian wydał”; „wyciekiem niektórych wpisów
pacjentów” → „wyciekiem danych niektórych pacjentów”; „kolejne
aktualizacje pojawiają się w kolejnych produktach” → bez powtórzenia.
LanguageTool nie zgłosił uwag (0 z 6), mimo błędów przypadku – jego
polskie reguły są słabe, więc główną pracę robi Gemini. Do dalszej
obserwacji: uwaga „Liczba poszkodowanych nie została podana” (forma
„nie została podana” nie jest jeszcze wykrywana). Rozbiór „Weekendowej
lektury” i łączenie po nazwach firm przechodzą do v31.

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
w tym przykłady z prasówek z 23–24.10.2026. Łączenie tematów po nazwach
firm w tytułach (Quest Diagnostics, Capcom) zostaje na kolejną wersję.

Test na gałęzi `v29-jezyk` 25.10.2026 (niedziela, 6 artykułów):
wszystkie streszczenia po polsku, bez kalek i ogólników, z konkretami;
katalog KEV pobrany (1756 pozycji), oznaczony 1 artykuł; runda korekty
nie zmieniła żadnego streszczenia („poprawione językowo 0 z 6”), choć
zostały błędy („dotykających wersje”, „nieokreśloną liczbę danych”).

Poprawki po teście (decyzje JW z 25.10.2026):

- Korekta językowa najpierw głównym modelem (gpt-oss-120b), drugim
  dopiero przy błędzie; prompt korekty dostał listę typowych błędów z
  przykładami (przypadek po imiesłowie, rodzaj i liczba, kalki,
  składnia bezosobowa).
- „wykonanie kodu zdalnie” (odwrócona kolejność) → „RCE”, zgodnie ze
  słowniczkiem.
- Po „typu”/„rodzaju” objaśnienie „podwyższenia uprawnień” w
  mianowniku: „luk typu podwyższenie (eskalacja) uprawnień”.
- Lista stylu: „liczb* danych” → „zakres danych, wolumen danych”.

Testy jednostkowe po poprawkach: 270, zakończone powodzeniem.

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

## Stan projektu wynikający z przeanalizowanej historii (zapis historyczny po v10)

Zapis stanu z odtworzenia historii v1–v10; nie opisuje obecnego stanu.
Aktualny stan projektu: [README_PL.md](README_PL.md).

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

## v40 · Two parentheses --- 2026-11-07

**Explanations in parentheses for two terms only (mirror v92).**

Reason: the author's first decision from the bridge span P8 ·
Rozbieżności (Discrepancies) (Letter 18, 2 November 2026). Since mother workbook v92 the H182 and
H207 explanations come from its language block, not from exceptions in
the bridge code (Letters 21–22). An explanation
in parentheses stays only where the Polish term may be unclear:
"podwyższenie (eskalacja) uprawnień" (H182) and "poświadczenia (dane
logowania)" (H207). Exploit, botnet, ransomware and infostealer (H153,
H004, H015, H019) are clear to digest readers without one; wiper (H723)
had none.

Changes:

- **Mirror v92** `data/glosariusz_mirror.csv` from the bridge exporter
  (runbook step K5: new mirror to the digest), one mirror instead of two
  (Letter 22): empty `nawias` column for H004, H015, H019 and H153,
  header `plik-matka v92 · 2026-11-03`.
- **Explanation code** (`src/glossary.py`): removed the inflected
  explanations for exploit, botnet and infostealer, the case-dependent
  explanation for ransomware and the rule skipping "ransomware" after
  people and groups (v33). The exploit, botnet and infostealer form
  tables stay as a test set for the inflected forms planned in the
  mother workbook (Letter 16, point 3a). Explanations still come from
  the mirror data, so restoring one in the mother workbook needs no code
  change (except for case-dependent inflection).
- **Tests:** explanation examples moved to H182 and H207; a new test
  checks that exploit, botnet, ransomware, infostealer and wiper stay
  without parentheses. 441 tests in total.

Changed files: `data/glosariusz_mirror.csv`, `src/glossary.py`,
`src/test_glossary.py`, `src/test_quality_v33.py`,
`src/test_discord_output.py`, README (PL/EN).

------------------------------------------------------------------------

## v39 --- 2026-11-02

**Guards for the last two data lines read by the bridge, and the
`proofread` field.**

Reason: the analysis of the "Linie styku" graph in the bridge carton
(Letter 13). The bridge report (`bridge_report.py` in `cybersec-most`)
reads four digest files, and the v38 contract test guarded only two: the
archive and the mirror. The tops (`data/tops/`, for the span P4 · Live
examples) and the style list (`data/styl_unikaj.csv`, for P3 · Calques)
had no guard. The bridge also wants to prefer sentences that passed the
language correction when choosing live examples (Letter 14).

The first top saved by v38 (`data/tops/2026-W44.json`, 2 November 2026)
served as real test material.

Changes:

- **Tops contract test** (`src/test_v39.py`): every file in `data/tops/` –
  a list with consecutive ranks from 1, all fields, `kind` (`week`/`month`)
  matching the period format, period matching the file name, number and
  list types.
- **Style list format test:** header exactly `forma;zamiast`, separator
  `;`, `#` comments, a star only at the end of a word – the way the bridge
  report reads the file.
- **`proofread` field** (`src/ai_summaries.py`, `src/article_archive.py`):
  the name of the model that checked the summary in the language
  correction, or empty text when there was no correction (e.g. Gemini and
  Mistral unavailable). Records from before v39 have no such field – the
  bridge tells the two cases apart.

New and changed files: `src/ai_summaries.py`, `src/article_archive.py`,
`src/test_v39.py` (new), README (PL/EN).

Unit tests: 443, passed.

------------------------------------------------------------------------

## v38 --- 2026-11-01

**Data for the bridge to CyberSec Mozaika: glossary entries in the
archive, saved tops, data contract test; mirror v90; exporter in the
bridge repository.**

Reason: the agreements between the digest and Mozaika (Letters 1–11 in
`cybersec-most`) and the trial bridge report of 1 November 2026. The
report (`bridge_report.py` in the private repository `cybersec-most`)
reads the digest's data, not its code. It lacked two things: which
glossary entries an article contains (summaries are inflected, so
matching forms on the bridge side would be unreliable), and the tops,
which until now existed only on Discord.

Changes:

- **`terms` field in the archive** (`src/article_archive.py`,
  `src/glossary.py`): IDs of mirror entries (H###) found in the title and
  summary, with the same matching as the prompt glossary.
- **Saved tops** (`src/monthly_top.py`, `src/weekly_top.py`): delivered
  top 5 and top 10 go to `data/tops/YYYY-Www.json` and `YYYY-MM.json`
  (rank, title, link, summary, story model, numbers of articles and
  sources, KEV, CVE ids, links). The file is written together with the
  marker, so not on branch test runs. Log: "ZAPIS ZESTAWIENIA".
- **Data contract test** (`src/test_v38.py`): archive record fields,
  language note fields by type, `fixed_by` values, the six mirror
  columns and the mirror header.
- **File placement test:** only code in `src/`, no `.py`/`.csv`/`.json`
  files in the root. On 1 November the v90 mirror landed in `src/`, the
  digest kept reading v84, and every test passed.
- **Mirror exporter removed** (`tools/eksport_mirrora.py`): it now lives
  in `cybersec-most` with `OVERRIDES`, because it reads the private
  mother workbook.
- **Live log:** `PYTHONUNBUFFERED=1` in the digest and top workflows (on
  31 October the step looked stuck, because the log appeared only at the
  end).
- **Glossary licence** in both READMEs (CC BY-NC-ND 4.0, © Jan Wolski).

Small change of 1 November (separately, before v38): mirror refreshed to
mother workbook v90 – 740 entries (14 new UKC entries, H727–H740), the
six runtime columns, a header with the version, ISO date and CC
attribution.

New and changed files: `src/article_archive.py`, `src/glossary.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/ai_summaries.py`,
`src/test_v38.py` (new), `tools/eksport_mirrora.py` (removed),
`.github/workflows/daily-digest.yml`, `weekly-top.yml`,
`monthly-top.yml`, README (PL/EN).

Unit tests: 436, passed.

------------------------------------------------------------------------

## v37c --- 2026-10-31

**The API's reason for a refusal in the log; Ministral as the Mistral
model; reading Ministral's answers.**

Reason: in the weekly top tests of 31 October 2026 Mistral answered "HTTP
Error 403: Forbidden" – also for `mistral-large-2512` from the free-tier
limits list, with the training consent on and no access restrictions in
the organization. The log showed only the code, without a reason.

Changes:

- **Reason for a refusal in the log** (`src/ai_summaries.py`): on HTTP 4xx
  errors (except 404 and 429) the log gets the first 200 characters of
  the API response, e.g. "KOREKTA: Mistral … niedostępny … | odpowiedź
  API: {…}". The key never goes to the log.
- **Default Mistral model** (`src/mistral.py`): `ministral-14b-2512`. The
  new log showed the reason for the 403: `mistral-large-2512` is on the
  limits list but not in the free tier ("This model is not available in
  your subscription tier"); `mistral-medium-latest` has 20,000 tokens per
  minute, less than one event-story request (429). Ministral (937,500
  tokens per minute) wrote the first real event stories, e.g. PHP2Shell
  from the honeypot to Mirai, Arista "the third such flaw in four months"
  from a later article. The variable `MISTRAL_MODEL` still overrides it.
- **An empty answer is a failure** (`src/ai_summaries.py`): test with
  `ministral-14b-2512` – the model answered, but not a single story could
  be read from the answer, and the code took it as a success and did not
  try the next model ("ZESTAWIENIE AI: pominięte"). Now such a chunk goes
  to the next model, the log shows the start of the answer, and reading
  accepts ids as text ("1"), the key "wydarzenia" and the field "historia"
  instead of "tekst" (the way `ministral-14b-2512` answers).

New and changed files: `src/ai_summaries.py`, `src/mistral.py`,
`src/test_v37c.py` (new), README (PL/EN).

Unit tests: 427, passed.

------------------------------------------------------------------------

## v37b --- 2026-10-31

**The tops use the same chain as the digest.**

Reason: before the first monthly top 10 (1 November 2026) – design
consistency after v37a. The correction of the top summaries already used
the new chain in v37a (`proofread_top` calls `proofread_summaries`), but
the top workflows did not get the Mistral secret, and the event stories
(`summarize_events`) went the old way: one request, Gemini in one round,
then Groq.

Changes:

- **Event stories in chunks and rounds** (`src/ai_summaries.py`): Gemini
  main, Mistral, Gemini lite, and from the second round Groq as the last
  writer. Mistral before lite, unlike in the correction: in the branch test
  `gemini-3.5-flash-lite` wrote every story like a summary of one article
  (PHP2Shell: 17 articles, nothing after 22.10) – lite is enough for the
  correction, not for putting a story together from many articles – it writes the daily summaries anyway, and every story is
  checked against the event material. Log: "ZESTAWIENIE AI: 1–5 – model
  …".
- **Weekly and monthly workflows** get `MISTRAL_API_KEY`,
  `GEMINI_LITE_MODEL` and `MISTRAL_MODEL`.
- The correction of the tops also works with the Mistral key alone.

New and changed files: `src/ai_summaries.py`, `src/test_v37b.py` (new),
`.github/workflows/weekly-top.yml`, `.github/workflows/monthly-top.yml`,
README (PL/EN).

Unit tests: 420, passed.

------------------------------------------------------------------------

## v37a --- 2026-10-31

**Language correction every day: chunks, Gemini lite, Mistral; no empty
"two other flaws".**

Reason: the digests of 30 and 31 October 2026 went out without
correction (JW: "I would rather have a correction that runs every
day"). Logs: both Gemini models unavailable in both rounds – timeouts
and 503, not a single 429, so overload on Google's side, not a used-up
quota. Without correction, "grupa wyciekła dane", "10 august 2023" and
"nie zostały załatwione" got through. Also "oraz dwie inne luki" ("and
two other flaws") in 5 summaries – an empty mention suggested by the
request to limit CVE ids itself.

Changes:

- **Correction in chunks of 5 summaries** (`src/ai_summaries.py`): a short
  answer fits in 30 s even under load, and a lost chunk does not take the
  correction away from the others.
- **Lighter Gemini models** (`src/gemini.py`): `gemini-3.8-flash-lite`,
  `gemini-3.5-flash-lite` after the main models; separate capacity. The
  repository variable `GEMINI_LITE_MODEL` overrides the names.
- **Mistral as the last fallback** (`src/mistral.py`, new): free plan
  without a card, secret `MISTRAL_API_KEY`, model `mistral-large-latest`
  (variable `MISTRAL_MODEL`). It joins from the second round – Gemini goes
  first. No Groq, as since v35.
- **Three rounds with a growing wait** (30 s, 60 s); a model that failed is
  skipped for the rest of the round, so the run does not wait for it on
  every chunk. Log: "KOREKTA: streszczenia 1–5 – model …", "KOREKTA:
  runda 2 za 30 s", "KOREKTA: bez korekty N z M streszczeń".
- **No "and two other flaws"** (prompt, `src/summary_quality.py`): extra
  flaws are named by their type from the article or left out; an empty
  mention goes back for correction as a soft problem.

The bridge to CyberSec Mozaika moves to v38.

New and changed files: `src/ai_summaries.py`, `src/gemini.py`,
`src/mistral.py` (new), `src/summary_quality.py`,
`src/test_proofreading.py`, `src/test_v37a.py` (new),
`.github/workflows/daily-digest.yml`, README (PL/EN).

Unit tests: 415, passed.

------------------------------------------------------------------------

## v36 --- 2026-10-29

**Soft problems never cut a summary; no headless fragments; less
telegraphic; "z/ze" right; no added phishing.**

Reason: the digest of 2026-10-29 (JW: "still a bit lame, though a bit
better … choppy"). The Gemini correction worked (12 of 15,
`gemini-3.5-flash` in the v35 retry). Problems:

- Oracle E-Business Suite: "Luka umożliwia … RCE po jej załataniu." – the
  draft had only the calque "eksploatację" (a soft problem), the AI
  correction got a hard problem, and code cut the corrected version,
  removing the first sentence with the product name;
- "ze włączoną funkcją" – an error of the v35 autofix ("ze" before every
  "w" with a consonant);
- choppy text: the v34 prompt ("short simple sentences, one sentence –
  one fact") and splitting sentences over 25 words gave a row of short
  sentences without conjunctions, sometimes a verbless fragment ("W tym
  cztery krytyczne błędy…");
- an added effect: "co może umożliwić kampanie phishingowe" (Burger King;
  on 27 October "zwiększa ryzyko phishingu" for Copenhagen).

Changes:

- **A draft with only soft problems stays** (`src/ai_summaries.py`) when
  the AI correction is not clean – code does not cut the corrected
  version.
- **No first sentence – no summary**: if the code repair would remove the
  first sentence (the subject: product, company, group), the article
  goes with its title only. Log: "KONTROLA: streszczenie N odrzucone (kod
  usunąłby pierwsze zdanie)".
- **"Ze" before "w" only with a sibilant** (`src/glossary.py`): "ze
  wsparciem", "ze wszystkimi", "ze względu"; "z włączoną", "z wnukiem"
  unchanged.
- **Smoother** (prompt, `src/summary_quality.py`): sentences up to about
  25 words, related facts joined with conjunctions ("bo", "więc", "ale",
  "a"); every sentence has a verb; split requested only above 30 words
  (was 25).
- **Phishing and social engineering only from the article**: a mention
  without support in the material goes back for correction (on the
  archive: 2 additions caught, 2 real mentions pass).

The bridge to CyberSec Mozaika moved to v37.

New and changed files: `src/ai_summaries.py`, `src/summary_quality.py`,
`src/glossary.py`, `src/test_v36.py` (new), README (PL/EN).

Unit tests: 404, passed.

------------------------------------------------------------------------

## v35 --- 2026-10-28

**One vulnerability – one item; correction by Gemini only; advice only
when concrete.**

Reason: the digests of 27 and 28 October 2026 after v34 (JW: "it read a
bit hard, the Polish limps, it pushes filler too … a bit embarrassing,
my mentors read it"). Problems collected during the observation and
checked in the archive:

- the same vulnerability several times: Brotli CVE-2026-111497 in three
  items (27 October), Apple CVE-2026-86950 in two (28 October) – the
  second day in a row;
- the language correction by Groq (Gemini unavailable for the third time
  in three days) made the text worse: "starsze iPhone’y i iPad’y" →
  "starsze iPhone’ów i iPad’ów", "Exploity PoC pojawiły się" →
  "Exploitów PoC pojawiły się", "uni‑związany" → "niezależny" (meaning
  changed);
- advice in the imperative in 6 of 13 summaries, often empty
  ("Zainstaluj najnowsze wersje systemów, aby usunąć te luki", "Postępuj
  zgodnie z zaleceniami GMO", "Zaleca się aktualizację wtyczki po jej
  wydaniu") – a side effect of the v34 prompt ("sentence 3: what to
  do");
- remarks about the article ("Artykuł opisuje…", "Brak dostępnych łatek
  w artykule"); "w wtyczce", "z wsparciem", "łaty";
- "twofactorgauthenticator" instead of "twofactor_gauthenticator";
- "Bezpłatne e-dzienniki z lukami w przepisach" in "Podatności", the
  column "This is Fine: What NetScaler Zero-Days Tell Us…" in
  "Najważniejsze".

Changes:

- **Merging by CVE ids after the page texts** (`src/event_grouping.py`,
  `merge_by_cves`, `src/main.py`): event grouping ran before the article
  pages were fetched, and many feeds give only a teaser without the CVE
  id. After the pages and KEV markers, selected articles sharing a CVE
  id become one item (the one with the higher score leads, a Polish one
  on ties); a second pass after the summaries also uses CVE ids from the
  summaries (SecurityWeek named the Apple CVE after the first 600
  characters of its page). Log: "SCALENIE PO CVE (ze stron / ze
  streszczeń): N". The roundup is never merged.
- **CVE ids with a non-breaking hyphen** (`src/kev.py`,
  `src/summary_quality.py`, `src/ai_summaries.py`): the AI often writes
  "CVE‑2026‑86950" with U+2011; code looked only for a plain "-", so
  merging, KEV and the fact check did not see such ids (10 of 110
  October summaries). All variants are recognized, and cleaning a
  summary turns them into "-".
- **Language correction by Gemini only** (`src/ai_summaries.py`): one
  more round after 30 s on a temporary error (503, timeout); when Gemini
  is unavailable, the summaries stay uncorrected – no fallback to Groq.
  Event stories in the tops (writing, not correcting) keep Groq as a
  fallback.
- **Advice only when concrete** (prompt): sentence 3 optional, only with
  a concrete action (fixed version, workaround, what to disable),
  descriptive ("Poprawka jest w wersji 6.2606.4246."), not imperative.
  In the check: advice without content ("najnowsze wersje", "udostępnione
  łatki", "zgodnie z zaleceniami", "po jej wydaniu") counts as filler;
  the imperative at the start of a sentence is a soft problem (asked to
  rephrase, never cut).
- **Remarks about the article** count as filler: "artykuł opisuje /
  omawia / przedstawia…", "w artykule"; "brak dostępnych łatek" like
  "brak łatki".
- **Autofix** (`src/glossary.py`): "w"/"z" → "we"/"ze" before a lowercase
  word starting with a consonant cluster ("we wtyczce", "we wszystkich",
  "we francuskich", "ze wsparciem", "ze szkoły"); the digraphs sz, rz,
  cz, dz count as one sound ("z szybkiego" stays); names and acronyms
  unchanged ("z SQL", "w Wrocławiu"). "Łata / łaty / łatę…" → "łatka /
  łatki / łatkę…".
- **Underscore in names** stays ("twofactor_gauthenticator"); only an
  "_" that could start or end Markdown formatting is removed.
- **Selection** (`src/article_selection.py`): context penalty for "luk w
  przepisach / prawie / ustawie", "luki prawnej" and columns ("tell us",
  "new normal", "lessons from"). A column with many keywords (NetScaler:
  zero-day) still passes the threshold after the penalty – it ranks lower
  but can enter when there are free places.

Test on the `v35-jakosc` branch on 2026-10-28: green, "SCALENIE PO CVE
(ze stron): 0" and "(ze streszczeń): 0" (few articles after the morning
digest); correction skipped – `gemini-3.8-flash` timed out twice (2 × 90
s), `gemini-3.5-flash` returned 503 twice; Groq did not touch the text.
The run took over 5 minutes. Fix: Gemini request timeout 30 s instead of
90 s (`src/gemini.py`) – a working Gemini answers in a few seconds; the
worst-case waiting drops from about 6.5 to about 2 minutes. Lesson for
the writing-model experiment: Gemini on the free tier is sometimes
unavailable in the morning (four days in a row), so the writing model
needs a fallback.

Checked on the archive: CVE merging on all October days joins only items
about the same event (PHP2Shell, Brotli, Apple); the new filler rules on
107 summaries flag only filler and formulas; the preposition autofix
changed only wrong forms ("z szybkiego" stays after the fix); the
context penalty hits 3 of 110 titles, all rightly. The old correction
tests (fallback to Groq) were replaced by tests of the new rule.

New and changed files: `src/event_grouping.py`, `src/main.py`,
`src/kev.py`, `src/summary_quality.py`, `src/ai_summaries.py`,
`src/glossary.py`, `src/article_selection.py`, `src/gemini.py`, `src/test_v35.py` (new),
`src/test_ai_summaries.py`, `src/test_proofreading.py`,
`src/test_language_notes.py`, README (PL/EN).

Unit tests: 398, passed.

------------------------------------------------------------------------

## v34 --- 2026-10-26

**Summaries that say why it matters and read easily: what happened, why
it matters, what to do; summaries of whole events in the tops.**

Reason: JW's review of the weekly top of 2026-10-26: summaries without
filler, but telegraphic – stacks of CVE ids and versions, long chains of
participles, no answer to the SOC practitioner's questions "is it
exploited?", "do I patch today?". In a top an event got the summary of
one article from one day: PHP2Shell (17 articles, 7 sources) was one
sentence of CVE ids and the CVSS score, without the story of the week
(exploit attempts 4 days before disclosure, site outages, another flaw
without a patch). JW's goal: quality, and at the same time easy to
read. JW's decision of 2026-10-26: the bridge to Mozaika becomes v35.

Changes in the daily digest:

- **Summary layout** (prompt in `src/ai_summaries.py`): sentence 1 – what
  happened and whom it concerns, in plain words, with the product or
  company name (at most one CVE id, not first); sentence 2 – why it
  matters for a defender: exploitation in attacks, public exploit,
  scale, patch or no patch; sentence 3, when the article says so – what
  to do. At most 420 characters (check: 480), 2 CVE ids and 3 versions.
- **CISA KEV for the AI**: the 🔥 marker set by code also reaches the AI
  as the field "kev", so "wykorzystywana w atakach" rests on the
  catalog, not on guesses; the fact is added to the check material.
- **Context of a follow-up** (`src/event_grouping.py`): an article
  marked as a follow-up by its title gets the earlier report from the
  archive (date and summary) as the field "kontekst"; the AI writes what
  is new, with a short reference ("Kilka dni po ujawnieniu PHP2Shell
  (22.10) …"). The context is part of the fact-check material.
- **Guards** (`src/summary_quality.py`): "aktywnie wykorzystywana",
  "wykorzystywana w atakach" and "brak łatki / nie wydano łatki /
  niezałatana" only when the material says so (like "zero-day" in v33) –
  the second sentence must not dramatize. Speculation about escalation
  ("sytuacja może eskalować", "ataki mogą się nasilić") counts as
  filler.
- **Detector of sentences without a concrete detail**
  (`src/summary_quality.py`, JW's question: how to make sure the AI does
  not push filler into the story): a sentence with no concrete detail
  (digit, CVE id, acronym, name, number word) but with evaluative words
  ("pokazuje", "wyzwania", "poważne zagrożenie", "ryzyko", "współpracuje
  z ekspertami") goes back for correction and is removed by code if it
  stays. The first version (only "no concrete detail") flagged 35 of
  140 archive sentences, half of them good ("Luka umożliwia wykonanie
  dowolnego kodu bez uwierzytelnienia"), so it was dropped; the current
  one flags 8 of 140 – all filler ("Firma współpracuje z organami
  ścigania i ekspertami ds. cyberbezpieczeństwa", "Problemy te pokazały,
  że … mogą stać się wektorem zagrożenia"). A sentence already caught by
  the filler list is not reported twice.
- **Readability** (soft, like the style list – never cuts a summary): a
  sentence over 25 words and more than 2 CVE ids go back for correction
  with a request to split. On 60 summaries of 22–26 October this
  concerns 14 (e.g. the PHP sentence with four versions, 28 words).

Changes in the tops:

- **Summary of the whole event** (`src/ai_summaries.py`,
  `src/monthly_top.py`): one request per top (Gemini, Groq as fallback)
  writes a short story in 3–4 very short sentences for each event with
  at least two material items (JW's clarification of 2026-10-26): what
  broke and whom it concerns, how it went (the key turn with a date),
  what is happening now and whether it escalates (attacks ongoing, new
  botnets, further flaws, a patch – only from a concrete turn in the
  material), how to patch; an element without support in the material
  is left out. The story should stick ("people learn and remember best
  through stories that speak to the imagination", JW): the AI picks one
  concrete, vivid detail from the material ("attacks began 4 days before
  disclosure"), no metaphors – the same in the daily prompt instead of
  "large scale". The story should work as a case study to tell SOC
  people over coffee ("case study condensate", JW): in "how it went"
  the AI gives, when the material says so, how the attackers got in –
  vector and technique (SQL injection, stolen keys, phishing, a chain of
  flaws). No moral or "lesson" – the reader draws the conclusions; "Ta
  historia pokazuje, że…" and "lekcja z tego…" count as filler. Material: the Polish summaries of the event's
  articles in date order (with the source) and the titles of related
  articles. The new summary is used only when it passes the fact,
  glossary and quality checks against that material; otherwise the
  previous one stays. Log: "ZESTAWIENIE AI: wydarzenie N – przed / po"
  and "streszczenia wydarzeń N z M". Then, as in v33, the language
  correction.

The material for PHP2Shell (top 5 for 19–25 October) is 8 summaries from
21 to 24 October and related titles ("PHP Warns of Another Unpatched RCE
Risk…", "PHP2Shell Exploit Attempts Hit Millions…", "Mirai Botnet
Operators Join PHP2Shell Attacks").

Digest test on the `v34-sens` branch on 2026-10-26 (12:09): 3 articles, all
analyses from the roundup. The check caught a 26-word sentence and an IP
address not in the article. Weaknesses checked at the source: Signal –
"nie ma jeszcze dostępnej łatki", although RingRTC 2.72.0 and newer
Signal apps are fixed (the guard let it through because the page
mentions "unpatched versions"); Plex2Shell – one technical sentence
instead of the point (a chain of four flaws, unauthenticated RCE, CVSS
9.8) and no story, because the CISA warning of 22 October was older than
3 days; PaperCut – English "AI‑orchestrated toolkit".

Fixes after the test:

- **Context from 14 days** (`src/event_grouping.py`, `src/main.py`):
  every article gets the latest earlier report of the same event from the
  archive of 14 days (shared CVE id or the same-event rule; no whole
  roundup records), not only a follow-up from 3 days. The "Ciąg dalszy"
  section unchanged (3 days). Log: "KONTEKST: wcześniejsze doniesienie z
  archiwum dla N z M artykułów".
- **"No patch" with a fixed version** (`src/summary_quality.py`):
  "unpatched" / "niezałatane" in the source is not enough when the source
  gives a fixed version ("before 2.72.0", "fixed in"); a summary that
  gives a fixed version and "no patch" at the same time is a
  contradiction.
- Style list: "AI-orchestrat*", "AI-powered", "AI-driven", "toolkit*".

Weekly top test on the branch (2026-10-26, 12:24): both Gemini models
unavailable (timeout, 503), the stories were written by Groq
gpt-oss-120b; "streszczenia wydarzeń 5 z 5". Better than before – story
elements appeared ("exploity 4 dni przed publicznym ujawnieniem",
"kryptominery i backdoor w postaci proxy"). Weaknesses: in 3 of 5
stories remarks about the material instead of facts ("Materiał nie
podaje żadnych ataków ani łatek", "CISA … nie podaje łatek", "nie ma
informacji o dalszych atakach ani o dostępnych łatach" for a leak of
API keys); word and meaning errors the checks cannot see ("mógł
wyczerpać klucze API", "aktywnie wykorzystywaną zero‑day", "Od końca
października dostępne są łatki", "łatki w pełni blokują RCE" without
the further flaw of 24 October); an empty sentence for Arista and the
missed detail "the third such flaw in four months". Fix (the same family
as "Nie podano…" in v29 and "nie są znane" in v33): remarks "materiał
nie…", "nie podaje…", "nie ma informacji…" count as filler (on 80
archive summaries: 2, both such remarks); story prompt: skip an element
without support silently, patches only for software flaws – for a leak,
what leaked and what to do. Word and meaning errors get no rules: an
argument for an experiment with the writing model (Gemini writes the
daily summaries, Groq as fallback; more material) after the observation
period.

JW's question (2026-10-26): are we in a "test → rule → test" loop?
Conclusion: partly yes – more rules from single examples on small samples
(here 3 roundup articles) risk overfitting and an overloaded prompt.
Therefore the rule on impersonal openings ("Wykryto…", 3 of 80
summaries) was withdrawn, and v34 closes with fixes of real errors (a
false fact, too short a context). JW's decision: after merging, 1–2 days
of watching regular digests without new changes; further fixes only for
recurring problems, not single sentences.

New and changed files: `src/ai_summaries.py`, `src/summary_quality.py`,
`src/event_grouping.py`, `src/monthly_top.py`, `src/main.py`,
`src/test_summaries_v34.py` (new), `src/test_summary_quality.py` (length
limit), `data/styl_unikaj.csv`, README (PL/EN).

Unit tests: 377, passed.

Completion of v34 (2026-10-27): the digest of 27 October had no
"KONTEKST" line in its log. The five code files of the second package
(`ai_summaries.py`, `summary_quality.py`, `event_grouping.py`, `main.py`,
`test_summaries_v34.py`) were uploaded to the repository root instead of
`src`, so they were part of the v34 merge but never ran: the workflow
runs `src/main.py`. Main therefore lacked the 14-day context, the guard
against a false "no patch" and the check of remarks about the material.
The files were moved to `src` and the root copies deleted. It is the
third such case (v22, v26), so a new test `src/test_repo_layout.py`
stops the workflow when a `.py` file appears in the root. Unit tests:
379.

------------------------------------------------------------------------

## v33 --- 2026-10-26

**Quality of summaries and tops after the digest and the first
scheduled weekly top 5 of 2026-10-26.** JW's decision of 2026-10-26:
this version closes with the quality fixes, and the report for CyberSec
Mozaika from the language log (v32) becomes v34 once the log has data.

Reason: the first digest after v32 (2026-10-26, alarm clock, 10
articles) looked "lame" (JW): the formula "Zaleca się natychmiastową
aktualizację / natychmiastowe zastosowanie łatki" in 4 of 10 summaries;
"podatność zero-day" for the Brotli flaw patched on 21 October (the
first confirmed case of a label added by the AI); "Liczba i rodzaj
naruszonych danych nie są znane"; the PHP 8.5.12 release from the
roundup at the top of "Najważniejsze", although PHP2Shell had been in
the digests of 22–24 October.

Changes:

- **A closing formula without content counts as filler**
  (`src/summary_quality.py`): the sentence "Zaleca się (natychmiastową)
  aktualizację / zastosowanie łatki / aktualizację wszystkich
  wymienionych komponentów." goes back for correction and is removed by
  code if it stays. Advice with content ("… i ograniczenie dostępu do
  interfejsów zarządzania", "do wersji 8.5.12") stays. Prompt: advice
  only when concrete, no closing formula.
- **"zero-day" and "natychmiast…" only when the material has them**:
  checked like numbers not in the article (the material counts with
  zero-day, 0-day, immediately, urgent, imperative, natychmiast,
  niezwłocznie, pilnie, jak najszybciej etc.). When the AI correction
  does not help, code removes only the label ("podatność zero-day CVE-…"
  → "podatność CVE-…"), so the sentence with the facts stays. The
  proofreading cannot add such labels.
- Filler "nie jest / nie są (jeszcze) znane".
- **"Ciąg dalszy" by CVE ids from the page of a lektura link**
  (`src/main.py`): for articles "via Zaufana Trzecia Strona" the CVE ids
  in the first 2000 characters of the fetched page count too (the ZTS
  comment is short, and the PHP Foundation post names CVE-2026-109618
  and CVE-2026-109619 after the first 600 characters). Regular articles
  unchanged.

Checked on the summaries of 2026-10-26: the rules catch the three
formulas (PHP, Armory Castle, Atlassian) and "nie są znane" (Quest
Diagnostics); the HPE advice with content stays.

Test on the `v33-jakosc` branch on 2026-10-26 (07:26): 3 articles of 78
(the morning digest took the rest), all from the roundup; no summary
ends with a formula, the check reported only the number "2023" not in
the article (corrected by the AI). Weaknesses: "Negocjatorzy ransomware
(program żądający okupu)" – the explanation reads as if the negotiators
were a program; calques "AI-hackingowego" and "buildów szyfrujących".

Fixes after the test:

- **Ransomware explanation** (`src/glossary.py`): skipped when ransomware
  describes people or groups ("negocjatorzy / grupy / gang / operatorzy /
  członkowie ransomware"); the explanation then goes to a later
  occurrence or the next summary. "Atak ransomware (program żądający
  okupu)" stays as before. After a verb or preposition that governs the
  genitive, the explanation is in the genitive: "użyła ransomware
  (programu żądającego okupu)" – the same mechanism as for exploit and
  infostealer (v27), forms following the inflection generated earlier
  with Morfeusz 2.
- Style list `data/styl_unikaj.csv`: "AI-hacking*" (→ do włamań z użyciem
  AI) and "buildy / buildów / buildami / buildach" (→ wersje,
  kompilacje); no bare "build", so product names ("Build Tools") are not
  caught.

**Fixes after the first scheduled weekly top 5** (2026-10-26, 08:17,
`#top-tygodnia`, week 19–25 October). The top was sent on time, but:
PHP2Shell appeared twice (item 4 was the announcement of 21 October
"… patches coming tomorrow" with the summary "Łatki zostaną udostępnione
jutro", and four other PHP2Shell articles were separate events); item 5
merged Fortinet (Sekurak) with FortiSIEM (The Hacker News); old archived
summaries still had "RCE (RCE)", "exploit tych luk mogą prowadzić"
(lowercase, wrong syntax) and "zero‑day podatność". The tops did not
merge by CVE ids or by the titles of related articles, and showed
archived summaries without any check.

- **Single-name rule** (`src/event_grouping.py`): forms of one name may
  differ only by the ending ("Capcom" / "Capcomu"), so "Fortinet" and
  "FortiSIEM" (only "forti" shared) no longer merge; platform names
  (Python) do not merge in this rule either (wrong MCP Python SDK /
  Pillow merge). Product-type words (center, manager, software,
  platform, suite…) are not company names (data of 2026-10-26: "Siemens
  Software Center" with "Atlassian … Data Center"). The wrong merges
  Fortinet/FortiSIEM and MCP Python SDK/Pillow watched since v31 are
  gone.
- **Merging in the tops** (`src/monthly_top.py`): a shared CVE id (saved
  in the archive or in the title or summary) or an event name with
  digits in any title of the record and the event, including titles of
  related articles; a second pass joins events split by order. A whole
  roundup record links nothing by CVE.
- **Event leader**: highest score, then a Polish source, then the most
  related articles (PHP2Shell under the Kapitan Hack title instead of
  the English announcement).
- **Summaries in the tops**: code applies the autofix ("RCE (RCE)" →
  "RCE") and sentence case and removes sentences with problems
  ("jutro", filler); an English or title-only summary falls back to the
  next article of the event. Then one language correction of the whole
  top (Gemini, Groq as fallback; one request per week or month). The
  workflows `weekly-top.yml` and `monthly-top.yml` get the secrets
  `GROQ_API_KEY`, `GEMINI_API_KEY` and the variable `GEMINI_MODEL`;
  without them the top goes out without the correction.
- **Roundups left out of the tops**: ThreatsDay and Weekendowa lektura
  as one item, archived before the v29 filter.
- **CVE ids of lektura links** (`src/kev.py`): for articles "via Zaufana
  Trzecia Strona" the first 2000 characters of the linked page count
  (instead of 600), so the archive keeps the CVE ids of such a
  publication (for 🔥 and merging in the tops); "Ciąg dalszy" uses the
  same limit.

Simulation on the archive: the top 5 for 19–25 October is PHP2Shell (17
articles, 7 sources, Kapitan Hack title, summary without "RCE (RCE)"),
Arista VCO, Node2Shell, Plex2Shell, OpenCode; no PHP duplicate, no
Fortinet/FortiSIEM and no ThreatsDay. Grouping of the whole of October:
no correct merges lost. Left to the AI correction: "Exploit tych luk
mogą prowadzić" (Plex) – code only fixes the capital letter.

New and changed files: `src/summary_quality.py`, `src/ai_summaries.py`,
`src/main.py`, `src/glossary.py`, `src/event_grouping.py`,
`src/monthly_top.py`, `src/weekly_top.py`, `src/kev.py`,
`src/test_quality_v33.py` (new), `src/test_tops_v33.py` (new),
`src/discord_output.py`, `.github/workflows/weekly-top.yml`,
`.github/workflows/monthly-top.yml`, `data/styl_unikaj.csv`, README
(PL/EN).

Second branch test (2026-10-26, 10:50) – digest and weekly top run from
the branch to the test channel. The top 5 matches the simulation, and
the Gemini correction fixed "Exploity tych luk mogą prowadzić" and
"podatność zero-day". Digest: the style list caught "rekordów",
"Breaches", "AI‑napędzany", "eksploatacji", "AI‑zarządzany" and
"buildów". New weaknesses: an empty "🔁 CIĄG DALSZY (cd.)" header above
the notes only; "46 własnych wersji, kompilacji szyfrujących" (the AI
pasted both suggestions from the style list); "4,1 mln danych" (data
cannot be counted); "firm negocjujących ransomware (program żądający
okupu)".

- **Message splitting** (`src/discord_output.py`): an empty line not
  followed by a numbered item ends the section, so the notes get no
  "(cd.)" header; a top section (empty line below its header) still
  continues.
- **Style-list suggestions as alternatives** (`src/summary_quality.py`,
  `src/ai_summaries.py`): "wersji, kompilacji" reaches the AI as "wersji
  albo kompilacji (wybierz jedno słowo, nie wpisuj obu)"; the list file
  itself unchanged for this.
- Style list: "mln / tys. / mld danych" → "wpisów" (data cannot be
  counted).
- Ransomware explanation also skipped after "negocjujących" (stem
  "negocj").

To watch (meaning, not form – code cannot detect it): the VeraCrypt
summary describes the mechanism but misses the point (loss of the Mark
of the Web); in PHP2Shell a sentence without a subject ("podatności …
potwierdzono ich wykorzystywanie") that the correction did not fix.

Clean-up log in the tops (`src/ai_summaries.py`, `src/monthly_top.py`,
`src/weekly_top.py`): every change code makes to a top summary goes to
the workflow log as "PORZĄDEK: wydarzenie N – …" (autofix, removed
sentence with the reason, summary skipped as English or title-only) and
a summary "streszczenia zmienione przez kod: N z M". The clean-up used
to be silent, and the top log showed only the correction ("KOREKTA:
…"). Simulation on the top 5 of 19–25 October: "RCE (RCE)" → "RCE"
(PHP2Shell) and a skipped English summary (Node2Shell) – 2 of 5.

Unit tests: 346, passed.

------------------------------------------------------------------------

## v32 --- 2026-10-25

**Language log: language corrections of summaries saved in the
archive.**

Reason: until v31 the language corrections existed only in the run log
("KONTROLA: …", "KOREKTA: przed/po"). The log is deleted after 90 days
and cannot be counted, so there was no data for reports to CyberSec
Mozaika. JW's decision of 2026-10-25: close this gap first (v32), and
build the reports for Mozaika in v33.

Changes:

- **Language notes on the article** (new `src/language_notes.py`):
  every delivered article has a `language` field in the archive with the
  corrections of its summary. Types: `glossary` (a forbidden form
  instead of the required one, with the entry id), `style` (a calque
  from `data/styl_unikaj.csv`), `inflection` (a term left in the base
  form after a preposition, e.g. "przed exploit", with the entry id),
  `autofix` (a replacement by code without an AI request, with the entry
  id when the rule follows the glossary) and `proofreading` (the summary
  before and after the correction and the model that made it).
- **Outcome** (`fixed_by`) for forms from the AI draft: `ai` (fixed by
  the AI), `code` (code removed the sentence), `remains` (still in the
  summary – possible only for calques, which never cut a summary) or
  `dropped` (summary dropped; the notes stay on the article).
- `src/glossary.py`: autofix rules carry the glossary form (łatka, RCE,
  exploit) or a rule name; new functions `entry_by_form` and
  `violation_entries` (forbidden form with its entry).
  `src/summary_quality.py`: calques and uninflected terms available as
  data (`style_hits`, `uninflected_hits`).
- Log: "JĘZYK: uwagi językowe do archiwum – słowniczek N, styl N,
  odmiana N, autopoprawki N, korekta N".
- The notes only describe what the AI wrote: they change nothing in the
  summary and write nothing to the glossary. Test runs save nothing, as
  before.

Checked on real errors from the logs of 22–25 October 2026: "rekordy
pacjentów" and "AI‑zarządzanego" (style), "patchują" (glossary, H166),
"przed exploit" (inflection, H153), "eksploatując", "intruzji",
"Kompromisy", "rootowy" (style) – all recorded.

Test on the `v32-jezyk` branch on 2026-10-25: AI summaries 9 of 9,
proofreading changed 7; log "JĘZYK: … słowniczek 0, styl 2, odmiana 0,
autopoprawki 2, korekta 7", consistent with the KONTROLA and KOREKTA
lines. "Ciąg dalszy" had 6 of 9 items. Five were right (PHP, Arista
VCO, BeyondTrust/Armory Castle, Brotli/Node.js, Quest Diagnostics), but
the Unit 42 analysis of FortiManager got there through CVE-2024-47575
from the whole roundup 699, delivered on 2026-10-24 as one item. Also in
the summaries: "eliminują ryzyko ataków" (filler), "75 unikalnych
podatności" and "wpływających na wersje" (calques).

Fixes after the test:

- **CVE-based "Ciąg dalszy" skips records of a whole roundup**
  (`src/main.py`): their CVE ids come from dozens of different links, so
  a new analysis of one of them is not a follow-up of an event.
- Filler "eliminuje ryzyko / zagrożenie" (`src/summary_quality.py`).
- Style list `data/styl_unikaj.csv`: "unikaln*" (→ różny, or no
  adjective) and "wpływając* na wersj*" (→ dotyczący wersji).

New and changed files: `src/language_notes.py` (new),
`src/test_language_notes.py` (new), `src/ai_summaries.py`,
`src/glossary.py`, `src/summary_quality.py`, `src/article_archive.py`,
`src/main.py`, `src/test_roundup_parts.py`, `data/styl_unikaj.csv`,
README (PL/EN).

Unit tests: 307, passed.

------------------------------------------------------------------------

## v31 --- 2026-10-25

**Splitting "Weekendowa lektura" into links, merging stories by company
names, alarm on workflow failure.**

- **"Weekendowa lektura" split into parts** (new `src/roundup_parts.py`,
  `src/main.py`): as JW originally intended (2026-10-25), the ZTS
  roundup is not one item but a source of links. Every list item or
  paragraph with a link to another site becomes a candidate article
  (title: the link text or the beginning of the comment; description:
  the ZTS comment) and goes through the same scoring, threshold,
  filtering of published links and event merging. At most 3 such links
  per digest (`LEKTURA_LIMIT` in `src/article_selection.py`), labelled
  "via Zaufana Trzecia Strona"; the archive saves the `via` field. The
  log lists the parts found ("WEEKENDOWA LEKTURA: N pozycji",
  "LEKTURA: …"). When the content has no such links (layout change), the
  roundup stays one item with the fixed description, as in v29.
- **Merging by company and product names** (`src/event_grouping.py`,
  `src/monthly_top.py`): in Title Case titles every word is capitalized,
  so the earlier name rule saw nothing (Quest Diagnostics and Capcom twice
  in the digests of 23–24 October). New rules: a shared pair of
  capitalized, non-generic words rare in the pool ("Quest Diagnostics");
  a single shared word only when the article texts (descriptions, Polish
  summaries) show it is a name – always capitalized, never lowercase
  ("Capcom"); platform names that appear in different stories
  (Microsoft, Windows, Chrome, Python, WordPress…) never merge alone.
  Works in the digest, "Ciąg dalszy" and the tops.
- **Alarm on failure** (`.github/workflows/daily-digest.yml`,
  `weekly-top.yml`, `monthly-top.yml`): when a workflow fails, a message
  "⚠️ … workflow zakończył się błędem" with a link to the log goes to
  the test channel – the owner learns about a failure before the
  readers.
- Small change: remarks "… nie została podana / ujawniona / wskazana"
  are reported like filler ("Liczba poszkodowanych nie została podana",
  v30 test).

Checked on the October archive (70 articles): the top now merges Quest
Diagnostics, Capcom and Arista VCO, without new wrong merges (two merges
from earlier rules – Fortinet/FortiSIEM and MCP Python SDK/Pillow – stay
under observation).

New and changed files: `src/roundup_parts.py` (new),
`src/test_roundup_parts.py` (new), `src/main.py`,
`src/article_selection.py`, `src/discord_output.py`,
`src/article_archive.py`, `src/event_grouping.py`,
`src/test_event_grouping.py`, `src/monthly_top.py`,
`src/summary_quality.py`, three workflows, README (PL/EN).

Test on the `v31-lektura` branch on 2026-10-25: Weekendowa Lektura
episode 699 split into 53 parts with Polish ZTS titles; 3 entered the
digest (incl. Krebs on the negotiator working with ShinyHunters); the
subscription link, YouTube and Discord fell below the threshold.
Weaknesses: commentary got in ("Najbezpieczniejsza przeglądarka 2026?
…", +3 for "zero-day"), while threat analyses without keywords in the
title were left out (Unit 42, ESET, Mandiant, Microsoft, Securelist);
the PHP item from the roundup went to "Najważniejsze" although PHP2Shell
had already been in the digest (the ZTS comment has no CVE id, the
title no name).

Fixes before merging (JW's decision: right away, before v32):

- **A question mark in the title of a lektura link** = commentary: the
  same penalty as for event/advice context (`has_context_title`); only
  for lektura, because in regular feeds news titles also use question
  marks ("Fakturownia zhakowana?").
- **+2 bonus for lektura links to threat-research publications**
  (`ANALYSIS_SOURCES`: Unit 42, Securelist, ESET WeLiveSecurity,
  Google/Mandiant Threat Intelligence, Microsoft Security Blog, Sophos,
  Sekoia, Zscaler, Symantec, Check Point Research, Talos, CrowdStrike,
  Proofpoint, Elastic Security Labs, Huntress, GreyNoise, Hunt.io, CERT
  Polska), so analyses without keywords in the title pass the threshold.
- **Links without article text skipped**: z3s.pl (ZTS short link),
  YouTube, Discord, X/Twitter, Facebook, LinkedIn, Instagram, TikTok,
  Telegram (matching the domain or a subdomain, not the ending – "x.com"
  is not "netflix.com").
- **"Ciąg dalszy" by CVE ids in summaries** (`src/main.py`): after the
  summaries, an article whose summary has a CVE id from an archive
  record of the last 3 days goes to "Ciąg dalszy".

Simulation on the titles of roundup 699: top of the ranking Nginx, PHP,
Unit 42 on FortiManager, Mandiant on Armory Castle; "Najbezpieczniejsza
przeglądarka" falls below the threshold. Unit tests: 290, passed.

Documentation before merging: README (PL/EN) rewritten for the state of
v31. Outdated statuses removed (alarm clock "awaiting confirmation",
grouping "not yet observed live", v13 results with 69 tests, "planned
AI processing"); a table of 16 stages with versions; the description
split into sections (sources and selection, events and markers, AI
summaries, delivery and tops, triggers); current limitations and the
roadmap (bridge to Mozaika, v32). The Polish README got the missing
sections: architecture, repository structure, configuration and
secrets, testing. The section "Project status based on the reviewed
history" at the end of the changelog is marked as a historical record
after v10.

## v30 --- 2026-10-25

**"Polacy nie gęsi": Gemini language correction, LanguageTool hints,
simpler sentences.**

Reason: in the v29 test (2026-10-25) the correction (gpt-oss-120b)
fixed 5 of 6 summaries, but errors of government and agreement that
lose the meaning remained: "CISA dodało do listy KEV dwóch podatności"
(should be "CISA dodała … dwie podatności") and "Exploit CVE-2026-110447
umożliwia backdoor". The Groq models write Polish too poorly to catch
this. Completion of v29: the second test on the `v29-jezyk` branch gave
"KOREKTA: poprawione językowo 5 z 6 streszczeń" after the correction
moved to gpt-oss-120b.

JW's decision of 2026-10-25: correction by Google Gemini within the free
quota (project "PolacyNieGesi4Digest", no billing; secret
`GEMINI_API_KEY`). The Gemini API terms clause on the paid tier for apps
made available to users in the EEA was noted – only the GitHub
automation uses the API, and in the EEA even free use follows the paid
tier's data terms (content is not used for training); on any problem
the correction falls back to Groq.

Changes:

- **Correction by Gemini** (new `src/gemini.py`): models
  `gemini-3.8-flash`, fallback `gemini-3.5-flash` (read from AI Studio;
  the repository variable `GEMINI_MODEL` can override them). The key is
  sent in the `x-goog-api-key` header, never in the URL or the log.
  Order: Gemini → gpt-oss-120b → qwen3.8-27b; when the free quota is used
  up (error 429) the correction moves to Groq and the digest goes on.
  One request a day.
- **LanguageTool hints** (new `src/languagetool.py`): all summaries are
  checked in one request to the public LanguageTool API (pl-PL, no key);
  findings in grammar, punctuation, confused words and semantics go to
  the correction as "uwagi" next to the summary (spelling findings are
  skipped, as they are mostly technical names). Code does not apply them
  itself.
- **Summary prompt**: short, simple sentences (up to about 20 words, one
  fact per sentence), verb agreement with the subject ("CISA dodała",
  "Microsoft wydał"), accusative after "dodać/wydać/załatać", a CVE id is
  a vulnerability, not an exploit.
- **Correction prompt**: government and agreement with the example from
  the test, rephrasing an unclear sentence while keeping the facts,
  splitting a long sentence allowed.
- **"przed → po" log** for every corrected summary and the name of the
  model that did the correction.

New and changed files: `src/gemini.py` (new), `src/languagetool.py`
(new), `src/test_proofreading.py` (new), `src/ai_summaries.py`,
`.github/workflows/daily-digest.yml` (secret `GEMINI_API_KEY`, variable
`GEMINI_MODEL`), README (PL/EN).

The change was verified: unit tests (277) passed. Test on the
`v30-Polacy` branch on 2026-10-25: the correction was done by
`gemini-3.8-flash` (key and model name work), 6 of 6 summaries
corrected, no correction rejected. Examples from the "przed → po" log:
"Exploit CVE-2026-110447 umożliwia instalację backdoora" → "Luka
CVE-2026-110447 pozwala zainstalować backdoora"; "łatki dla 72
podatności…, w tym osiem krytycznych luk" → "ośmiu krytycznych luk";
"Atlassian wydało" → "Atlassian wydał"; "wyciekiem niektórych wpisów
pacjentów" → "wyciekiem danych niektórych pacjentów"; a repeated
"kolejne… kolejnych" removed. LanguageTool reported nothing (0 of 6)
despite case errors – its Polish rules are weak, so Gemini does the
main work. To watch: the remark "Liczba poszkodowanych nie została
podana" (the form "nie została podana" is not detected yet). Parsing
"Weekendowa lektura" and merging by company names move to v31.

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
from the digests of 23–24 October 2026. Merging stories by company
names in titles (Quest Diagnostics, Capcom) is left for the next
version.

Test on the `v29-jezyk` branch on 2026-10-25 (Sunday, 6 articles): all
summaries in Polish, without calques or filler, with facts; KEV catalog
downloaded (1756 entries), 1 article marked; the proofreading round
changed no summary ("poprawione językowo 0 z 6"), although errors
remained ("dotykających wersje", "nieokreśloną liczbę danych").

Fixes after the test (JW's decisions of 2026-10-25):

- Proofreading with the main model first (gpt-oss-120b), the second one
  only on error; the proofreading prompt got a list of typical errors
  with examples (case after participles, gender and number, calques,
  impersonal syntax).
- "wykonanie kodu zdalnie" (reversed order) → "RCE", as in the glossary.
- After "typu"/"rodzaju" the explanation of "podwyższenie uprawnień" is
  in the nominative: "luk typu podwyższenie (eskalacja) uprawnień".
- Style list: "liczb* danych" → "zakres danych, wolumen danych".

Unit tests after the fixes: 270, passed.

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

## Project status based on the reviewed history (historical record after v10)

A record of the state reconstructed for v1–v10; it does not describe
the current state. Current status: [README.md](README.md).

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
