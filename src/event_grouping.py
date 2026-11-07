"""Detection of the same event reported by different sources.

Titles are compared word by word. Each word is shortened to its first
STEM_LENGTH letters, so Polish inflected forms ("Fakturownia",
"Fakturowni") and English forms ("patches", "patched") match. A shared word
counts only when it is rare in the day's pool of articles: "Fakturownia",
found in two titles, is strong evidence; "Microsoft", found in ten, is not.
Generic security vocabulary ("exploit", "wyciek", "million"...) is ignored.

Two titles describe the same event when they share a CVE identifier or an
event name made of letters and digits ("PHP2Shell", "Plex2Shell", "Log4j";
v26), when
their rare shared words reach SIMILARITY_THRESHOLD, or when they share one
name found in no other title. A word counts as a name when it has a capital
letter inside ("BeyondTrust") or is capitalized in the middle of a title
written in sentence case ("ofiarą firma Fakturownia.pl"). In Title Case
titles every word is capitalized, so capitalization says nothing there.

The rules favour precision: a missed duplicate only repeats a story, while a
false match would hide a different one.

Event names with digits are checked before word rarity, because a big event
appears in many titles of the day ("PHP2Shell" in five), so its name is not
"rare" (seen in the digest test of 22.10.2026: three PHP2Shell articles shown
separately). Such a shared name or CVE is also strong enough to merge two
articles from the same source (The Hacker News wrote about PHP2Shell twice).
"""

import re

from article_selection import is_roundup, prioritize_article, source_domain
from kev import article_cves


STEM_LENGTH = 5
MIN_WORD_LENGTH = 3
SIMILARITY_THRESHOLD = 2.0
NAME_MIN_LENGTH = 6
NAME_ENDING_LENGTH = 3

CVE_PATTERN = re.compile(r"cve-\d{4}-\d{4,}")
# A word of at least 5 characters with at least 2 letters and a digit.
EVENT_NAME_PATTERN = re.compile(r"(?<![\w-])(?=\w*[^\W\d_]\w*[^\W\d_])(?=\w*\d)\w{5,}(?![\w-])")
# Names of threat groups and generic technical names with digits are not one
# event: APT28 or Storm-1849 appear in many different stories.
NOT_EVENT_NAME = re.compile(r"^(apt|unc|fin|ta|tag|storm|dev|uat|win|windows|covid|ipv|sha|aes|arm|x86|x64)\d")

STOPWORDS = frozenset(
    """
    the and for with from that this into over after amid about via are was
    has have its new how why what who all can may than more most out off
    against under using use used now not but you your our their they his her
    one two three four five six first last says said report reports
    oraz jak dla czy ale lub nie się jest są był była było przez przy pod nad
    już jeszcze tylko nowy nowa nowe nowych nowym kolejny kolejna kolejne
    tym razem czyli który która które którzy jego jej ich tego tej ten
    """.split()
)


# Stems of generic news and security words that say nothing about which
# event an article describes.
GENERIC_STEMS = frozenset(
    """
    explo vulne attac hacke secur criti patch updat flaw zero day bug bugs
    warns fixes resea milli billi recor data users custo remot code malwa
    ranso breac leak leaks targe activ campa actor threa group syste devic
    serve netwo softw onlin compa firms gover state natio servi appli
    dane danyc wycie atak ataku ataki cyber haker włama podat luka luki lukę
    firma firmy firm polsk polsc polak polac ofiar spraw użytk klien pacje
    bezpi inter sieci kolej milio rekor syste aplik usług dostę infor
    """.split()
)


def title_cves(title):
    return set(CVE_PATTERN.findall(title.casefold()))


# v44: product names written as capitals, a hyphen or a space and a number
# ("GPT-6", "GPT 6": three articles on 7.11.2026 shown separately).
PRODUCT_VERSION = re.compile(r"(?<![\w-])([A-Z]{3,})[- ](\d{1,2})(?![\w.,])")
NOT_PRODUCT_VERSION = frozenset({"aes", "sha", "rsa", "cve", "top", "ios", "tls", "ssl", "php", "usb", "nis"})


