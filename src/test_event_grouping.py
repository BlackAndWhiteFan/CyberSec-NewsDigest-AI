import unittest

from event_grouping import (
    document_frequency,
    group_events,
    mark_continuations,
    same_event,
)

# Real titles from digests of 15-18.10.2026, used as the day's pool.
B="https://www.bleepingcomputer.com/"; T="https://thehackernews.com/"; Z="https://zaufanatrzeciastrona.pl/"; S="https://sekurak.pl/"; N="https://niebezpiecznik.pl/"; C="https://cyberdefence24.pl/"
RAW = [
(B,"Palo Alto Networks warns of PAN-OS RCE flaw exploited in attacks"),
(B,"Cisco patches new Secure Email Gateway zero-day exploited in attacks"),
(B,"CISA warns admins to immediately fix Ivanti flaw exploited as zero-day"),
(T,"CISA Urges Immediate Ivanti Connect Secure Updates as Honeypots Log 105 Exploit Attempts"),
(T,"Attackers Exploit CVSS 10.0 Bricksforge WordPress Flaw Enabling Unauthenticated RCE"),
(Z,"Gdzie przestępcy kupują dostęp do twojej firmy"),
(T,"Attacker Chains Three Ivanti Connect Secure Zero-Days for Root Access, Only Two Patched So Far"),
(T,"⚡ Weekly Recap: Helpdesk 0-Days, Rogue Certs, ShinyHunters Arrest, AI-Fooling Malware and More"),
(S,"Google wypłacił $250 000 za exploita. Exploita przygotowali w kilka dni używając GPT Sol. Koszt $40 000"),
(B,"Is AI pentesting as good as a human pentester?"),
(B,"Microsoft fixes VPN issues caused by September Windows updates"),
(B,"The Blind Spots of Agentic Pentesting and How to Close Them"),
(T,"Silent Lynx Exploits WinRAR Flaw to Deploy Reverse Shell in CIS Government Attacks"),
(T,"NGINX Fixes 5 Flaws, Including Possible RCE and a TLS Bug That May Skip Client-Cert Checks"),
(T,"Next.js Ships Out-of-Band Patch for Two Critical RCE Flaws in Caching and SVG Processing"),
(T,"Drupal Patches Critical Field UI Flaw With Unauthenticated RCE Path via Contributed Modules"),
(T,"Palo Alto Networks Patches PAN-OS Authenticated RCE Flaw Amid Active Exploitation"),
(T,"Langflow's Critical Authenticated RCE Flaw Targeted in 1,423 Honeypot Exploit Attempts"),
(T,"AhsayCBS Flaws Exploited to Deploy Web Shells Get New Fixes After Incomplete Patches"),
(T,"Cisco Warns of Active Attacks Exploiting New Critical Secure Email Gateway Vulnerability"),
(T,"Hackers Backdoor Nextcloud Servers Through Critical Flaw in Collabora's Built-in CODE App"),
(T,"Researchers Used a Public OpenAI Model to Build a $250,000 Chrome Full-Chain Exploit in Six Days"),
(T,"AI-Found Linux Kernel Flaw Gives Local Users Root, and Can Break a Guest Out to the Host"),
(T,"Microsoft Patches Record 1,413 Flaws, Including Exploited Windows Shell Bug"),
(T,"Docker Fixes Critical Two-Year-Old Hub Flaw That Let One User Push Images as Another"),
(T,"LG Smart TVs Vulnerable to Pre-Auth Root Takeover From Local Network"),
(T,"Critical SonicWall SMA 1000 Flaw Targeted in 135 Exploitation Attempts After Patch"),
(T,"P7 DarkSword iOS Exploit Kit Adds Crypto Wallet Data Theft and Remote Commands"),
(N,"Sejm przyjął ustawę o blokowaniu treści przez UKE. Czy to oznacza cenzurę internetu?"),
(N,"Kolejni pacjenci mogą mieć duży problem, czyli nowy incydent w branży medycznej…"),
(S,"Poprzez SQL injection dostali się do 130 000 rekordów bazy Polskiego Związku Szachów."),
(C,"Firmy widzą wzrost cyberataków. Droga do odporności jest jednak daleka"),
(C,"Oczyszczalnie, kamery, bioreaktor. Rosja znów atakuje Polskę"),
(C,"Polski ślad w cyberataku na Albert Heijn. Nowe ustalenia"),
(C,"Dane z Pegasusa trafiały za granicę. ABW potwierdza"),
(C,"Operacje Rosji w Europie. Microsoft potwierdza: Polska najczęściej atakowanym krajem"),
(N,"ENEL-MED informuje o kradzieży danych pacjentów"),
(N,"Wakacje.pl zhackowane – pozyskano dane paszportowe Polaków"),
(S,"admin/123456 – takim hasłem dostali się do duńskiej bazy PESEL (wyciek prawie 9 milionów rekordów)"),
(S,"Zaobserwowano wykorzystanie podatności SQL injection w Roundcube"),
(S,"Duży cyberatak na lodówki i zamrażarki sklepowe we Francji."),
(C,"Włamanie do systemów IT urzędu miasta w zachodniopomorskim"),
(B,"BeyondTrust patches zero-day exploited in attacks since August"),
(T,"China-Linked Hackers Exploited BeyondTrust Zero-Day to Take Over Remote Support Servers"),
(C,"Adwersarz próbuje zakłócić dostawy energii dla wojska, firm i Polaków. Tu szuka słabych punktów"),
(N,"Kolejny wyciek danych, tym razem 2 500 000 pacjentów"),
(N,"(AKTUALIZACJA 2) Fakturownia.pl zhackowana – wykradziono faktury i dane kontrahentów"),
(Z,"Nowe włamanie \"Fingerprinta\" - ofiarą firma Fakturownia.pl"),
(Z,"Sprawcy ataku na system Medyc twierdzą, że ukradli dane 5 milionów pacjentów i 8 milionów zdjęć"),
(Z,"Sprawcy wycieku MyDr ponownie atakują - tym razem ofiarą aplikacja Medyc"),
(C,"Kolejny cyberatak na sklepy. Tym razem we Francji"),
(B,"Burger King Japan data breach exposes 11 million customer records"),
(T,"Xandr Fined a Record €8.6 Million for Relaying Grindr Data Revealing Sexual Orientation"),
(S,"Poważne luki bezpieczeństwa w routerach ASUS. Uwierzytelniony atakujący może wykonać dowolny kod w routerze z uprawnieniami roota"),
(B,"Critical BlockStrap flaw lets hackers run code on Magento servers"),
(B,"Microsoft: October Windows update may break Smart App Control"),
(T,"Researchers Demonstrate OpenBSD Root Exploit Chaining 37-Year-Old Shared-Memory Bug"),
(B,"Drupal patches critical RCE flaws, warns exploits may emerge soon"),
(B,"Hackers breach Microsoft 365 tenants via ConnectWise supply-chain attack"),
(B,"Hackers exploit SiteGuard WAF flaw to run commands as admins"),
(S,"Reklamami na Google infekowali telefony / komputery na całym świecie. Operacja AdFection."),
(S,"Tłumy i hackowanie na żywo – Michał Sajdak na VIII Forum Cyberbezpieczeństwa"),
(C,"AI to wielka siła. Jak Chiny mogą wpływać na inne kraje?"),
(C,"Ciepło z serwerowni ogrzeje polskie domy?"),
(C,"Wielkopolskie: masowe podszywanie się podczas głosowania online"),
(C,"Gawkowski spotkał się z platformami. Postawił twarde żądania: te konta mają znikać"),
(C,"Polacy wolą zagraniczne technologie. Raport ujawnia skalę problemu"),
(C,"Okulary ze sztuczną inteligencją zyskują popularność. Unijny organ ostrzega"),
(C,"ChatGPT pomaga w zbrodniach?"),
]
POOL = [
    {"title": title, "link": f"{domain}{index}", "description": ""}
    for index, (domain, title) in enumerate(RAW)
]
FREQUENCY = document_frequency([article["title"] for article in POOL])


