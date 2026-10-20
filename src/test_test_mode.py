import unittest

import test_mode


MAIN = {"GITHUB_REF_NAME": "main", "DISCORD_WEBHOOK_URL": "real", "DISCORD_TEST_WEBHOOK_URL": "test"}
BRANCH = {"GITHUB_REF_NAME": "v20-kanal-testowy", "DISCORD_WEBHOOK_URL": "real", "DISCORD_TEST_WEBHOOK_URL": "test"}


class TestTestMode(unittest.TestCase):
    def test_main_uses_real_channel(self):
        self.assertFalse(test_mode.is_test_run(MAIN))
        self.assertEqual(test_mode.webhook_url("DISCORD_WEBHOOK_URL", MAIN), ("real", "DISCORD_WEBHOOK_URL"))

    def test_branch_uses_test_channel(self):
        self.assertTrue(test_mode.is_test_run(BRANCH))
        self.assertEqual(test_mode.webhook_url("DISCORD_WEBHOOK_URL", BRANCH), ("test", "DISCORD_TEST_WEBHOOK_URL"))

    def test_branch_without_test_secret_never_uses_real_channel(self):
        environ = {"GITHUB_REF_NAME": "v20", "DISCORD_WEBHOOK_URL": "real"}
        self.assertEqual(test_mode.webhook_url("DISCORD_WEBHOOK_URL", environ), ("", "DISCORD_TEST_WEBHOOK_URL"))

    def test_monthly_webhook_on_branch_is_test_channel(self):
        environ = dict(BRANCH, DISCORD_MONTHLY_WEBHOOK_URL="monthly")
        self.assertEqual(test_mode.webhook_url("DISCORD_MONTHLY_WEBHOOK_URL", environ)[0], "test")

    def test_local_run_is_not_a_test_run(self):
        self.assertFalse(test_mode.is_test_run({}))

    def test_banner_only_on_first_message_of_test_run(self):
        messages = test_mode.with_banner(["a", "b"], BRANCH)
        self.assertTrue(messages[0].startswith("🧪 **TEST** · gałąź `v20-kanal-testowy`"))
        self.assertTrue(messages[0].endswith("\na"))
        self.assertEqual(messages[1], "b")
        self.assertEqual(test_mode.with_banner(["a"], MAIN), ["a"])
        self.assertEqual(test_mode.with_banner([], BRANCH), [])


if __name__ == "__main__":
    unittest.main()