def title_event_names(title):
    """Names with letters and digits, e.g. "php2shell" (CVE ids excluded)."""
    names = EVENT_NAME_PATTERN.findall(CVE_PATTERN.sub(" ", title.casefold()))
    names = {name for name in names if not NOT_EVENT_NAME.match(name)}
    names |= {
        f"{letters.lower()}{number}"
        for letters, number in PRODUCT_VERSION.findall(CVE_PATTERN.sub(" ", title))
        if letters.lower() not in NOT_PRODUCT_VERSION
    }
    return names


def strong_match(title_a, title_b):
    """True when two titles share a CVE id or an event name with digits."""
    return bool(
        title_cves(title_a) & title_cves(title_b)
        or title_event_names(title_a) & title_event_names(title_b)
    )


def is_title_case(words):
    """Return True when most longer words of a title are capitalized."""
    long_words = [word for word in words if len(word) >= 4 and word[0].isalpha()]

    if not long_words:
        return False

    capitalized = sum(1 for word in long_words if word[0].isupper())
    return capitalized / len(long_words) >= 0.6


def title_words(title):
    """Return {stem: (word, looks_like_name)} for comparing titles."""
    text = CVE_PATTERN.sub(" ", title)
    tokens = list(re.finditer(r"\w+", text))
    title_case = is_title_case([token.group() for token in tokens])
    words = {}

    for position, token in enumerate(tokens):
        original = token.group()
        word = original.casefold()

        if len(word) < MIN_WORD_LENGTH or word.isdigit() or word in STOPWORDS:
            continue

        stem = word[:STEM_LENGTH]

        if stem in GENERIC_STEMS:
            continue

        sentence_start = position == 0 or text[: token.start()].rstrip()[-1:] in ".:!?"
        name_like = bool(re.search(r"[a-ząćęłńóśźż][A-ZĄĆĘŁŃÓŚŹŻ]", original)) or (
            not title_case and original[0].isupper() and not sentence_start
        )

        previous_word, previous_name = words.get(stem, ("", False))
        words[stem] = (max(word, previous_word, key=len), name_like or previous_name)

    return words


def title_stems(title):
    """Return the set of word stems used for comparing titles."""
    return set(title_words(title))


def document_frequency(titles):
    """Count in how many distinct titles each stem appears."""
    counts = {}

    for title in set(titles):
        for stem in title_stems(title):
            counts[stem] = counts.get(stem, 0) + 1

    return counts


def stem_weight(count, rare_limit=2):
    """Weight of a shared stem found in `count` titles of the pool."""
    if count <= rare_limit:
        return 1.0

    if count == rare_limit + 1:
        return 0.25

    return 0.0


# v31: names of companies and products in Title Case titles ("Quest
# Diagnostics", "Capcom"). In such titles every word is capitalized, so the
# name rule further below says nothing. Two rules:
# 1. A pair of capitalized, non-generic words shared by both titles and rare
#    in the pool ("Quest Diagnostics").
# 2. A single shared word counts only when the article texts (descriptions,
#    Polish summaries) show it is a name: always capitalized, never written
#    in lowercase ("Capcom"). Without such evidence ("Popular", "Allows") a
#    single word never merges stories.
# Common platform names appear in different stories on the same day, so
# they never count.
COMMON_NAMES = frozenset(
    """
    microsoft google apple amazon meta windows linux android chrome firefox
    office exchange azure cloud server servers update updates security cisa
    fbi nsa europol interpol github openai cisco fortinet ivanti oracle
    router routers plugin plugins browser browsers firewall firewalls
    report reports warning researchers python javascript wordpress docker
    kubernetes nodejs gitlab apache nginx
    center centre manager software product products platform portal suite
    studio console service services system systems enterprise edition
    """.split()
)
# v33: the product-type words at the end ("Siemens Software Center" and
# "Atlassian … Data Center", 26.10.2026) name no company on their own.
CAPITALIZED = re.compile(r"[A-ZĄĆĘŁŃÓŚŹŻ][\w-]*")


def usable_name(word):
    lower = word.casefold()
    return not (
        len(lower) < 4
        or lower in STOPWORDS
        or lower in COMMON_NAMES
        or lower[:STEM_LENGTH] in GENERIC_STEMS
        or NOT_EVENT_NAME.match(lower)
        or lower.isdigit()
    )