def find(fragment):
    return next(article for article in POOL if fragment in article["title"])


# Pairs from different sources describing the same event.
SAME = [
 ("Fakturownia.pl zhackowana", "ofiarą firma Fakturownia"),
 ("BeyondTrust patches zero-day", "Exploited BeyondTrust Zero-Day"),
 ("lodówki i zamrażarki", "cyberatak na sklepy"),
 ("Cisco patches new Secure Email", "Cisco Warns of Active Attacks"),
 ("Palo Alto Networks warns of PAN-OS", "Palo Alto Networks Patches PAN-OS"),
 ("CISA warns admins to immediately fix Ivanti", "CISA Urges Immediate Ivanti"),
 ]

# Pairs describing different events.
DIFFERENT = [
 ("Langflow's Critical", "CISA Urges Immediate Ivanti"),
 ("Microsoft fixes VPN issues", "Microsoft Patches Record 1,413"),
 ("Microsoft: October Windows update", "Microsoft Patches Record 1,413"),
 ("Microsoft: October Windows update", "Microsoft fixes VPN issues"),
 ("Hackers breach Microsoft 365", "Microsoft Patches Record 1,413"),
 ("Google wypłacił", "Researchers Used a Public OpenAI Model"),
 ("Kolejny wyciek danych, tym razem", "ENEL-MED"),
 ("Wakacje.pl zhackowane", "Fakturownia.pl zhackowana"),
 ("Burger King Japan", "Xandr Fined"),
 ("Critical BlockStrap", "Hackers exploit SiteGuard"),
 ("Zaobserwowano wykorzystanie podatności SQL", "Poprzez SQL injection"),
 ("Polski ślad w cyberataku", "Kolejny cyberatak na sklepy"),
 ("Is AI pentesting", "The Blind Spots of Agentic Pentesting"),
]


