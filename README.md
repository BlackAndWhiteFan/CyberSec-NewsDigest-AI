[English](README.md) | [Polski](README.pl.md)
_**CyberSec NewsDigest AI**_

An automated daily cybersecurity news digest built with Python, GitHub Actions, RSS feeds, and AI-powered content processing.

**Project Goal**

CyberSec NewsDigest AI is designed to collect cybersecurity news from selected RSS feeds, identify relevant articles, generate concise summaries, and deliver a daily digest to Discord.

The project aims to operate with a budget of 0 PLN, using free service tiers wherever possible.

Project Status

Phase 1 — RSS ingestion and quality checks: completed.

**Current Implementation:**

Retrieves RSS or Atom entries from six configured cybersecurity news sources.

Extracts article titles, links, and descriptions.

Skips entries with missing titles or invalid URLs.

Detects duplicate links within a single run.

Continues processing when an individual RSS feed fails.

Displays statistics about retrieved and processed entries.

The current GitHub Actions workflow runs unit tests and then executes the RSS ingestion script.

Latest Verified Run:

Feed entries found: 150

Unique article links: 150

Duplicate links: 0

Invalid entries skipped: 0

Failed RSS feeds: 0

Unit tests: 12 passed

These figures describe one successful run and may change over time. The absence of identical links does not guarantee that different URLs cannot refer to the same underlying story.

**Planned Features**

Persistent history of processed articles across workflow runs.

Filtering and prioritization of relevant cybersecurity news.

Generation of concise article summaries using AI.

Delivery of the daily news digest to Discord.

Automatic execution at a scheduled time every day.

Operational documentation and troubleshooting instructions.

Planned features are not considered implemented until they have been developed and verified.

**Architecture**

Target processing workflow:

Retrieve articles from configured RSS feeds.

Validate article data and detect duplicates.

Compare articles against persistent processing history.

Select and prioritize relevant news.

Generate concise summaries using an AI service.

Format and deliver the news digest to Discord.

Record processing results and maintain operational history.

GitHub Actions executes the workflow, while Python implements the processing logic.

**Repository Structure**

.github/workflows/daily-digest.yml — GitHub Actions workflow.

src/main.py — main RSS ingestion and processing script.

src/deduplication.py — article deduplication logic.

src/rss_helpers.py — helper functions for URL validation and duplicate-link detection.

src/test_deduplication.py — deduplication unit tests.

src/test_url_validation.py — URL validation and duplicate-detection tests.

**Configuration and Secrets**

Runtime configuration and credentials will be stored in GitHub Actions secrets or other appropriate secure configuration mechanisms when required.

Never commit API keys, Discord webhook URLs, passwords, or other credentials to the repository.

**Development and Testing**

Unit tests can be run locally from the repository root using:

python -m unittest discover -s src -p "test_*.py"

The GitHub Actions workflow also runs the tests before executing the RSS ingestion script.

**Documentation**

Project documentation will be maintained alongside the code in this repository. Technical changes should be reflected in the relevant documentation as the implementation evolves.