def title_name_pairs(title):
    """Pairs of consecutive capitalized usable words, lowercased."""
    words = re.findall(r"[\w-]+", CVE_PATTERN.sub(" ", title))
    return {
        f"{a.casefold()} {b.casefold()}"
        for a, b in zip(words, words[1:])
        if CAPITALIZED.fullmatch(a) and CAPITALIZED.fullmatch(b) and usable_name(a) and usable_name(b)
    }


def text_names(texts):
    """Words that the texts show to be names: always capitalized, never
    written in lowercase ("Capcom potwierdziło…", "…dewelopera Capcom").
    The texts are article descriptions and Polish summaries, where ordinary
    words also appear in lowercase."""
    capitalized, lowercase = set(), set()

    for text in texts:
        for word in re.findall(r"[\w-]+", re.sub(r"<[^>]+>", " ", text or "")):
            if word.islower():
                lowercase.add(word)
            elif CAPITALIZED.fullmatch(word) and not word.isupper():
                capitalized.add(word.casefold())

    return {name for name in capitalized - lowercase if usable_name(name)}


def shared_rare_name(title_a, title_b, frequency, rare_limit, names=frozenset()):
    """True when both titles name the same rare company or product."""
    for pair in title_name_pairs(title_a) & title_name_pairs(title_b):
        if all(frequency.get(word[:STEM_LENGTH], 2) <= rare_limit for word in pair.split()):
            return True

    words_a = {word.casefold() for word in re.findall(r"[\w-]+", title_a)}
    words_b = {word.casefold() for word in re.findall(r"[\w-]+", title_b)}

    return any(
        len(word) >= 5 and frequency.get(word[:STEM_LENGTH], 2) <= rare_limit
        for word in words_a & words_b & set(names)
        if usable_name(word)
    )


# v44: places are names, but not of one event ("Japan Airlines" and
# "Japan's GMO", 29.10.2026).
PLACE_NAMES = frozenset(
    """
    japan japonia china chiny chin russia rosja rosji ukraine ukraina ukrainy
    europe europa europie europy poland polska polski usa america ameryka
    iran israel izrael korea north south india indie brazil germany niemcy
    france francja francji britain british brytyjski london california
    florida texas
    """.split()
)
FREQUENT_NAME_LIMIT = 8


def shared_frequent_name(title_a, title_b, frequency, names=frozenset()):
    """v44: one company or product named in both titles, even when it is in
    many titles of the day.

    A big event appears in many titles, so its name is not "rare" and the
    rarity rules miss it: Chainalysis (2.11 and 7.11.2026), Binance (31.10,
    4.11) and OpenSSH (6.11) each went out twice. The word must look like a
    name in a title (capital inside "OpenSSH", capital in the middle of a
    sentence-case title "z Binance"), or be a name in the article texts and
    capitalized in both titles. Common platforms (COMMON_NAMES), places and
    words in more than FREQUENT_NAME_LIMIT titles never count.
    """
    words_a = title_words(title_a)
    words_b = title_words(title_b)
    capitalized_a = {word.casefold() for word in re.findall(r"\w+", title_a) if word[0].isupper()}
    capitalized_b = {word.casefold() for word in re.findall(r"\w+", title_b) if word[0].isupper()}

    for stem in words_a.keys() & words_b.keys():
        word_a, name_a = words_a[stem]
        word_b, name_b = words_b[stem]

        if (
            frequency.get(stem, 2) > FREQUENT_NAME_LIMIT
            or max(len(word_a), len(word_b)) < 5
            or abs(len(word_a) - len(word_b)) > NAME_ENDING_LENGTH
            or not same_name(word_a, word_b)
            or word_a in PLACE_NAMES
            or word_b in PLACE_NAMES
        ):
            continue

        in_texts = (word_a in names or word_b in names) and word_a in capitalized_a and word_b in capitalized_b

        if name_a or name_b or in_texts:
            return True

    return False


