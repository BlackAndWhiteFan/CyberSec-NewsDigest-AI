"""Detection of the same event reported by different sources.

Titles are compared word by word. Each word is shortened to its first
STEM_LENGTH letters, so Polish inflected forms ("Fakturownia",
"Fakturowni") and English forms ("patches", "patched") match. A shared word
counts only when it is rare in the day's pool of articles: "Fakturownia",
found in two titles, is strong evidence; "Microsoft", found in ten, is not.
Generic security vocabulary ("exploit", "wyciek", "million"...) is ignored.

Two titles describe the same event when they share a CVE identifier, when
their rare shared words reach SIMILARITY_THRESHOLD, or when they share one
name found in no other title. A word counts as a name when it has a capital
letter inside ("BeyondTrust") or is capitalized in the middle of a title
written in sentence case ("ofiarą firma Fakturownia.pl"). In Title Case
titles every word is capitalized, so capitalization says nothing there.

The rules favour precision: a missed duplicate only repeats a story, while a
false match would hide a different one.
"""

import re

from article_selection import prioritize_article, source_domain


STEM_LENGTH = 5
MIN_WORD_LENGTH = 3
SIMILARITY_THRESHOLD = 2.0
NAME_MIN_LENGTH = 6
NAME_ENDING_LENGTH = 3

CVE_PATTERN = re.compile(r"cve-\d{4}-\d{4,}")

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


def same_event(title_a, title_b, frequency, threshold=SIMILARITY_THRESHOLD, rare_limit=2):
    """Return True when two titles most likely describe the same event.

    rare_limit is the largest number of titles in which a word still counts
    as rare. Within one day it is 2 (only the compared pair); across a month
    it grows with the event, whose name appears in all of its articles.
    """
    if title_cves(title_a) & title_cves(title_b):
        return True

    words_a = title_words(title_a)
    words_b = title_words(title_b)
    shared = words_a.keys() & words_b.keys()

    score = sum(stem_weight(frequency.get(stem, 2), rare_limit) for stem in shared)

    if score >= threshold:
        return True

    # One name found only in these titles. The two words may differ only by
    # an inflectional ending (at most NAME_ENDING_LENGTH letters), so the name
    # "Medyc" does not match the adjective "medycznej".
    return any(
        frequency.get(stem, 2) <= rare_limit
        and (words_a[stem][1] or words_b[stem][1])
        and max(len(words_a[stem][0]), len(words_b[stem][0])) >= NAME_MIN_LENGTH
        and abs(len(words_a[stem][0]) - len(words_b[stem][0])) <= NAME_ENDING_LENGTH
        for stem in shared
    )


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
    are never merged, because a site does not report the same event twice.

    Returns one representative per group, highest priority first; each
    representative gets a "related" list with the other articles.
    """
    pool_titles = [
        a.get("title", "") for a in (pool if pool is not None else articles)
    ]
    frequency = document_frequency(pool_titles)

    groups = []

    for article in sorted(articles, key=representative_key, reverse=True):
        for group in groups:
            leader = group[0]
            sources = {source_domain(member) for member in group}

            if source_domain(article) in sources:
                continue

            if same_event(leader.get("title", ""), article.get("title", ""), frequency):
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

    for article in articles:
        if article.get("link") in recent_links:
            continue

        for record in recent_records:
            if same_event(article.get("title", ""), record.get("title", ""), frequency):
                article["continuation"] = True
                break

    return articles
