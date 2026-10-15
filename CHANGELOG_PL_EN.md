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
potwierdzenia. W nagłówku changelogu zaznaczono, że od v11 wpisy są
dodawane na bieżąco, razem ze zmianą, a nie odtwarzane z historii Git.

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
confirmation. The changelog header now notes that, from v11 onwards,
entries are added together with each change rather than reconstructed
from Git history.

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