def same_event(title_a, title_b, frequency, threshold=SIMILARITY_THRESHOLD, rare_limit=2, names=frozenset()):
    """Return True when two titles most likely describe the same event.

    rare_limit is the largest number of titles in which a word still counts
    as rare. Within one day it is 2 (only the compared pair); across a month
    it grows with the event, whose name appears in all of its articles.
    """
    if strong_match(title_a, title_b):
        return True

    words_a = title_words(title_a)
    words_b = title_words(title_b)
    shared = words_a.keys() & words_b.keys()

    score = sum(stem_weight(frequency.get(stem, 2), rare_limit) for stem in shared)

    if score >= threshold:
        return True

    if shared_rare_name(title_a, title_b, frequency, rare_limit, names):
        return True

    if shared_frequent_name(title_a, title_b, frequency, names):
        return True

    # One name found only in these titles. The two words may differ only by
    # an inflectional ending (at most NAME_ENDING_LENGTH letters), so the name
    # "Medyc" does not match the adjective "medycznej".
    return any(
        frequency.get(stem, 2) <= rare_limit
        and (words_a[stem][1] or words_b[stem][1])
        and max(len(words_a[stem][0]), len(words_b[stem][0])) >= NAME_MIN_LENGTH
        and abs(len(words_a[stem][0]) - len(words_b[stem][0])) <= NAME_ENDING_LENGTH
        and same_name(words_a[stem][0], words_b[stem][0])
        for stem in shared
    )


def same_name(word_a, word_b):
    """True when two words are one name in different inflected forms (v33).

    The weekly top of 26.10.2026 merged "Fortinet" with "FortiSIEM" (only
    the beginning "forti" is shared) and an MCP Python SDK story with a
    Pillow flaw (Python is a platform name, see COMMON_NAMES). Forms of one
    name share everything but the ending: "Capcom" / "Capcomu",
    "Fakturownia" / "Fakturowni".
    """
    a, b = word_a.casefold(), word_b.casefold()

    if not (usable_name(a) and usable_name(b)):
        return False

    shorter = min(len(a), len(b))
    prefix = 0

    while prefix < shorter and a[prefix] == b[prefix]:
        prefix += 1

    return prefix >= shorter - 2


def is_polish(article):
    return source_domain(article).endswith(".pl")


def representative_key(article):
    """Order group members: highest score first, Polish sources on ties."""
    return (prioritize_article(article), is_polish(article))


def group_events(articles, pool=None):
    """Merge articles about the same event from different sources.

    Articles are taken from the highest priority down; each one joins the
    first group whose leading article describes the same event, otherwise it
    starts a new group. Comparing with the leader only (not with every member)
    prevents chains of loosely related titles. Articles from the same source
    are merged only on a strong match (shared CVE id or event name with
    digits): a site may follow up its own story, but similar titles from one
    site are usually different stories.

    Returns one representative per group, highest priority first; each
    representative gets a "related" list with the other articles.
    """
    pool_titles = [
        a.get("title", "") for a in (pool if pool is not None else articles)
    ]
    frequency = document_frequency(pool_titles)

    groups = []

    # v29: CVE ids from the title and the lead of the feed text also tie
    # articles (PHP2Shell articles without the name in the title, 23.10).
    lead = {id(article): set() if is_roundup(article) else set(article_cves(article)) for article in articles}
    names = text_names(article.get("description", "") for article in (pool if pool is not None else articles))

    def strong(leader, article):
        return strong_match(leader.get("title", ""), article.get("title", "")) or bool(
            lead.get(id(leader), set()) & lead.get(id(article), set())
        )

    for article in sorted(articles, key=representative_key, reverse=True):
        for group in groups:
            leader = group[0]
            sources = {source_domain(member) for member in group}

            if source_domain(article) in sources:
                if strong(leader, article):
                    group.append(article)
                    break

                continue

            if strong(leader, article) or same_event(
                leader.get("title", ""), article.get("title", ""), frequency, names=names
            ):
                group.append(article)
                break
        else:
            groups.append([article])

    representatives = []

    for group in groups:
        leader = dict(group[0])
        leader["related"] = group[1:]
        representatives.append(leader)

    return representatives


