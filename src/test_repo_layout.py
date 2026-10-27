"""Code must live in src/ (v34 completion, 27.10.2026).

The web upload puts files into the folder that is open at the moment. Three
times code files landed in the repository root instead of src/ (v22, v26,
and the second v34 package: the 14-day context never ran, because the
workflow runs src/main.py). This test fails the workflow when a Python file
is in the root, so such an upload cannot pass unnoticed.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class TestRepoLayout(unittest.TestCase):
    def test_no_python_files_in_the_repository_root(self):
        stray = sorted(path.name for path in ROOT.glob("*.py"))
        self.assertEqual(stray, [], "Pliki .py w katalogu głównym – przenieś je do src/: " + ", ".join(stray))

    def test_main_script_is_in_src(self):
        self.assertTrue((ROOT / "src" / "main.py").is_file())


if __name__ == "__main__":
    unittest.main()
