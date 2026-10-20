"""Test runs from branches other than main (v20).

A run started on any branch other than main is a test run: it sends the
digest to a separate Discord test channel (secret DISCORD_TEST_WEBHOOK_URL)
with a "TEST" banner and saves nothing (no published links, archive or
daily marker). The real channel only ever receives digests from main, and a
test on a branch can no longer make main send the same articles again
(case of 2026-10-20). Without the test secret a test run sends nothing –
it never falls back to the real channel.
"""

import os


MAIN_BRANCH = "main"


def branch_name(environ=None):
    environ = os.environ if environ is None else environ
    return environ.get("GITHUB_REF_NAME", "").strip()


def is_test_run(environ=None):
    """True for GitHub Actions runs on a branch other than main."""
    name = branch_name(environ)
    return bool(name) and name != MAIN_BRANCH


def webhook_url(real_variable, environ=None):
    """Return (webhook URL, variable name) for this run."""
    environ = os.environ if environ is None else environ
    variable = "DISCORD_TEST_WEBHOOK_URL" if is_test_run(environ) else real_variable
    return environ.get(variable, "").strip(), variable


def banner(environ=None):
    return (
        f"🧪 **TEST** · gałąź `{branch_name(environ)}` · "
        "bez zapisu w historii i archiwum"
    )


def with_banner(messages, environ=None):
    """Prefix the first message with the test banner (test runs only)."""
    if not messages or not is_test_run(environ):
        return messages

    return [f"{banner(environ)}\n{messages[0]}"] + messages[1:]
