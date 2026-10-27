"""v34: summaries that say why it matters, readable; event summaries in the tops."""

import io
import json
import unittest

import ai_summaries
from ai_summaries import build_request_messages, summarize_articles, summarize_events, summary_material
from event_grouping import mark_continuations
from monthly_top import rank_events
from summary_quality import quality_problems, readability_problems


def setUpModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 0
    ai_summaries.PROOFREAD = False


def tearDownModule():
    ai_summaries.MIN_REQUEST_INTERVAL = 20
    ai_summaries.PROOFREAD = True


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ScriptedOpener:
    """Groq-style replies with given texts; records the request payloads."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append(json.loads(request.data.decode("utf-8")))
        texts = self.replies.pop(0)
        content = json.dumps({"streszczenia": [{"id": n, "tekst": t} for n, t in texts.items()]})
        return FakeResponse(json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8"))


def has(problems, fragment):
    return any(fragment in problem for problem in problems)


class TestPromptItems(unittest.TestCase):
    def article(self, **extra):
        return dict({"title": "PHP2Shell exploited in the wild", "link": "https://x/1",
                     "description": "Attackers exploit PHP2Shell."}, **extra)

    def test_kev_and_context_reach_the_ai(self):
        article = self.article(kev=["CVE-2026-109618"], previous={
            "date": "2026-10-22", "title": "PHP2Shell: dwie krytyczne luki", "summary": "Ujawniono dwie luki w PHP."})
        item = json.loads(build_request_messages([(1, article)])[1]["content"])["artykuly"][0]

        self.assertEqual(item["kev"], "tak")
        self.assertEqual(item["kontekst"], "22.10: Ujawniono dwie luki w PHP.")

    def test_plain_article_has_neither(self):
        item = json.loads(build_request_messages([(1, self.article())])[1]["content"])["artykuly"][0]
        self.assertNotIn("kev", item)
        self.assertNotIn("kontekst", item)

    def test_material_for_the_fact_check(self):
        article = self.article(kev=["CVE-2026-109618"], previous={"date": "2026-10-22", "summary": "Luki z 22.10."})
        material = summary_material(article)
        self.assertIn("Kontekst: 22.10: Luki z 22.10.", material)
        self.assertIn("CISA KEV", material)

    def test_prompt_asks_why_it_matters(self):
        prompt = build_request_messages([(1, self.article())])[0]["content"]
        self.assertIn("czy to jest wykorzystywane?", prompt)
        self.assertIn("„kontekst”", prompt)

    def test_continuation_keeps_the_earlier_report(self):
        articles = [{"title": "Quest Diagnostics confirms data breach exposed patient records", "link": "https://a"}]
        records = [{"title": "Quest Diagnostics warns of potential data theft after attack", "link": "https://b",
                    "date": "2026-10-24", "summary": "Quest Diagnostics zgłosiła atak."}]
        mark_continuations(articles, records)

        self.assertTrue(articles[0]["continuation"])
        self.assertEqual(articles[0]["previous"]["summary"], "Quest Diagnostics zgłosiła atak.")


class TestGuards(unittest.TestCase):
    def test_exploited_needs_support(self):
        text = "Luka jest aktywnie wykorzystywana."
        self.assertTrue(has(quality_problems(text, "Title\nA flaw was patched."), "wykorzystywaniu"))
        self.assertFalse(has(quality_problems(text, "Title\nThe flaw is actively exploited."), "wykorzystywaniu"))
        self.assertFalse(has(quality_problems(text, "Title\nText.\nCISA KEV: luka wykorzystywana w atakach."),
                             "wykorzystywaniu"))

    def test_no_patch_needs_support(self):
        text = "Producent nie wydał jeszcze łatki."
        self.assertTrue(has(quality_problems(text, "Title\nVersion 2.1 fixes the bug."), "braku łatki"))
        self.assertFalse(has(quality_problems(text, "Title\nThe flaw remains unpatched."), "braku łatki"))

    def test_long_sentence_and_cve_stack_are_soft(self):
        long = ("Wydano wersje PHP 8.5.12, 8.4.27, 8.3.36 i 8.2.35, które łatają dwie krytyczne podatności "
                "umożliwiające nieautoryzowane wykonanie kodu na serwerach PHP w wielu popularnych "
                "konfiguracjach hostingu współdzielonego.")
        self.assertTrue(has(readability_problems(long), "podziel"))
        self.assertTrue(has(readability_problems("Luki CVE-2026-65637, CVE-2026-65182 i CVE-2026-68525."), "3 numery CVE"))
        self.assertFalse(has(quality_problems(long, soft=False), "podziel"))

    def test_short_sentences_pass(self):
        self.assertEqual(readability_problems("PHP wydało łatki. Luki są wykorzystywane od 23.10."), [])


class TestEscalation(unittest.TestCase):
    def test_speculation_is_filler(self):
        self.assertTrue(has(quality_problems("Sytuacja może eskalować w kolejnych dniach."), "ogólnik"))
        self.assertTrue(has(quality_problems("Ataki mogą się nasilić."), "ogólnik"))
        self.assertTrue(has(quality_problems("Może dojść do dalszej eskalacji."), "ogólnik"))

    def test_fact_of_escalation_stays(self):
        self.assertFalse(has(quality_problems("Od 24.10 lukę wykorzystują też operatorzy botnetu Mirai."), "ogólnik"))

    def test_moral_is_filler(self):
        self.assertTrue(has(quality_problems("Ta historia pokazuje, że łatki trzeba wdrażać szybko."), "ogólnik"))
        self.assertTrue(has(quality_problems("Lekcja z tego incydentu jest prosta."), "ogólnik"))

    def test_event_prompt_asks_how_they_got_in(self):
        from ai_summaries import EVENT_PROMPT
        self.assertIn("jak atakujący weszli", EVENT_PROMPT)
        self.assertIn("Nie dopisuj morału", EVENT_PROMPT)

    def test_event_prompt_tells_the_story(self):
        from ai_summaries import EVENT_PROMPT
        self.assertIn("czy sprawa eskaluje", EVENT_PROMPT)
        self.assertIn("nigdy „może eskalować”", EVENT_PROMPT)


class TestEmptySentences(unittest.TestCase):
    # Real sentences from the October 2026 archive.
    FILLER = [
        "Problemy te pokazały, że zarówno usługi, jak i urządzenia mogą stać się wektorem zagrożenia bez "
        "wcześniejszego ostrzeżenia.",
        "Firma współpracuje z organami ścigania i ekspertami ds. cyberbezpieczeństwa.",
        "Firma uruchomiła protokół reagowania na incydenty i prowadzi dalsze dochodzenie.",
    ]
    CONCRETE = [
        "Luka umożliwia nieautoryzowanemu atakującemu wykonanie dowolnego kodu bez uwierzytelnienia.",
        "Oszuści rozsyłają fałszywe pisma, podszywając się pod państwowy urząd.",
        "To już trzeci incydent tego typu w ciągu około miesiąca.",
        "Firma zaleca natychmiastową rotację wszystkich sekretów i poświadczeń przechowywanych na platformie.",
        "Zeabur ujawnił, że atakujący wykorzystali wyciek wewnętrznych poświadczeń, co doprowadziło do przejęcia "
        "infrastruktury.",
        "Amazon wykrył próby ataków 4 dni przed ujawnieniem.",
        "Zagrożenie dotyczy serwerów Microsoft Exchange.",
    ]

    def test_filler_is_found(self):
        from summary_quality import empty_sentences
        for sentence in self.FILLER:
            self.assertEqual(empty_sentences(sentence), [sentence], sentence)

    def test_known_filler_is_reported_once(self):
        problems = quality_problems("Atak ten stanowi poważne zagrożenie dla kluczowych sektorów.")
        self.assertEqual(len(problems), 1)
        self.assertIn("ogólnik", problems[0])

    def test_concrete_sentences_stay(self):
        from summary_quality import empty_sentences
        for sentence in self.CONCRETE:
            self.assertEqual(empty_sentences(sentence), [], sentence)

    def test_code_removes_the_empty_sentence(self):
        from summary_quality import repair_summary
        text = "Bank XYZ padł ofiarą ataku 12.10. Firma współpracuje z organami ścigania i ekspertami."
        self.assertEqual(repair_summary(text, lambda s: quality_problems(s, soft=False)),
                         "Bank XYZ padł ofiarą ataku 12.10.")


class TestBranchTestFixes(unittest.TestCase):
    # Daily branch test of 26.10.2026 (12:09).
    def test_no_patch_with_a_fixed_version_is_rejected(self):
        source = ("Signal vulnerability\nThe flaw affects RingRTC versions before 2.72.0. "
                  "Users running unpatched versions should update.")
        text = "Luka dotyczy wersji starszych niż 2.72.0 i nie ma jeszcze dostępnej łatki."
        self.assertTrue(has(quality_problems(text, source), "braku łatki"))

    def test_clear_no_patch_stays(self):
        source = "Tailscale\nTailscale has not yet released a patch for the flaws."
        self.assertFalse(has(quality_problems("Tailscale nie wydał jeszcze łatki.", source), "braku łatki"))

    def test_english_ai_compounds(self):
        problems = quality_problems("Badacze ujawnili AI‑orchestrated toolkit używany w atakach.")
        self.assertTrue(has(problems, "kalka „AI‑orchestrated”"))
        self.assertTrue(has(problems, "kalka „toolkit”"))

    def test_context_from_two_weeks_back(self):
        from event_grouping import add_context
        articles = [{"title": "Plex2Shell: łańcuch podatności w serwerze multimediów Plex", "link": "https://z/1",
                     "cves": ["CVE-2026-96652"]}]
        records = [
            {"title": "CISA: Hackers chain Plex flaws in Plex2Shell attacks to breach servers", "link": "https://b/1",
             "date": "2026-10-22", "summary": "CISA ostrzega przed atakami na Plex Media Server.",
             "cves": ["CVE-2026-96652"]},
            {"title": "Weekendowa Lektura: odcinek 699", "link": "https://z3s/1", "date": "2026-10-24",
             "summary": "Przegląd.", "cves": ["CVE-2026-96652"]},
        ]

        self.assertEqual(add_context(articles, records), 1)
        self.assertEqual(articles[0]["previous"]["date"], "2026-10-22")

    def test_continuation_context_is_kept(self):
        from event_grouping import add_context
        articles = [{"title": "X", "previous": {"date": "2026-10-25", "summary": "Wcześniej."}}]
        self.assertEqual(add_context(articles, [{"title": "X", "summary": "Inne.", "date": "2026-10-20"}]), 0)
        self.assertEqual(articles[0]["previous"]["summary"], "Wcześniej.")


class TestMaterialRemarks(unittest.TestCase):
    # Weekly top branch test of 26.10.2026 (12:24), written by gpt-oss-120b.
    def test_remarks_about_the_material_are_filler(self):
        for text in ("Materiał nie podaje żadnych ataków ani łatek, jedynie opisuje mechanizm exploitu.",
                     "CISA ostrzega przed dalszymi wykorzystaniami, nie podaje łatek.",
                     "Incydent zgłoszono 19 października, nie ma informacji o dalszych atakach."):
            self.assertTrue(has(quality_problems(text), "ogólnik"), text)

    def test_facts_stay(self):
        self.assertFalse(has(quality_problems("Sprawcy zainstalowali kryptominery na serwerach Plex."), "ogólnik"))

    def test_prompt_skips_missing_elements_silently(self):
        from ai_summaries import EVENT_PROMPT
        self.assertIn("Pomiń bez słowa", EVENT_PROMPT)
        self.assertIn("przy wycieku danych", EVENT_PROMPT)


class TestDailySummary(unittest.TestCase):
    def test_kev_sentence_passes_the_check(self):
        article = {"title": "Arista patches VeloCloud zero-day", "link": "https://x/a",
                   "description": "Arista fixed CVE-2026-114625 in VeloCloud Orchestrator 6.4.2.12.",
                   "kev": ["CVE-2026-114625"]}
        opener = ScriptedOpener([{1: "Arista załatała lukę CVE-2026-114625 w VeloCloud Orchestrator. "
                                     "Luka jest w katalogu CISA KEV, czyli jest wykorzystywana w atakach. "
                                     "Poprawka jest w wersji 6.4.2.12."}])

        summarize_articles([article], {"GROQ_API_KEY": "g"}, opener, lambda s: None)

        self.assertIn("wykorzystywana w atakach", article["summary"])


def event(title, material, summary="Stare streszczenie.", kev=()):
    return {"title": title, "summary": summary, "material": material, "kev": list(kev)}


PHP_MATERIAL = [
    "21.10 · bleepingcomputer.com · PHP warns admins: Zespół PHP zapowiedział łatki na dwie krytyczne luki.",
    "22.10 · sekurak.pl · Krytyczne podatności w PHP core: Wydano wersje 8.5.12 i 8.4.27 z łatkami.",
    "23.10 · thehackernews.com · Someone Tried to Exploit PHP2Shell 4 Days Before: Amazon wykryło próby "
    "wykorzystania luk 4 dni przed ujawnieniem.",
]


class TestEventSummaries(unittest.TestCase):
    def test_event_summary_replaces_the_old_one(self):
        events = [event("PHP2Shell", PHP_MATERIAL), event("Single", ["01.10 · a.pl · X: Jedno."])]
        opener = ScriptedOpener([{1: "Dwie krytyczne luki PHP2Shell pozwalają przejąć serwer z PHP. "
                                     "Łatki wyszły 22.10 w wersjach 8.5.12 i 8.4.27, a Amazon wykrył próby "
                                     "wykorzystania 4 dni przed ujawnieniem."}])

        self.assertEqual(summarize_events(events, {"GROQ_API_KEY": "g"}, opener, lambda s: None), 1)
        self.assertTrue(events[0]["summary"].startswith("Dwie krytyczne luki PHP2Shell"))
        self.assertEqual(events[1]["summary"], "Stare streszczenie.")
        sent = json.loads(opener.requests[0]["messages"][1]["content"])["wydarzenia"]
        self.assertEqual([item["id"] for item in sent], [1])

    def test_summary_with_facts_not_in_the_material_is_rejected(self):
        events = [event("PHP2Shell", PHP_MATERIAL)]
        opener = ScriptedOpener([{1: "Luki PHP2Shell dotknęły 40 000 serwerów."}])

        self.assertEqual(summarize_events(events, {"GROQ_API_KEY": "g"}, opener, lambda s: None), 0)
        self.assertEqual(events[0]["summary"], "Stare streszczenie.")

    def test_without_keys_nothing_changes(self):
        events = [event("PHP2Shell", PHP_MATERIAL)]
        self.assertEqual(summarize_events(events, {}), 0)
        self.assertEqual(events[0]["summary"], "Stare streszczenie.")

    def test_material_from_the_archive(self):
        records = [
            {"title": "PHP2Shell: dwie krytyczne luki", "source": "kapitanhack.pl", "date": "2026-10-24", "score": 5,
             "summary": "Ujawniono dwie krytyczne podatności w PHP.", "cves": ["CVE-2026-109618"],
             "related": [{"title": "Mirai Botnet Operators Join PHP2Shell Attacks", "source": "x.com"}]},
            {"title": "PHP warns admins", "source": "bleepingcomputer.com", "date": "2026-10-21", "score": 5,
             "summary": "Patches will be released tomorrow by the PHP team for the two flaws in all branches.",
             "cves": ["CVE-2026-109618"]},
        ]
        material = rank_events(records)[0]["material"]

        self.assertEqual(material[0], "24.10 · kapitanhack.pl · PHP2Shell: dwie krytyczne luki: "
                                      "Ujawniono dwie krytyczne podatności w PHP.")
        self.assertEqual(material[-1], "Powiązane artykuły: Mirai Botnet Operators Join PHP2Shell Attacks")
        self.assertEqual(len(material), 2)


if __name__ == "__main__":
    unittest.main()
