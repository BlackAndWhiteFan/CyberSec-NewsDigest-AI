# Reguły języka Prasówki

Żywy dokument zasad polszczyzny Prasówki (CyberSec AI News Digest),
opracowany przez JW z Claude (od v46, 07.11.2026). Rośnie razem z
glosariuszem Mozaiki (CyberSec Mozaika) i obserwacją kolejnych prasówek.

**Kto decyduje:** JW. Claude proponuje, JW akceptuje wiersz po wierszu.

**Zasada nadrzędna (JW, 7.11.2026):** język branży wygrywa z purystyką.
Kalka utrwalona w żargonie SOC i IT („wystawiony”, „w buildzie”,
„framework”) zostaje. Na listę zakazów trafia tylko to, co razi także
praktyka albo zmienia sens.

## Gdzie co jest

| Rodzaj reguły | Plik | Kto stosuje |
|---|---|---|
| Glosariusz: terminy i formy obowiązkowe | `data/glosariusz_mirror.csv` (mirror glosariusza, Mozaika → Prasówka) | prompt, kontrola, autopoprawka |
| Zakazy: kalki i anglicyzmy z podpowiedzią | `data/styl_unikaj.csv` | prompt, kontrola (prośba o poprawkę) |
| Uzus branżowy: angielskie słowa dozwolone | `data/slowa_angielskie_ok.csv` | kontrola słów (Morfeusz 2), prompt |
| Nakazy dla modeli | ten plik, sekcja „Nakazy dla modeli” | prompt piszącego, korektora i historii wydarzeń |
| Autopoprawki pewne w 100% | `src/glossary.py` (AUTOFIX) | kod, bez AI |
| Reguły gramatyczne z Morfeuszem 2 | `src/polish_words.py` | kontrola (prośba o poprawkę) |

## Nakazy dla modeli

Każda linia zaczynająca się od „- ” w tej sekcji trafia dosłownie do
promptów. Pisz krótko, z przykładem „błąd → poprawnie”.

- Grupy przestępcze i APT to „grupa”, nie „zespół”: „grupa Storm-0940”, a nie „zespół Storm-0940”. „Zespół” tylko dla badaczy i firm („zespół Unit 42”).
- Nazwę firmy odmieniaj w jednym rodzaju w całym streszczeniu: „Chainalysis poinformowało… Chainalysis ujawniło”, a nie raz „poinformowało”, raz „ujawnił”.
- Nazwy produktów odmieniaj, gdy polszczyzna to umożliwia: „w Firefoksie”, „w Androidzie”, „w Linuksie”. Nie odmieniaj nazw nieodmiennych („w Windows”, „w Chrome”).
- Szyk: określenie po rzeczowniku: „81 podatności wysokiego ryzyka”, a nie „81 wysokiego ryzyka podatności”.
- Zdanie ma podmiot, gdy artykuł go podaje: „Badacze z firmy X przeanalizowali…”, a nie „Przeanalizowano…”.
- O katalogu KEV pisz o luce, nie o ataku: „Luki nie ma w katalogu CISA KEV”, a nie „Atak nie został zgłoszony w katalogu CISA KEV”.
- Zamiast ogólników o naprawie podaj wersję: „Lukę usunięto w wersji 10.02.002”, a nie „Problem został naprawiony w metryce 242 wersji…”.
- Liczebnik uzgadniaj z rodzajem: „dwie luki”, „dwie podatności”, „dwa błędy”.
- Wartość CVSS pisz z przecinkiem: „CVSS 8,1” (wersje programów zostają z kropkami: „16.7.8”).
- *Unauthenticated* to „bez uwierzytelnienia” lub „niezalogowany”, nie „nieautoryzowany”: „luka pozwala atakującemu bez uwierzytelnienia wykonać kod”. „Niezalogowany” piszemy tylko o osobie (atakujący, użytkownik); o luce lub ataku: „podatność XXE dostępna bez logowania”, „obejście uwierzytelniania bez logowania”, a nie „niezalogowana podatność” ani „niezalogowane obejście”.
- „Hash” to uzus branżowy: przy pierwszym wystąpieniu w streszczeniu „hashe (skróty haseł)”, dalej „hashe”. Pisownia „hash, hasha, hashe”, nie „hasz, hasze”. Odmieniaj oba człony: „wyciek hashy (skrótów haseł)”, „hashami (skrótami haseł)”, a nie „hashy (skróty haseł)”.
- Liczba przy zero-day: „30 luk zero-day”, „dwie luki zero-day”, a nie „30 zero-day” ani „30 zero-dayów”.
- Uzus branżowy, który jest poprawny: „łatka” i „poprawka (bezpieczeństwa)”, „RCE” i „zdalne wykonanie kodu”, „wyciek 2 mln rekordów”. Nie pisz „patchować” ani „remote code execution”. Podatności się „wykorzystuje”, a nie „eksploatuje”: „wykorzystanie podatności”, nie „eksploatacja podatności”.

## Historia zmian reguł

- v46 (07.11.2026): pierwsza wersja dokumentu; nakazy z przeglądu prasówek 31.10–7.11; „build” przeniesiony z zakazów do uzusu branżowego.
- v52 (16.11.2026): decyzje autora z Listu 42 – „poprawka (bezpieczeństwa)”, „zdalne wykonanie kodu” i „rekordy” dopuszczone; „eksploatacja” podatności dalej zakazana.
- v51 (12.11.2026): przy „hashe (skróty haseł)” odmieniaj oba człony (prasówka z 12.11: „wyciek hashy (skróty haseł)”).
- v49 (10.11.2026): „hash” przeniesiony z zakazów do uzusu branżowego; pierwsze wystąpienie „hashe (skróty haseł)” (decyzja JW: branża mówi „hash”).
- v48 (10.11.2026): „niezalogowany” tylko o osobie (prasówka z 10.11: „niezalogowana podatność XXE”); liczba przy zero-day.