class TestSameEvent(unittest.TestCase):

    def test_same_events_are_detected(self):
        for first, second in SAME:
            with self.subTest(first=first, second=second):
                self.assertTrue(
                    same_event(find(first)["title"], find(second)["title"], FREQUENCY)
                )

    def test_different_events_from_different_sources_are_kept_apart(self):
        for first, second in DIFFERENT:
            a, b = find(first), find(second)
            if a["link"][:20] == b["link"][:20]:
                continue
            with self.subTest(first=first, second=second):
                self.assertFalse(same_event(a["title"], b["title"], FREQUENCY))

    def test_shared_cve_means_same_event(self):
        self.assertTrue(
            same_event(
                "Exploit for CVE-2026-12345 published",
                "Łatka dla CVE-2026-12345 już dostępna",
                {},
            )
        )

    def test_known_limitation_name_at_title_start_in_english(self):
        # Both titles start with "Drupal" and one is in Title Case, so the
        # name cannot be recognized; the duplicate is missed on purpose
        # rather than risking false matches.
        self.assertFalse(
            same_event(
                find("Drupal patches critical RCE flaws")["title"],
                find("Drupal Patches Critical Field UI")["title"],
                FREQUENCY,
            )
        )


class TestGroupEvents(unittest.TestCase):

    def test_groups_from_real_pool(self):
        representatives = group_events(POOL)
        groups = [r for r in representatives if r["related"]]

        self.assertEqual(len(groups), 6)
        self.assertEqual(
            len(representatives) + sum(len(r["related"]) for r in representatives),
            len(POOL),
        )

    def test_same_source_is_never_merged(self):
        for representative in group_events(POOL):
            sources = [representative["link"][:20]] + [
                related["link"][:20] for related in representative["related"]
            ]
            self.assertEqual(len(sources), len(set(sources)))

    def test_polish_source_represents_group_on_equal_score(self):
        articles = [
            {"title": "Fakturownia.pl hacked by Fingerprint group", "link": "https://www.bleepingcomputer.com/x", "description": ""},
            {"title": "Nowe włamanie - ofiarą firma Fakturownia.pl", "link": "https://zaufanatrzeciastrona.pl/y", "description": ""},
        ]
        representative = group_events(articles)[0]

        self.assertIn("zaufanatrzeciastrona.pl", representative["link"])
        self.assertEqual(len(representative["related"]), 1)

    def test_original_articles_are_not_modified(self):
        articles = [find("BeyondTrust patches zero-day"), find("Exploited BeyondTrust Zero-Day")]
        group_events(articles, pool=POOL)

        for article in articles:
            self.assertNotIn("related", article)