def merge_by_cves(articles, use_summaries=False):
    """v35: merge selected articles that share a lead CVE id, after the page
    texts are fetched and "cves" set (kev.mark_kev).

    group_events runs before the article pages are fetched, and many feeds
    give only a teaser without the CVE id, so one vulnerability could appear
    several times (Brotli CVE-2026-111497 three times on 27.10.2026, Apple
    CVE-2026-86950 twice on 28.10.2026). The article with the highest
    priority (Polish source on ties) leads; the others and their related
    articles become its related articles. Returns the merged list, in the
    original order of the leaders.

    use_summaries=True (second pass, after the AI summaries): CVE ids in the
    summaries count too, for articles whose page names the CVE only after its
    first 600 characters (SecurityWeek on Apple CVE-2026-86950, 28.10.2026);
    the leader keeps its own summary.
    """
    from kev import find_cves

    def known(item):
        found = set(item.get("cves", []))

        if use_summaries:
            found |= set(find_cves(item.get("summary", "")))

        return found

    merged = []

    for article in articles:
        cves = known(article)
        target = next(
            (item for item in merged if cves and cves & known(item) and not is_roundup(item)),
            None,
        )

        if target is None or is_roundup(article):
            merged.append(article)
            continue

        if representative_key(article) > representative_key(target):
            position = merged.index(target)
            article, target = target, article
            merged[position] = target

        target["related"] = list(target.get("related", [])) + [
            {key: value for key, value in article.items() if key != "related"}
        ] + list(article.get("related", []))
        target["cves"] = sorted(set(target.get("cves", [])) | set(article.get("cves", [])))
        target["kev"] = sorted(set(target.get("kev", [])) | set(article.get("kev", [])))
        target["continuation"] = bool(target.get("continuation") or article.get("continuation"))

        if not target.get("previous") and article.get("previous"):
            target["previous"] = article["previous"]

    stage = "ze streszczeń" if use_summaries else "ze stron"
    print(f"SCALENIE PO CVE ({stage}): {len(articles) - len(merged)} artykułów dołączonych do innych pozycji")
    return merged


# v44: the same amounts of money or people in two summaries. The six
# articles about the CERT Polska bug bounty (4.11.2026) had different titles
# without a shared name, but the same "20 tys. zł" and "1 mln zł".
AMOUNT = re.compile(
    r"(\d{1,3}(?:[ \u00a0]\d{3})+|\d+(?:[.,]\d+)?)\s*(tys\.?|mln|mld|milion\w*|miliard\w*|million|billion)?"
    r"|(?<!\w)(milion|miliard)\w*",
    re.IGNORECASE,
)
MIN_AMOUNT = 1000


def amounts(text):
    """Numbers of at least MIN_AMOUNT, with "tys.", "mln", "mld" applied;
    years and CVE ids do not count."""
    text = re.sub(r"CVE-\d{4}-\d+", " ", text or "", flags=re.IGNORECASE)
    found = set()

    for match in AMOUNT.finditer(text):
        if match.group(3):
            found.add(10 ** 6 if match.group(3).lower().startswith("milion") else 10 ** 9)
            continue

        number = float(re.sub(r"[ \u00a0]", "", match.group(1)).replace(",", "."))
        unit = (match.group(2) or "").lower()

        if unit.startswith("tys"):
            number *= 1000
        elif unit.startswith(("mln", "milion", "million")):
            number *= 10 ** 6
        elif unit.startswith(("mld", "miliard", "billion")):
            number *= 10 ** 9
        elif 1900 <= number <= 2100:
            continue

        if number >= MIN_AMOUNT:
            found.add(round(number))

    return found


def summary_names(text):
    """Capitalized words in the middle of a sentence ("platforma CERT
    Polska", "program Bug Bounty")."""
    found = set()

    for match in re.finditer(r"(?<=[^.!?:\s] )([A-ZĄĆĘŁŃÓŚŹŻ][\w-]{4,})", text or ""):
        word = match.group(1)

        if usable_name(word) and word.casefold() not in PLACE_NAMES:
            found.add(word.casefold()[:STEM_LENGTH])

    return found


