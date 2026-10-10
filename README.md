[English](README.md) | [Polski](README_PL.md)

# CyberSec NewsDigest AI

An automated daily cybersecurity news digest built with Python, GitHub Actions, RSS feeds, and AI-powered content processing.

## Project Goal

CyberSec NewsDigest AI is designed to collect cybersecurity news from selected RSS feeds, identify relevant articles, generate concise summaries, and deliver a daily digest to Discord.

The project aims to operate with a budget of 0 PLN, using free service tiers wherever possible.

## Project Status

**Phase 1 — RSS ingestion and quality checks: completed.**

**Phase 2 — Persistent article history and cross-run deduplication: implemented and verified.**

### Current Implementation

- Retrieves RSS or Atom entries from six configured cybersecurity news sources.
- Extracts article titles, links, and descriptions.
- Skips entries with missing titles or invalid URLs.
- Detects duplicate links within a single run.
- Skips article links recorded in the persistent history.
- Records newly processed article links in `data/seen_articles.json`.
- Continues processing when an individual RSS feed fails.
- Displays statistics about retrieved, skipped, and processed entries.
- Runs unit tests before executing the RSS ingestion script.
- Uses GitHub Actions to commit and push changes to the persistent article history when that file changes.

The current workflow can be triggered manually through GitHub Actions. Daily scheduling has not yet been configured.

### Latest Verified Results

The RSS ingestion test retrieved 150 entries across the configured feeds, with no invalid entries or failed feeds. A subsequent run confirmed that all 150 recorded links were loaded from persistent history and recognized as previously seen.

- Initial collection: 150 entries, 150 unique article links.
- Initial duplicate count: 0.
- Invalid entries skipped: 0.
- Failed RSS feeds: 0.
- Subsequent run: 150 previously seen articles recognized.
- Unit tests: 18 passed.

These figures describe verified runs and may change over time. Link-based deduplication does not guarantee that different URLs cannot refer to the same underlying story.

## Planned Features

- Filtering and prioritization of relevant cybersecurity news.
- Generation of concise article summaries using an AI service.
- Delivery of the daily news digest to Discord.
- Automatic execution at a scheduled time every day.
- Operational documentation and troubleshooting instructions.

Planned features are not considered implemented until they have been developed and verified.

## Architecture

The target processing workflow is:

1. Retrieve articles from configured RSS feeds.
2. Validate article data and detect duplicates.
3. Compare article links against persistent processing history.
4. Select and prioritize relevant news.
5. Generate concise summaries using an AI service.
6. Format and deliver the news digest to Discord.
7. Record processing results and maintain article history.

GitHub Actions executes the workflow, while Python implements the processing logic. The current implementation covers RSS ingestion, validation, deduplication, and persistent link history.

## Repository Structure

- `.github/workflows/daily-digest.yml` — GitHub Actions workflow.
- `data/seen_articles.json` — persistent history of previously seen article links.
- `src/main.py` — main RSS ingestion and processing script.
- `src/deduplication.py` — article deduplication logic.
- `src/rss_helpers.py` — helper functions for URL validation and duplicate-link detection.
- `src/article_history.py` — loading and saving persistent article history.
- `src/test_deduplication.py` — deduplication unit tests.
- `src/test_url_validation.py` — URL validation and duplicate-detection tests.
- `src/test_article_history.py` — persistent article history unit tests.

## Configuration and Secrets

Runtime configuration and credentials will be stored in GitHub Actions secrets or other appropriate secure configuration mechanisms when required.

Never commit API keys, Discord webhook URLs, passwords, or other credentials to the repository.

## Development and Testing

Unit tests can be run locally from the repository root using:

```bash
python -m unittest discover -s src -p "test_*.py"
```

The GitHub Actions workflow runs the tests before executing the RSS ingestion script.

## Documentation

Project documentation is maintained in English and Polish in this repository. Technical changes should be reflected in both versions as the implementation evolves.
