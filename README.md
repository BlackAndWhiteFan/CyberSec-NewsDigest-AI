[English](README.md) | [Polski](README_PL.md)

_# CyberSec NewsDigest AI_

An automated cybersecurity news digest built with Python, GitHub Actions, RSS feeds, and planned AI-powered content processing.

## Project Goal

CyberSec NewsDigest AI is designed to collect cybersecurity news from selected RSS feeds, identify relevant articles, generate concise summaries, and deliver a daily digest to Discord.

The project aims to operate with a budget of 0 PLN by using free service tiers wherever possible.

## Project Status

**Phase 1 — RSS ingestion, URL validation, and quality checks: completed.**

**Phase 2 — Persistent article history and publication-aware filtering: implemented; automated workflow and unit tests verified.**

**Phase 3 — Rule-based article categorization and prioritization: implemented and verified in a full workflow run.**

AI-powered summaries, Discord delivery, and automatic daily scheduling have not yet been implemented.

### Current Implementation

- Retrieves RSS or Atom entries from six configured cybersecurity news sources.
- Extracts article titles, links, and descriptions.
- Skips entries with missing titles or invalid URLs.
- Detects duplicate links within a single run and tracks the feeds in which an article appears.
- Maintains persistent article history in `data/seen_articles.json`, separating previously seen links from published links.
- Filters out articles whose links are already recorded in `published_links`, rather than excluding every previously seen article.
- Categorizes articles using keyword-based rules into critical news, vulnerabilities, and Poland-related news.
- Assigns preliminary priority scores based on matching categories.
- Selects up to 20 highest-priority eligible articles for the planned digest.
- Continues processing when an individual RSS feed fails.
- Displays diagnostic information about retrieved, skipped, and processed entries, as well as article selection.
- Runs unit tests before executing the RSS ingestion script.
- Uses GitHub Actions to commit and push changes to the persistent article history when that file changes.

The current workflow can be triggered manually through GitHub Actions. Daily scheduling has not yet been configured.

### Latest Verified Results

The latest verified run (v11, 2026-10-15) completed successfully:

- Unit tests: **30 passed**.
- All 6 feeds retrieved without errors; 150 entries processed and 20 articles selected for the digest.
- `published_links` is currently empty because Discord publishing has not yet been implemented.

These figures describe a specific run and may change over time. Verification results for each change are recorded in [CHANGELOG_PL_EN.md](CHANGELOG_PL_EN.md).

Link-based deduplication does not guarantee that different URLs cannot refer to the same underlying story.

### Important History and Selection Limitations

`seen_links` records links encountered during RSS ingestion. It does not mean that an article has been published.

`published_links` is intended to record links successfully delivered to the digest. Articles already recorded there are excluded from subsequent selections.

The current implementation does not persist complete article content as a backlog. Therefore, an eligible article that disappears from the RSS feeds before being selected may no longer be available for a later digest.

Priority scores are preliminary, keyword-based indicators. They do not represent an AI assessment or a guarantee of editorial relevance.

## Planned Features

- AI-powered summaries of selected cybersecurity articles.
- Formatting and delivery of the daily digest to Discord.
- Recording successfully published article links in `published_links`.
- Automatic execution at a scheduled time every day.
- Operational documentation and troubleshooting instructions.
- End-to-end verification of the complete workflow.

Planned features are not considered implemented until they have been developed and verified.

## Architecture

The target processing workflow is:

1. Retrieve articles from configured RSS feeds.
2. Validate article data and detect duplicate links.
3. Update persistent history with newly encountered links.
4. Exclude articles already recorded as published.
5. Categorize eligible articles and calculate preliminary priority scores.
6. Select up to 20 articles for the digest.
7. Generate concise summaries using an AI service.
8. Format and deliver the digest to Discord.
9. Record successfully published links and maintain article history.

GitHub Actions executes the workflow, while Python implements the processing logic. The current implementation covers RSS ingestion, validation, deduplication, persistent link history, rule-based categorization, prioritization, and article selection.

## Repository Structure

- `.github/workflows/daily-digest.yml` — GitHub Actions workflow and automated test execution.
- `data/seen_articles.json` — persistent history of seen and published article links.
- `src/main.py` — main RSS ingestion and processing script.
- `src/deduplication.py` — article deduplication and source tracking.
- `src/rss_helpers.py` — URL validation and duplicate-link detection helpers.
- `src/article_history.py` — loading, validating, saving, and filtering persistent article history.
- `src/article_selection.py` — keyword-based categorization, preliminary prioritization, and top-article selection.
- `src/test_deduplication.py` — deduplication unit tests.
- `src/test_url_validation.py` — URL validation and duplicate-detection tests.
- `src/test_article_history.py` — persistent article history and publication-filtering tests.
- `src/test_article_selection.py` — article categorization, prioritization, and selection tests.

## Configuration and Secrets

Runtime configuration and credentials will be stored in GitHub Actions secrets or other appropriate secure configuration mechanisms when required.

Never commit API keys, Discord webhook URLs, passwords, or other credentials to the repository.

## Development and Testing

Run unit tests locally from the repository root using:

```bash
python -m unittest discover -s src -p "test_*.py"
```

The GitHub Actions workflow runs the tests before executing the RSS ingestion script.

## Documentation

Project documentation is maintained in English and Polish in this repository. Technical changes should be reflected in both versions as the implementation evolves.