def same_story(article_a, article_b):
    """v44: two summaries tell the same story when they share two amounts,
    or one amount and one name (checked on the archive since 19.10.2026:
    only the bug bounty articles of 4.11 match)."""
    def text(article):
        return f"{article.get('title', '')}. {article.get('summary', '')}"

    shared = amounts(text(article_a)) & amounts(text(article_b))

    if len(shared) >= 2:
        return True

    return bool(shared) and bool(summary_names(article_a.get("summary", "")) & summary_names(article_b.get("summary", "")))


def merge_by_story(articles):
    """v44: merge selected articles whose summaries tell the same story
    (after the AI summaries), like merge_by_cves."""
    merged = []

    for article in articles:
        target = next(
            (item for item in merged if not is_roundup(item) and not is_roundup(article) and same_story(item, article)),
            None,
        )

        if target is None:
            merged.append(article)
            continue

        if representative_key(article) > representative_key(target):
            position = merged.index(target)
            article, target = target, article
            merged[position] = target

        target["related"] = list(target.get("related", [])) + [
            {key: value for key, value in article.items() if key != "related"}
        ] + list(article.get("related", []))
        target["cves"] = sorted(set(target.get("cves", [])) | set(article.get("cves", [])))
        target["kev"] = sorted(set(target.get("kev", [])) | set(article.get("kev", [])))
        target["continuation"] = bool(target.get("continuation") or article.get("continuation"))

    print(f"SCALENIE PO TREŚCI: {len(articles) - len(merged)} artykułów dołączonych do innych pozycji")
    return merged


CONTEXT_DAYS = 14


def add_context(articles, records, pool_titles=()):
    """v34: the latest earlier report of the same event from the archive
    (up to CONTEXT_DAYS days back) as "previous", so the AI can tell the
    story (test of 26.10.2026: a Plex2Shell write-up without the CISA
    warning of 22.10, which was older than the 3 days of "Ciąg dalszy").

    A record matches by a shared CVE id (the lead CVE ids, see kev), an
    event name with digits or the same-event rule. Articles that already
    have a context (continuations) are left as they are. Returns the
    number of articles that got a context.
    """
    from kev import find_cves

    frequency = document_frequency(
        list(pool_titles)
        + [record.get("title", "") for record in records]
        + [article.get("title", "") for article in articles]
    )
    names = text_names(
        [record.get("summary", "") for record in records]
        + [article.get("description", "") for article in articles]
    )
    ordered = sorted(
        (record for record in records if record.get("summary") and not is_roundup(record)),
        key=lambda record: record.get("date", ""),
        reverse=True,
    )
    added = 0

    for article in articles:
        if article.get("previous") or is_roundup(article):
            continue

        cves = set(article.get("cves", []))

        for record in ordered:
            if record.get("link") == article.get("link"):
                continue

            record_cves = set(record.get("cves", [])) | set(find_cves(record.get("title", ""), record.get("summary", "")))

            if (cves & record_cves) or same_event(
                article.get("title", ""), record.get("title", ""), frequency, names=names
            ):
                article["previous"] = {
                    "date": record.get("date", ""),
                    "title": record.get("title", ""),
                    "summary": record.get("summary", ""),
                }
                added += 1
                break

    print(f"KONTEKST: wcześniejsze doniesienie z archiwum dla {added} z {len(articles)} artykułów")
    return added


def mark_continuations(articles, recent_records, pool_titles=()):
    """Mark articles that continue events delivered in recent digests.

    recent_records are archive entries (with "title" and "link"). A marked
    article gets "continuation": True and is shown in a separate section.
    """
    frequency = document_frequency(
        list(pool_titles)
        + [record.get("title", "") for record in recent_records]
        + [article.get("title", "") for article in articles]
    )
    recent_links = {r.get("link") for r in recent_records}
    names = text_names(
        [record.get("summary", "") for record in recent_records]
        + [article.get("description", "") for article in articles]
    )

    for article in articles:
        if article.get("link") in recent_links:
            continue

        for record in recent_records:
            if same_event(article.get("title", ""), record.get("title", ""), frequency, names=names):
                article["continuation"] = True
                # v34: the earlier report, as context for the AI summary.
                article["previous"] = {
                    "date": record.get("date", ""),
                    "title": record.get("title", ""),
                    "summary": record.get("summary", ""),
                }
                break

    return articles
