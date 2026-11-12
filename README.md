[English](README.md) | [Polski](README_PL.md)

# CyberSec NewsDigest AI

An automated daily cybersecurity news digest in Polish, built with Python, GitHub Actions, RSS feeds and AI summaries, delivered to Discord.

## Project Goal

CyberSec NewsDigest AI collects cybersecurity news from Polish and English RSS feeds, selects the relevant articles, merges reports about the same event, writes a concrete summary of each article in Polish and delivers a daily digest to Discord, together with a weekly top 5 and a monthly top 10.

The project runs with a budget of 0 PLN, using free service tiers only (GitHub Actions, Groq, Google Gemini without billing, Mistral free plan, LanguageTool public API, cron-job.org).

## Project Status

The digest has been running in production since October 2026 (version v36). Every change is described, with its verification, in [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

| Stage | Scope | Status |
|---|---|---|
| 1 | RSS ingestion, URL validation, quality checks | completed (v1–v10) |
| 2 | Persistent article history, filtering of published links | completed and verified |
| 3 | Rule-based categorization and priority scoring | completed and verified |
| 4 | Delivery of the digest to Discord | completed and verified |
| 5 | Selection quality: Polish keywords, relevance threshold, source limits, promotional filter; 11 sources and a 3-day age filter (v26) | completed and verified |
| 6 | Automatic start: external alarm clock cron-job.org, GitHub's schedule as a backup, one digest per day (v14, v19, v24) | completed; the first digest started by the alarm clock confirmed on 2026-10-23 |
| 7 | Monthly archive of delivered articles (v15) | completed and verified |
| 8 | Merging articles about the same event and the "🔁 Ciąg dalszy" section (v16, v26, v29, v31) | completed; merging observed in live digests |
| 9 | Monthly top 10 on a separate channel (v17) | completed; verified in manual runs, the first scheduled run on 2026-11-01 |
| 10 | AI summaries in Polish with a mandatory glossary from CyberSec Mozaika (v18, v21, v25) | completed and verified |
| 11 | Test channel for runs from branches (v20) | completed and verified |
| 12 | Weekly top 5 and one-time sending of tops (v22, v23) | completed; the first live preview reached `#top-tygodnia` on 2026-10-21, the first scheduled run on 2026-10-26 |
| 13 | Full article text from the article page and inflection of terms (v27) | completed and verified |
| 14 | 🔥 marker for vulnerabilities from the CISA KEV catalog (v28) | completed and verified |
| 15 | Language quality: style list, language check, proofreading by Google Gemini with LanguageTool hints (v29, v30) | completed and verified |
| 16 | "Weekendowa lektura" split into links, merging by company names, alarm on workflow failure (v31) | completed and verified |
| 17 | Language log: corrections of summaries saved in the archive (v32) | completed; verified with unit tests and real errors from the logs |
| 18 | Quality of summaries and tops: no closing formulas, labels only with support, tops merging by CVE, Polish leaders, clean-up and correction of top summaries (v33) | completed; verified on the test branch and a simulation on the archive |
| 19 | Summaries that say why it matters and read easily: what – why it matters – what to do, context of earlier reports, CISA KEV for the AI, event summaries in the tops (v34) | completed; verified on the test branch (digest and weekly top) |
| 20 | One vulnerability, one item: merging by CVE ids after the page texts and after the summaries; language correction by Gemini only; advice only when concrete (v35) | completed; checked on the digests of 27–28 October 2026 |
| 21 | Soft problems never cut a summary, no headless fragments, smoother sentences, no added phishing (v36) | completed; checked on the digest of 29 October 2026 |
| 22 | Language correction every day: chunks of 5 summaries, lighter Gemini models, Mistral as a fallback; no empty "other flaws" (v37a) | completed; verified by unit tests |
| 23 | The tops on the same chain as the digest: event stories in chunks, Mistral before Groq (v37b) | completed; verified by unit tests |
| 24 | Data for the bridge to CyberSec Mozaika: glossary entries in the archive (`terms`), tops saved in `data/tops/`, data contract and file placement tests, mirror v90, exporter moved to `cybersec-most` (v38) | completed; verified by unit tests |
| 25 | Data guards for the bridge: contract tests for the tops (`data/tops/`) and the style list, `proofread` field in the archive (v39) | completed; verified by unit tests |
| 26 | Explanations in parentheses only for "podwyższenie uprawnień" and "poświadczenia": mirror v92 after the author's decision from the bridge (v40) | completed; verified by unit tests |
| 27 | Karton Prasówki in the repository (`docs/karton.html`) with a version guard (v41) | completed; verified by unit tests |
| 28 | Clean Polish: Morfeusz 2 catches untranslated English words and typos from the correction; Gemini lite last in the correction queue (v42) | completed; verified by unit tests |
| 29 | Calque dictionary: 29 new rows in the calque list accepted by JW, Polish month names in dates (v43) | completed; verified by unit tests |
| 30 | No echo: one story, one item – merging by company names, product versions and amounts in the summaries (v44) | completed; verified by unit tests |
| 31 | Less, but better: at most 10 items in the daily digest, no sponsored content (v45) | completed; verified by unit tests |
| 32 | Polish polish: language rules document in the prompts, Morfeusz 2 grammar checks, industry usage over purism (v46) | completed; verified by unit tests |
| 33 | Separate stories: in the weekly and monthly tops a company name does not join events with different CVE ids (v47) | completed; verified by unit tests |
| 34 | Common platforms: inflected platform names ("Androida") no longer join different stories (v48) | completed; verified by unit tests |
| 35 | Hashes: "hash" is industry usage, "hashe (skróty haseł)" at the first mention (v49) | completed; verified by unit tests |
| 36 | One Tuesday: Patch Tuesday as one item, continuations from 7 days, items without a summary last in the daily limit (v50) | completed; verified by unit tests |

## Current Implementation

### Sources and selection

- Retrieves RSS or Atom entries from eleven sources: Polish (Niebezpiecznik, Sekurak, Zaufana Trzecia Strona, CyberDefence24, CERT Polska, Kapitan Hack) and English (BleepingComputer, The Hacker News, SecurityWeek, The Record, Krebs on Security). Entries older than 3 days are skipped. A failing feed does not stop the run.
- Extracts titles, links and descriptions (decoding HTML entities in titles) and skips entries with missing titles or invalid URLs.
- Keeps a persistent history in `data/seen_articles.json`: `seen_links` (encountered) and `published_links` (delivered). Only links already delivered are excluded from later digests.
- Categorizes articles as critical news, vulnerabilities and Poland-related news, using English and Polish keywords written as word stems (Polish stems checked against forms generated by the Morfeusz 2 morphological analyzer).
- Scores articles (critical +3, vulnerabilities +2, Poland +1) and subtracts 2 points for titles in an event, report or advice context (conferences, experts, how-to guides, regulatory fines).
- Excludes promotional titles (webinars, trainings, e-books, discounts, sponsored content) and English roundups (ThreatsDay, Weekly Recap, In Other News), whose stories reach the digest separately.
- Summarizes up to 14 candidates with a score of at least 2 and, after merging duplicates, sends at most 10 items (v45: KEV, CVE ids, other sources and Polish sources rank higher). Each source is limited to 4 articles (Niebezpiecznik 2, SecurityWeek and The Record 3); limits are set in `src/article_selection.py`.
- Splits "Weekendowa lektura" (Zaufana Trzecia Strona) into its links: each link to another site becomes a candidate article with the ZTS comment as its description and goes through the same scoring. A question mark in the link title counts as commentary (−2), links to threat-research publications (Unit 42, Securelist, ESET, Mandiant, Microsoft Security Blog, Talos, CERT Polska and others) get +2, links to video, chat and social media are skipped. At most 3 such links per digest, shown "via Zaufana Trzecia Strona".

### Events and markers

- Merges articles about the same event into one item with "także:" links to the other sources. The rules: similar titles; a shared CVE id or an event name with digits (e.g. PHP2Shell), also within one source; a shared company or product name ("Quest Diagnostics", "Capcom") when the article texts show the word is a name. Platform names that appear in many different stories (Microsoft, Windows, Chrome, Python…) never merge on their own. Since v35 the selected articles are merged once more by their CVE ids after the article pages are fetched (many feeds give only a teaser without the CVE id) and again after the summaries, so one vulnerability is one item.
- Shows articles about events delivered in the last 7 days (v50; 3 before) in a separate "🔁 Ciąg dalszy" section, also when only the summary (for lektura links also the linked page) shares a CVE id with such an event.
- Marks with 🔥 articles about vulnerabilities from the CISA KEV catalog (confirmed exploitation in attacks). The marker is set by code, not by the AI: CVE ids from the title and the beginning of the article text are compared with the catalog downloaded on every run (from CISA, with CISA's GitHub mirror as a fallback). The tops check the saved CVE ids again against the current catalog. Without the catalog the digest is sent without markers.

### AI summaries in Polish

- Each article gets a concrete summary in Polish (2–3 short sentences, up to about 420 characters; 1 sentence when the material is only a short teaser) written by Groq `gpt-oss-120b`, with `qwen3.8-27b` as a fallback. Since v34 the summary answers the questions of a SOC practitioner: what happened and whom it concerns (in plain words, CVE ids not first), why it matters (exploitation in attacks, public exploit, scale, patch or no patch) and what to do, if the article says so. The AI is told when a vulnerability is in the CISA KEV catalog, and every article gets the latest earlier report of the same event from the archive of 14 days as context (the story; "what is new"). Sentences over 25 words and more than 2 CVE ids go back for correction (soft: never cut); a sentence with no concrete detail (number, date, CVE id, name) but with evaluative words ("poważne zagrożenie", "współpracuje z ekspertami") counts as filler. "Actively exploited" and "no patch" are allowed only when the material says so. Requests are spaced out (at least 20 s) and a batch that no model handled is retried once at the end.
- Material: the full feed text or description; when the feed gives fewer than 600 characters, the article text is fetched from its page (paragraphs without menus, ads and footer). Page text is only material for the AI and is never saved.
- Terms follow the glossary `data/glosariusz_mirror.csv`, a mirror of the CyberSec Mozaika glossary. Simple forbidden forms are corrected by code without an AI request ("poprawka" → "łatka", "zdalne wykonanie kodu" → "RCE"); explanations in parentheses are added by code at the first occurrence of 2 chosen terms, in the case of the term ("podwyższenia (eskalacji) uprawnień", "poświadczeń (danych logowania)"; since v40).
- Quality check (`src/summary_quality.py`): glossary violations, filler phrases ("co podkreśla wagę…", "nie została podana"), relative time words, uninflected terms after a preposition, numbers and CVE ids not in the material, the labels "zero-day" and "natychmiast" (urgent) when the article does not use them, closing formulas without content ("Zaleca się natychmiastową aktualizację."), summaries that are too long, in English or only restate the title, and calques from the editable style list `data/styl_unikaj.csv`. A summary with a problem goes back to the AI for one correction; if a problem remains, code removes the faulty sentences. A summary is dropped only when no correct sentence is left (or it is still in English).
- Proofreading: since v37a in chunks of 5 summaries, with grammar hints from LanguageTool; Google Gemini first (`gemini-3.8-flash`, `gemini-3.5-flash`, then the lighter `-flash-lite`), and from the second round also Mistral (`ministral-14b-2512`, free plan); up to three rounds with a 30 s and 60 s wait. No Groq since v35, because it made the Polish worse; when all models fail, the summaries stay without correction. A correction is accepted only when it keeps the numbers, CVE ids and length; every correction is logged as "przed" / "po".
- Language log (v32): every correction of a summary is saved with the article in the archive (field `language`): forbidden glossary forms with the entry id, calques from the style list, terms left uninflected, replacements made by code and changes made by the proofreading, each with its outcome (fixed by the AI, by code, still present, or summary dropped). The notes describe the AI output only; they change nothing and never write to the glossary.

### Delivery and tops

- Sends the digest to Discord through a webhook, grouped by each article's most important category, with clickable titles, source domains and the "via" label, split into messages within Discord's length limit.
- Records links in `published_links` only after a successful delivery, and archives each delivered article (date, title, link, source, categories, score, summary, CVE ids, KEV, via, language notes) in `data/archive/YYYY-MM.json`. History and archive are saved even when the digest step fails (unless the run is cancelled).
- On Mondays sends the top 5 events of the previous week to `#top-tygodnia`, and on the 1st of each month the top 10 events of the previous month to a separate channel (ranked by number of articles, then sources and score), with the archived summaries. Each top is sent only once (marker `data/last_top.json`). Since v33 the tops also merge records that share a CVE id or an event name with digits in any title (also of related articles), show each event under its best record (highest score, then a Polish source, then the most related articles), leave out roundups, tidy the archived summaries by code (an English or title-only summary falls back to the next article) and send them through the language correction (since v37b the same chain as the digest: Gemini, lite, Mistral); every change made by code is logged as "PORZĄDEK". Since v34 one request per top writes a short story of each whole event (what broke, how it went, what is happening now and whether it escalates, how to patch) from the Polish summaries of all its articles and the titles of related articles; it is used only when it passes the checks against that material (log "ZESTAWIENIE AI").
- Runs from branches other than `main` send only to the test channel, with a "🧪 TEST" banner, and save nothing.
- When the digest or a top workflow fails, an alarm with a link to the log goes to the test channel.

### Triggers

The main trigger is an external alarm clock: cron-job.org calls the GitHub API (workflow_dispatch with the `budzik` input) at 06:17 Polish time, Monday to Saturday, and starts the tops on Mondays (weekly) and on the 1st of the month (monthly) at 08:17. It uses a fine-grained PAT limited to this repository and the Actions permission (Read and write), stored only in cron-job.org; the token must be renewed before it expires (one year). GitHub's schedule stays as a backup (digest attempts at 06:17–09:17, tops at 08:17–11:17, `Europe/Warsaw`), because GitHub skips or delays many scheduled runs. The first completed alarm-clock or scheduled run sends the digest, later runs that day end without sending (marker `data/last_digest.json`). A manual run (leave `budzik` unchecked) is never blocked and also counts as today's digest. A concurrency group prevents overlapping runs.

## Latest Verified Results

Version v35 (2026-10-28):

- Unit tests: **404 passed** (v36, 2026-10-29: soft problems never cut a summary, no headless fragments, smoother sentences, "z/ze" fixed, no added phishing).
- On the archive: Brotli (27 October, three items) and Apple CVE-2026-86950 (28 October, two items) each become one item; merges across all of October are correct. 10 of 110 October summaries had CVE ids with non-breaking hyphens that code could not see – now recognized.
- The new filler rules flag only real filler on 107 summaries (no false hits); the preposition autofix ("we wtyczce", "ze wsparciem") changes only wrong forms.

Version v33 (2026-10-26):

- Unit tests: **346 passed**.
- Weekly top 5 for 19–25 October run from the branch: PHP2Shell as one event (17 articles, 7 sources) under a Polish title, no duplicate, no Fortinet/FortiSIEM merge, no roundup; the Gemini correction fixed the old summaries.
- The rules catch the closing formulas and "nie są znane" in the summaries of 26 October; the style list caught six calques in the branch digest.

Version v32 (2026-10-25):

- Unit tests: **307 passed**.
- Language notes checked on real errors from the logs of 22–25 October 2026 ("rekordy pacjentów", "AI‑zarządzanego", "patchują", "przed exploit", "eksploatując", "intruzji"): all recorded, with entry ids H166 and H153 where the glossary has them.

Version v31 (2026-10-25):

- Test on the `v31-lektura` branch: "Weekendowa lektura" episode 699 split into 53 parts, 3 entered the digest; after the fixes the ranking favours threat-research analyses (Unit 42, Mandiant) over commentary.
- October archive (70 articles): the top merges Quest Diagnostics, Capcom and Arista VCO without new wrong merges.

Earlier: the v30 test fixed 6 of 6 summaries in the Gemini proofreading; the v28 test marked 2 of 20 articles with 🔥 (catalog of 1754 entries). Figures describe specific runs; details of each version are in the changelog.

## Known Limitations

- Priority scores are keyword-based indicators, not an AI assessment of editorial relevance.
- Event merging is rule-based and can rarely merge two different stories or miss a pair; such cases are watched and fixed with real examples.
- The AI can still make mistakes that the checks cannot detect, e.g. a fact that is in the material but placed in the wrong context (a year from the title used in a date). Summaries are marked as AI-generated in the digest.
- Article titles stay in the language of the source.
- There is no backlog of articles: an eligible article that disappears from its feed before being selected is no longer available.
- `seen_links` means "encountered", not "published"; only `published_links` excludes articles from later digests.

## Roadmap

- **Bridge to CyberSec Mozaika:** a weekly report (`bridge_report.py` in the private repository `cybersec-most`) with proposals for the mother workbook: most broken forms, calques, live examples, convention differences. Since v38 the digest provides the data (a `terms` field in the archive, tops in `data/tops/`) and guards its shape with a contract test; the report only proposes, and the Mozaika mother workbook stays the single source of truth.
- Branch protection for `main`.

- Experiment with the writing model: Google Gemini writes the daily summaries (Groq as fallback) and gets more article material; compared on regular weekday digests with the current setup.

Planned features are not considered implemented until they have been developed and verified.

## Architecture

1. Retrieve entries from the RSS/Atom feeds and skip entries older than 3 days.
2. Validate entries, remove duplicate links, split "Weekendowa lektura" into links.
3. Update the history and exclude links already published.
4. Categorize, score, exclude promotional titles and roundups.
5. Select up to 14 candidates within source limits (at most 10 items after merging, v45); merge articles about the same event; mark follow-ups of the last 7 days (v50).
6. Fetch article pages when the feed text is too short; mark CISA KEV vulnerabilities.
7. Write AI summaries, check and correct them, proofread them; keep the language notes.
8. Format and deliver the digest to Discord.
9. Record published links, archive delivered articles, save the day marker.

The weekly and monthly tops read the archive. GitHub Actions runs the workflows; Python implements the logic.

## Repository Structure

Workflows (`.github/workflows/`):

- `daily-digest.yml` — daily digest: alarm-clock input, backup schedule, unit tests, digest run, saving history and archive, failure alarm.
- `weekly-top.yml` — weekly top 5 (Mondays).
- `monthly-top.yml` — monthly top 10 (1st of the month).
- `backfill-summaries.yml` — one-time manual backfill of summaries in the archive (preview, then save).

Code (`src/`):

- `main.py` — the daily digest run.
- `rss_helpers.py` — URL validation, duplicate links, title cleanup, article age.
- `deduplication.py` — deduplication and source tracking.
- `article_history.py` — persistent history of seen and published links.
- `article_selection.py` — keywords, categories, scoring, promotional and roundup filter, source limits, lektura ranking.
- `roundup_parts.py` — splitting "Weekendowa lektura" into links.
- `event_grouping.py` — merging articles about the same event and follow-ups.
- `article_pages.py` — article text from the article page.
- `kev.py` — 🔥 marker: CISA KEV catalog and CVE ids.
- `ai_summaries.py` — AI summaries (Groq), corrections and proofreading.
- `gemini.py` — Google Gemini for proofreading.
- `mistral.py` — Mistral, the last fallback of proofreading (v37a).
- `languagetool.py` — grammar hints from LanguageTool.
- `glossary.py` — glossary rules from the mirror: prompt entries, forbidden forms, autofix, explanations in parentheses.
- `summary_quality.py` — quality and language checks of summaries, repair by code.
- `polish_words.py` — Morfeusz 2 word checks: untranslated English words and words invented by the language correction (since v42).
- `language_notes.py` — language log: corrections of summaries as notes for the archive.
- `discord_output.py` — digest formatting, message splitting, delivery.
- `article_archive.py` — monthly archive.
- `weekly_top.py`, `monthly_top.py` — tops from the archive.
- `run_guard.py`, `top_guard.py` — one digest per day, one top per week and month.
- `test_mode.py` — test runs from branches.
- `backfill_summaries.py` — backfill of summaries in the archive.
- `test_*.py` — unit tests (no network access), one file per module.

Data and tools:

- `data/seen_articles.json` — history of seen and published links.
- `data/archive/YYYY-MM.json` — monthly archive of delivered articles; since v38 with glossary entries (`terms`), since v39 with the language correction model (`proofread`, empty text = no correction).
- `data/last_digest.json`, `data/last_top.json` — markers of the last digest and tops.
- `data/tops/YYYY-Www.json`, `data/tops/YYYY-MM.json` — delivered weekly and monthly tops with their event stories (since v38; material for the bridge to CyberSec Mozaika).
- `data/glosariusz_mirror.csv` — mirror of the CyberSec Mozaika glossary (mother workbook v93, six columns). Exported by the private bridge repository `cybersec-most` (since v38; before that by `tools/eksport_mirrora.py` in this repository).
- `data/styl_unikaj.csv` — style list: calques and anglicisms with suggestions, edited by hand (`*` = any ending).
- `data/reguly_jezyka.md` — Prasówka language rules, edited by JW: the section "Nakazy dla modeli" goes to the prompts (since v46).
- `data/slowa_angielskie_ok.csv` — English words that may stay untranslated in summaries, edited by hand (`*` = any ending; since v42).
- `docs/karton.html` — Karton Prasówki, the interactive map of the digest, with version markers read by the bridge report (since v41).

## Configuration and Secrets

Repository secrets (Settings → Secrets and variables → Actions):

- `DISCORD_WEBHOOK_URL` — webhook of the digest channel. Without it, delivery is skipped without an error.
- `DISCORD_WEEKLY_WEBHOOK_URL` — webhook of `#top-tygodnia` (weekly top 5).
- `DISCORD_MONTHLY_WEBHOOK_URL` — webhook of the monthly top 10 channel.
- `DISCORD_TEST_WEBHOOK_URL` — webhook of the test channel: runs from branches and failure alarms. Without it, branch runs send nothing.
- `GROQ_API_KEY` — Groq API key for AI summaries (and, since v33, the fallback correction of top summaries). Without it, the digest is sent without summaries.
- `GEMINI_API_KEY` — Google Gemini API key (free quota, no billing) for proofreading of the digest and the tops; optional. Without it, proofreading uses the Groq models. The optional repository variable `GEMINI_MODEL` (comma-separated) overrides the model names, and `GEMINI_LITE_MODEL` the names of the lighter models (v37a).
- `MISTRAL_API_KEY` — Mistral API key (free plan, no card), the last fallback of the digest proofreading (v37a); optional. The optional variable `MISTRAL_MODEL` overrides the model.

Each secret is passed only to the workflow step that needs it. The cron-job.org token is kept only in cron-job.org. Never commit API keys, webhook URLs, tokens or passwords to the repository.

## Development and Testing

Run the unit tests from the repository root:

```bash
python -m unittest discover -s src -p "test_*.py"
```

The word checks need Morfeusz 2 (`pip install morfeusz2`; the workflows install it, since v42); without it they are skipped. Every workflow runs the tests before its main step. Changes are made on a branch, tested on the test channel, described in the changelog (PL/EN) and merged with Squash and merge.

## Documentation

The documentation is kept in English and Polish; every technical change is reflected in both README versions and in [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

**Karton Prasówki** (`docs/karton.html`) is the interactive map of the digest. Since v41 every version updates it in the same round (ecosystem rule 9 "Karton always up to date"): the markers `prasowka-wersja` and `plik-matka-wersja`, the visible state and the test count. `src/test_v41.py` turns red when the Karton is out of step with the changelog, the mirror or the test suite.

## Glossary licence

The file `data/glosariusz_mirror.csv` (forms, explanations in parentheses and rules) comes from the CyberSec Mozaika glossary: content licensed under CC BY-NC-ND 4.0, © 2026 Jan Wolski.
