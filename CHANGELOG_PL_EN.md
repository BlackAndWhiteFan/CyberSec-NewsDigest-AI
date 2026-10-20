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
otrzymują osobnych wersji.

Format inspirowany [Keep a Changelog](https://keepachangelog.com/).
Źródło wpisów v1--v10: historia Git (113 commitów), opisy commitów i
przeanalizowane diffy.

------------------------------------------------------------------------

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
Plex2Shell) poprawiane ręcznie w archiwum po zapisie. Testy: 198. Zapis
uzupełnionych streszczeń zostanie opisany w tym wpisie.

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
do not receive separate versions.

Format inspired by [Keep a Changelog](https://keepachangelog.com/).
Sources for v1--v10: Git history (113 commits), commit descriptions,
and reviewed diffs.

------------------------------------------------------------------------

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
the archive after saving. Tests: 198. The saving of the backfilled
summaries will be recorded in this entry.

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