class TestContinuations(unittest.TestCase):

    def test_event_from_recent_digest_is_marked(self):
        recent = [{"title": find("Fakturownia.pl zhackowana")["title"], "link": "https://niebezpiecznik.pl/old"}]
        article = dict(find("ofiarą firma Fakturownia"))

        mark_continuations([article], recent, pool_titles=[a["title"] for a in POOL])

        self.assertTrue(article.get("continuation"))

    def test_unrelated_article_is_not_marked(self):
        recent = [{"title": find("Fakturownia.pl zhackowana")["title"], "link": "https://niebezpiecznik.pl/old"}]
        article = dict(find("Burger King Japan"))

        mark_continuations([article], recent, pool_titles=[a["title"] for a in POOL])

        self.assertFalse(article.get("continuation", False))

    def test_no_recent_records_marks_nothing(self):
        article = dict(find("Burger King Japan"))
        mark_continuations([article], [])

        self.assertFalse(article.get("continuation", False))


class TestEventNames(unittest.TestCase):
    """Titles from the digest test of 22.10.2026 (v26)."""

    PHP = [
        ("https://www.bleepingcomputer.com/a", "Amazon says PHP2Shell exploitation began 4 days before patches"),
        ("https://thehackernews.com/b", "Someone Tried to Exploit PHP2Shell 4 Days Before the Vulnerabilities Were Publicly Disclosed"),
        ("https://thehackernews.com/c", "PHP2Shell: What Actually Protects You Before the 14:00 UTC PHP RCE Patch, and What Doesn't"),
        ("https://www.securityweek.com/d", "PHP2Shell Exploitation Started Days Before Patches"),
        ("https://www.bleepingcomputer.com/e", "CISA: Hackers chain Plex flaws in Plex2Shell attacks to breach servers"),
        ("https://therecord.media/f", "Russian APT28 hackers target Polish energy firm"),
        ("https://www.securityweek.com/g", "APT28 Uses New Backdoor Against NATO Shipbuilder"),
    ]

    def articles(self):
        return [{"title": title, "link": link, "description": ""} for link, title in self.PHP]

    def test_shared_event_name_merges_articles_also_from_the_same_source(self):
        groups = group_events(self.articles())
        php = [g for g in groups if "PHP2Shell" in g["title"]]

        self.assertEqual(len(php), 1)
        self.assertEqual(len(php[0]["related"]), 3)

    def test_different_event_names_and_group_names_are_not_merged(self):
        groups = group_events(self.articles())
        titles = [g["title"] for g in groups]

        self.assertEqual(sum("Plex2Shell" in t for t in titles), 1)
        self.assertEqual(sum("APT28" in t for t in titles), 2)

    def test_similar_titles_from_one_source_without_strong_match_stay_apart(self):
        articles = [
            {"title": "Microsoft fixes Exchange sign-in bug", "link": "https://www.bleepingcomputer.com/x", "description": ""},
            {"title": "Microsoft fixes Exchange mail flow bug", "link": "https://www.bleepingcomputer.com/y", "description": ""},
        ]
        self.assertEqual(len(group_events(articles)), 2)


if __name__ == "__main__":
    unittest.main()
